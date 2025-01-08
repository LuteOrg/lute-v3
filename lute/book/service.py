"""
book helper routines.
"""

import os
from io import StringIO
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
from lute.models.book import Book as DBBook, Text as DBText


class BookImportException(Exception):
    """
    Exception to throw on book import error.
    """

    def __init__(self, message="A custom error occurred", cause=None):
        self.cause = cause
        self.message = message
        super().__init__(message)


class SentenceGroupIterator:
    """
    An iterator of ParsedTokens that groups them by sentence, up
    to a maximum number of tokens.
    """

    def __init__(self, tokens, maxcount=500):
        self.tokens = tokens
        self.maxcount = maxcount
        self.currpos = 0

    def count(self):
        """
        Get count of groups that will be returned.
        """
        old_currpos = self.currpos
        c = 0
        while self.next():
            c += 1
        self.currpos = old_currpos
        return c

    def next(self):
        """
        Get next sentence group.
        """
        if self.currpos >= len(self.tokens):
            return False

        curr_tok_count = 0
        last_eos = -1
        i = self.currpos

        while (curr_tok_count <= self.maxcount or last_eos == -1) and i < len(
            self.tokens
        ):
            tok = self.tokens[i]
            if tok.is_end_of_sentence == 1:
                last_eos = i
            if tok.is_word == 1:
                curr_tok_count += 1
            i += 1

        if curr_tok_count <= self.maxcount or last_eos == -1:
            ret = self.tokens[self.currpos : i]
            self.currpos = i + 1
        else:
            ret = self.tokens[self.currpos : last_eos + 1]
            self.currpos = last_eos + 1

        return ret


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

    def get_file_content(self, filefielddata):
        """
        Get the content of the file.
        """
        content = None
        _, ext = os.path.splitext(filefielddata.filename)
        ext = (ext or "").lower()
        if ext == ".txt":
            content = self.get_textfile_content(filefielddata)
        if ext == ".epub":
            content = self.get_epub_content(filefielddata)
        if ext == ".pdf":
            msg = """
            Note: pdf imports can be inaccurate, due to how PDFs are encoded.
            Please be aware of this while reading.
            """
            flash(msg, "notice")
            content = self.get_pdf_content_from_form(filefielddata)
        if ext == ".srt":
            content = self.get_srt_content(filefielddata)
        if ext == ".vtt":
            content = self.get_vtt_content(filefielddata)

        if content is None:
            raise ValueError(f'Unknown file extension "{ext}"')
        if content.strip() == "":
            raise BookImportException(f"{filefielddata.filename} is empty.")
        return content

    def get_textfile_content(self, filefielddata):
        "Get content as a single string."
        content = ""
        try:
            content = filefielddata.read()
            return str(content, "utf-8")
        except UnicodeDecodeError as e:
            f = filefielddata.filename
            msg = f"{f} is not utf-8 encoding, please convert it to utf-8 first (error: {str(e)})"
            raise BookImportException(message=msg, cause=e) from e

    def get_epub_content(self, epub_file_field_data):
        """
        Get the content of the epub as a single string.
        """
        content = ""
        try:
            if hasattr(epub_file_field_data.stream, "seekable"):
                epub = Epub(stream=epub_file_field_data.stream)
                content = epub.get_text()
            else:
                # We get a SpooledTemporaryFile from the form but this doesn't
                # implement all file-like methods until python 3.11. So we need
                # to rewrite it into a TemporaryFile
                with TemporaryFile() as tf:
                    epub_file_field_data.stream.seek(0)
                    tf.write(epub_file_field_data.stream.read())
                    epub = Epub(stream=tf)
                    content = epub.get_text()
        except EpubError as e:
            msg = f"Could not parse {epub_file_field_data.filename} (error: {str(e)})"
            raise BookImportException(message=msg, cause=e) from e
        return content

    def get_pdf_content_from_form(self, pdf_file_field_data):
        "Get content as a single string from a PDF file using PyPDF2."
        content = ""
        try:
            pdf_reader = PdfReader(pdf_file_field_data)

            for page in pdf_reader.pages:
                content += page.extract_text()

            return content
        except Exception as e:
            msg = f"Could not parse {pdf_file_field_data.filename} (error: {str(e)})"
            raise BookImportException(message=msg, cause=e) from e

    def get_srt_content(self, srt_file_field_data):
        """
        Get the content of the srt as a single string.
        """
        content = ""
        try:
            srt_content = srt_file_field_data.read().decode("utf-8-sig")

            parser = SrtParser(StringIO(srt_content))
            parser.parse()

            content = "\n".join(subtitle.text for subtitle in parser.subtitles)

            return content
        except Exception as e:
            msg = f"Could not parse {srt_file_field_data.filename} (error: {str(e)})"
            raise BookImportException(message=msg, cause=e) from e

    def get_vtt_content(self, vtt_file_field_data):
        """
        Get the content of the vtt as a single string.
        """
        content = ""
        try:
            vtt_content = vtt_file_field_data.read().decode("utf-8-sig")

            # Check if it is from YouTube
            lines = vtt_content.split("\n")
            if lines[1].startswith("Kind:") and lines[2].startswith("Language:"):
                vtt_content = "\n".join(lines[:1] + lines[3:])

            parser = WebVttParser(StringIO(vtt_content))
            parser.parse()

            content = "\n".join(subtitle.text for subtitle in parser.subtitles)

            return content
        except Exception as e:
            msg = f"Could not parse {vtt_file_field_data.filename} (error: {str(e)})"
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

    def split_text_at_page_breaks(self, txt):
        "Break fulltext manually at lines consisting of '---' only."
        # Tried doing this with a regex without success.
        segments = []
        current_segment = ""
        for line in txt.split("\n"):
            if line.strip() == "---":
                segments.append(current_segment.strip())
                current_segment = ""
            else:
                current_segment += line + "\n"
        if current_segment:
            segments.append(current_segment.strip())
        return segments

    def split_by_sentences(self, language, fulltext, max_word_tokens_per_text=250):
        "Split fulltext into pages, respecting sentences."

        pages = []
        for segment in self.split_text_at_page_breaks(fulltext):
            tokens = language.parser.get_parsed_tokens(segment, language)
            it = SentenceGroupIterator(tokens, max_word_tokens_per_text)
            while toks := it.next():
                s = (
                    "".join([t.token for t in toks])
                    .replace("\r", "")
                    .replace("¶", "\n")
                    .strip()
                )
                pages.append(s)
        pages = [p for p in pages if p.strip() != ""]

        return pages

    def create_book(self, title, language, fulltext, max_word_tokens_per_text=250):
        """
        Create a book with given fulltext content,
        splitting the content into separate Text objects with max
        token count.
        """
        pages = self.split_by_sentences(language, fulltext, max_word_tokens_per_text)
        b = DBBook(title, language)
        for index, page in enumerate(pages):
            _ = DBText(b, page, index + 1)
        return b
