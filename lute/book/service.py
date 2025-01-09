"""
book helper routines.
"""

import os
import shutil
from io import StringIO, TextIOWrapper, BytesIO
from datetime import datetime
import uuid
from dataclasses import dataclass
from tempfile import TemporaryFile
import requests
from bs4 import BeautifulSoup
from flask import current_app, flash
from openepub import Epub, EpubError
from pypdf import PdfReader
from subtitle_parser import SrtParser, WebVttParser
from lute.book.model import Repository


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


class FileTextExtraction:
    "Utility to extract text from various file formats."

    def get_file_content(self, filename, filestream):
        """
        Get the content of the file.
        """
        _, ext = os.path.splitext(filename)
        ext = (ext or "").lower()

        messages = {
            ".pdf": """
            Note: pdf imports can be inaccurate, due to how PDFs are encoded.
            Please be aware of this while reading.
            """
        }
        msg = messages.get(ext)
        if msg is not None:
            flash(msg, "notice")

        handlers = {
            ".txt": self._get_textfile_content,
            ".epub": self._get_epub_content,
            ".pdf": self._get_pdf_content,
            ".srt": self._get_srt_content,
            ".vtt": self._get_vtt_content,
        }
        handler = handlers.get(ext)
        if handler is None:
            raise ValueError(f'Unknown file extension "{ext}"')
        content = handler(filename, filestream).strip()
        if content == "":
            raise BookImportException(f"{filename} is empty.")
        return content

    def _get_text_stream_content(self, fstream, encoding="utf-8"):
        "Gets content from simple text stream."

        usestream = fstream
        # May have to convert the fstream to a a BytesIO stream.
        # GitHub CI caught this, and per ChatGPT: In Python 3.10,
        # SpooledTemporaryFile no longer automatically gains all
        # file-like methods when rolled over to a regular temporary
        # file. Specifically, it seems that the object lacks the
        # readable method required by TextIOWrapper to validate the
        # stream ...
        #
        # I haven't looked into this deeply, but when running Python
        # 3.10.16 on my mac, "inv accept -k bad_text_files" failed on
        # line "with TextIOWrapper(fstream, encoding=encoding) as
        # decoded:" with "AttributeError: 'SpooledTemporaryFile'
        # object has no attribute 'readable'. Did you mean:
        # 'readline'?"..  Converting usestream to BytesIO fixed it.
        if not hasattr(fstream, "readable"):
            usestream = BytesIO(fstream.read())  # Wrap in BytesIO if needed
        with TextIOWrapper(usestream, encoding=encoding) as decoded:
            return decoded.read()

    def _get_textfile_content(self, filename, filestream):
        "Get content as a single string."
        try:
            return self._get_text_stream_content(filestream)
        except UnicodeDecodeError as e:
            f = filename
            msg = f"{f} is not utf-8 encoding, please convert it to utf-8 first (error: {str(e)})"
            raise BookImportException(message=msg, cause=e) from e

    def _get_epub_content(self, filename, filestream):
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

    def _get_pdf_content(self, filename, filestream):
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

    def _get_srt_content(self, filename, filestream):
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

    def _get_vtt_content(self, filename, filestream):
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


class Service:
    "Service."

    def _unique_fname(self, filename):
        """
        Return secure name pre-pended with datetime string.
        """
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
        _, ext = os.path.splitext(filename)
        ext = (ext or "").lower()
        newfilename = uuid.uuid4().hex
        return f"{formatted_datetime}_{newfilename}{ext}"

    def save_audio_file(self, audio_file_field_data):
        """
        Save the file to disk, return its filename.
        """
        filename = self._unique_fname(audio_file_field_data.filename)
        fp = os.path.join(current_app.env_config.useraudiopath, filename)
        audio_file_field_data.save(fp)
        return filename

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

    def import_book(self, book, session):
        """
        Save the book as a dbbook, parsing and saving files as needed.
        Returns new book created.
        """

        def _raise_if_file_missing(p, fldname):
            if not os.path.exists(p):
                raise BookImportException(f"Missing file {p} given in {fldname}")

        def _raise_if_none(p, fldname):
            if p is None:
                raise BookImportException(f"Must set {fldname}")

        fte = FileTextExtraction()
        if book.text_source_path:
            _raise_if_file_missing(book.text_source_path, "text_source_path")
            tsp = book.text_source_path
            with open(tsp, mode="rb") as stream:
                book.text = fte.get_file_content(tsp, stream)

        if book.text_stream:
            _raise_if_none(book.text_stream_filename, "text_stream_filename")
            book.text = fte.get_file_content(
                book.text_stream_filename, book.text_stream
            )

        if book.audio_source_path:
            _raise_if_file_missing(book.audio_source_path, "audio_source_path")
            newname = self._unique_fname(book.audio_source_path)
            fp = os.path.join(current_app.env_config.useraudiopath, newname)
            shutil.copy(book.audio_source_path, fp)
            book.audio_filename = newname

        if book.audio_stream:
            _raise_if_none(book.audio_stream_filename, "audio_stream_filename")
            newname = self._unique_fname(book.audio_stream_filename)
            fp = os.path.join(current_app.env_config.useraudiopath, newname)
            with open(fp, mode="wb") as fcopy:  # Use "wb" to write in binary mode
                while chunk := book.audio_stream.read(
                    8192
                ):  # Read the stream in chunks (e.g., 8 KB)
                    fcopy.write(chunk)
            book.audio_filename = newname

        repo = Repository(session)
        dbbook = repo.add(book)
        repo.commit()
        return dbbook
