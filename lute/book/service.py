"""
book helper routines.
"""

import os
from io import StringIO, TextIOWrapper
from datetime import datetime

from dataclasses import dataclass
from tempfile import TemporaryFile
import requests
from bs4 import BeautifulSoup
from flask import current_app, flash
from openepub import Epub, EpubError
from pypdf import PdfReader
from subtitle_parser import SrtParser, WebVttParser
from werkzeug.utils import secure_filename


class BookImportException(Exception):
    """
    Exception to throw on book import error.
    """

    def __init__(self, message="A custom error occurred", cause=None):
        self.cause = cause
        self.message = message
        super().__init__(message)


@dataclass
class BookDataFromUrl:
    "Data class"
    title: str = None
    source_uri: str = None
    text: str = None


class Service:
    "Service."

    def _secure_unique_fname(self, filename):
        """
        Return secure name pre-pended with datetime string.
        """
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
        f = "_".join([formatted_datetime, secure_filename(filename)])
        return f

    def save_audio_file(self, audio_file_field_data):
        """
        Save the file to disk, return its filename.
        """
        filename = self._secure_unique_fname(audio_file_field_data.filename)
        fp = os.path.join(current_app.env_config.useraudiopath, filename)
        audio_file_field_data.save(fp)
        return filename

    def get_file_content(self, filename, filestream):
        """
        Get the content of the file.
        """
        content = None
        _, ext = os.path.splitext(filename)
        ext = (ext or "").lower()
        if ext == ".txt":
            content = self.get_textfile_content(filename, filestream)
        if ext == ".epub":
            content = self.get_epub_content(filename, filestream)
        if ext == ".pdf":
            msg = """
            Note: pdf imports can be inaccurate, due to how PDFs are encoded.
            Please be aware of this while reading.
            """
            flash(msg, "notice")
            content = self.get_pdf_content(filename, filestream)
        if ext == ".srt":
            content = self.get_srt_content(filename, filestream)
        if ext == ".vtt":
            content = self.get_vtt_content(filename, filestream)

        if content is None:
            raise ValueError(f'Unknown file extension "{ext}"')
        if content.strip() == "":
            raise BookImportException(f"{filename} is empty.")
        return content

    def _get_text_stream_content(self, fstream, encoding="utf-8"):
        "Gets content from simple text stream."
        with TextIOWrapper(fstream, encoding=encoding) as decoded_stream:
            return decoded_stream.read()

    def get_textfile_content(self, filename, filestream):
        "Get content as a single string."
        try:
            return self._get_text_stream_content(filestream)
        except UnicodeDecodeError as e:
            f = filename
            msg = f"{f} is not utf-8 encoding, please convert it to utf-8 first (error: {str(e)})"
            raise BookImportException(message=msg, cause=e) from e

    def get_epub_content(self, filename, filestream):
        """
        Get the content of the epub as a single string.
        """
        content = ""
        try:
            if hasattr(filestream, "seekable"):
                epub = Epub(stream=filestream)
                content = epub.get_text()
            else:
                # We get a SpooledTemporaryFile from the form but this doesn't
                # implement all file-like methods until python 3.11. So we need
                # to rewrite it into a TemporaryFile
                with TemporaryFile() as tf:
                    filestream.seek(0)
                    tf.write(filestream.read())
                    epub = Epub(stream=tf)
                    content = epub.get_text()
        except EpubError as e:
            msg = f"Could not parse {filename} (error: {str(e)})"
            raise BookImportException(message=msg, cause=e) from e
        return content

    def get_pdf_content(self, filename, filestream):
        "Get content as a single string from a PDF file using PyPDF2."
        content = ""
        try:
            pdf_reader = PdfReader(filestream)
            for page in pdf_reader.pages:
                content += page.extract_text()
            return content
        except Exception as e:
            msg = f"Could not parse {filename} (error: {str(e)})"
            raise BookImportException(message=msg, cause=e) from e

    def get_srt_content(self, filename, filestream):
        """
        Get the content of the srt as a single string.
        """
        content = ""
        try:
            srt_content = self._get_text_stream_content(filestream, "utf-8-sig")
            parser = SrtParser(StringIO(srt_content))
            parser.parse()
            content = "\n".join(subtitle.text for subtitle in parser.subtitles)
            return content
        except Exception as e:
            msg = f"Could not parse {filename} (error: {str(e)})"
            raise BookImportException(message=msg, cause=e) from e

    def get_vtt_content(self, filename, filestream):
        """
        Get the content of the vtt as a single string.
        """
        content = ""
        try:
            vtt_content = self._get_text_stream_content(filestream, "utf-8-sig")
            # Check if it is from YouTube
            lines = vtt_content.split("\n")
            if lines[1].startswith("Kind:") and lines[2].startswith("Language:"):
                vtt_content = "\n".join(lines[:1] + lines[3:])
            parser = WebVttParser(StringIO(vtt_content))
            parser.parse()
            content = "\n".join(subtitle.text for subtitle in parser.subtitles)
            return content
        except Exception as e:
            msg = f"Could not parse {filename} (error: {str(e)})"
            raise BookImportException(message=msg, cause=e) from e

    def book_data_from_url(self, url):
        """
        Parse the url and load source data for a new Book.
        This returns a domain object, as the book is still unparsed.
        """
        s = None
        try:
            timeout = 20  # seconds
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            s = response.text
        except requests.exceptions.RequestException as e:
            msg = f"Could not parse {url} (error: {str(e)})"
            raise BookImportException(message=msg, cause=e) from e

        soup = BeautifulSoup(s, "html.parser")
        extracted_text = []

        # Add elements in order found.
        for element in soup.descendants:
            if element.name in ("h1", "h2", "h3", "h4", "p"):
                extracted_text.append(element.text)

        title_node = soup.find("title")
        orig_title = title_node.string if title_node else url

        short_title = orig_title[:150]
        if len(orig_title) > 150:
            short_title += " ..."

        b = BookDataFromUrl()
        b.title = short_title
        b.source_uri = url
        b.text = "\n\n".join(extracted_text)
        return b
