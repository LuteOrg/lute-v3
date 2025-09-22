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
from lute.book.model import Repository, Book
from lute.tts.service import TTSService


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
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()
            s = response.text
        except requests.exceptions.Timeout:
            msg = f"Could not parse {url} - Request timed out after {timeout} seconds"
            raise BookImportException(message=msg)
        except requests.exceptions.ConnectionError:
            msg = f"Could not parse {url} - Connection error. Please check the URL and your internet connection."
            raise BookImportException(message=msg)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 404:
                msg = f"Could not parse {url} - Page not found (404)"
            elif status_code == 403:
                msg = f"Could not parse {url} - Access denied (403). The website may be blocking automated requests."
            elif status_code >= 500:
                msg = f"Could not parse {url} - Server error ({status_code}). Please try again later."
            else:
                msg = f"Could not parse {url} - HTTP error {status_code}"
            raise BookImportException(message=msg)
        except requests.exceptions.RequestException as e:
            msg = f"Could not parse {url} - Network error: {str(e)}"
            raise BookImportException(message=msg)
        except Exception as e:
            msg = f"Could not parse {url} - Unexpected error: {str(e)}"
            raise BookImportException(message=msg)

        if not s or not s.strip():
            msg = f"Could not parse {url} - No content found at URL"
            raise BookImportException(message=msg)

        soup = BeautifulSoup(s, "html.parser")
        
        # Check if we have a valid HTML document
        if not soup.find():
            msg = f"Could not parse {url} - Invalid or empty HTML document"
            raise BookImportException(message=msg)

        extracted_text = []

        # Add elements in order found.
        for element in soup.descendants:
            if element.name in ("h1", "h2", "h3", "h4", "p"):
                text = element.get_text(strip=True)
                if text:  # Only add non-empty text
                    extracted_text.append(text)

        # If no text was extracted, try to get body text as fallback
        if not extracted_text:
            body = soup.find('body')
            if body:
                text = body.get_text(strip=True)
                if text:
                    extracted_text.append(text[:500])  # Limit to first 500 chars to avoid huge texts

        title_node = soup.find("title")
        orig_title = title_node.get_text(strip=True) if title_node else url

        # If we still don't have a title, try to get it from the URL
        if not orig_title or orig_title == url:
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                orig_title = parsed_url.netloc + parsed_url.path
                # Clean up the title
                orig_title = orig_title.strip('/').replace('/', ' - ')
            except:
                orig_title = url

        short_title = orig_title[:150]
        if len(orig_title) > 150:
            short_title += " ..."

        b = BookDataFromUrl()
        b.title = short_title
        b.source_uri = url
        b.text = "\n\n".join(extracted_text) if extracted_text else "No text could be extracted from the webpage."
        
        # If we have no meaningful content, raise an exception
        if not extracted_text and "No text could be extracted" in b.text:
            msg = f"Could not parse {url} - No readable content found on the webpage"
            raise BookImportException(message=msg)
            
        return b

    def import_book(self, book, session, progress_callback=None):
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

        # Use provided progress callback or look for one attached to the book
        actual_progress_callback = progress_callback or getattr(book, '_tts_progress_callback', None)
        
        # Report progress
        if actual_progress_callback:
            actual_progress_callback(10, "Processing book content...")

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

        # Add TTS generation here
        tts_service = TTSService()
        print("Pasé por aquí - Starting TTS generation")
        
        # Check if we should generate TTS (from form data or default behavior)
        should_generate_tts = getattr(book, 'generate_tts', True)
        
        # Debug information
        print(f"should_generate_tts: {should_generate_tts}")
        print(f"book.text exists: {bool(book.text)}")
        print(f"book.text length: {len(book.text) if book.text else 0}")
        print(f"book.audio_filename: {book.audio_filename}")
        print(f"book.audio_stream: {book.audio_stream}")
        print(f"book.audio_source_path: {book.audio_source_path}")
        print(f"book.language_name: {book.language_name}")
        print(f"book.language_id: {book.language_id}")
        
        if should_generate_tts and book.text and not book.audio_filename and not book.audio_stream and not book.audio_source_path:
            try:
                print("Entering TTS generation block")
                # Report progress
                if actual_progress_callback:
                    actual_progress_callback(30, "Preparing TTS generation...")
                    
                # Get the language code for TTS
                # First check if language_name is directly available
                if book.language_name:
                    lang_code = tts_service.get_language_code(book.language_name)
                    print(f"Using language_name: {book.language_name}, lang_code: {lang_code}")
                # If not, try to get it from language_id
                elif book.language_id:
                    # We need to get the language name from the database
                    from lute.models.repositories import LanguageRepository
                    lang_repo = LanguageRepository(session)
                    lang = lang_repo.find(book.language_id)
                    if lang:
                        lang_code = tts_service.get_language_code(lang.name)
                        print(f"Using language_id: {book.language_id}, language name: {lang.name}, lang_code: {lang_code}")
                    else:
                        lang_code = 'en'  # Default to English
                        print(f"Language not found for id {book.language_id}, defaulting to English")
                else:
                    lang_code = 'en'  # Default to English
                    print("No language specified, defaulting to English")
                
                print(f"Final lang_code: {lang_code}")
                print(f"Book title: {book.title}")
                print(f"Text preview: {book.text[:100] if book.text else 'No text'}")
                
                # Generate audio from the book text with progress tracking
                if actual_progress_callback:
                    # Use a wrapper to ensure we don't override the original callback
                    def tts_progress_wrapper(percent, message):
                        # Scale TTS progress from 30-90% to 30-90% of overall progress
                        scaled_percent = 30 + (percent * 0.6) if percent >= 0 else percent
                        actual_progress_callback(scaled_percent, message)
                    
                    print("Calling TTS service with progress callback")
                    audio_filename = tts_service.generate_audio(book.text, lang_code, book.title, tts_progress_wrapper)
                else:
                    print("Calling TTS service without progress callback")
                    audio_filename = tts_service.generate_audio(book.text, lang_code, book.title)
                book.audio_filename = audio_filename
                print(f"TTS generation successful, audio_filename: {audio_filename}")
            except Exception as e:
                # If TTS fails, we don't want to stop the book import
                error_msg = f"Warning: Failed to generate TTS audio: {str(e)}"
                print(error_msg)
                import traceback
                traceback.print_exc()
                # Flash a warning to the user
                try:
                    from flask import flash
                    flash(error_msg, "notice")
                except:
                    # If we can't flash, just print to console
                    pass
        else:
            print("Skipping TTS generation due to conditions not met")
            if not should_generate_tts:
                print("  - TTS generation disabled")
            if not book.text:
                print("  - No book text available")
            if book.audio_filename or book.audio_stream or book.audio_source_path:
                print("  - Audio already exists")

        # Report progress
        if actual_progress_callback:
            actual_progress_callback(90, "Processing audio files...")

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
        
        # Report completion
        if actual_progress_callback:
            actual_progress_callback(100, "Book import complete!")
            
        return dbbook

    def create_book(self, form_data, files_data, session, progress_callback=None):
        """
        Create a new book from form data and files.
        
        Args:
            form_data (dict): Form data containing book information
            files_data (dict): Files data containing text/audio files
            session: Database session
            progress_callback (function): Optional callback function to report progress
            
        Returns:
            Book: The created book object
        """
        from werkzeug.datastructures import FileStorage
        import tempfile
        import os
        
        # Report start of process
        if progress_callback:
            progress_callback(0, "Initializing book creation...")
        
        # Create a new book instance
        book = Book()
        
        # Set basic book properties from form data
        book.title = form_data.get('title', '')
        book.language_id = int(form_data.get('language_id', 0))
        book.source_uri = form_data.get('source_uri', '')
        
        # Handle text content
        if 'textfile' in files_data and files_data['textfile']:
            # Handle file upload
            file_info = files_data['textfile']
            if isinstance(file_info, dict) and 'content' in file_info:
                # For async processing where content is stored in dict
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    tmp_file.write(file_info['content'])
                    book.text_source_path = tmp_file.name
                    book.text_stream_filename = file_info.get('filename', 'upload.txt')
            elif isinstance(file_info, FileStorage):
                # For direct file upload
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    file_info.save(tmp_file.name)
                    book.text_source_path = tmp_file.name
                    book.text_stream_filename = file_info.filename
        elif 'text' in form_data:
            # Handle direct text input
            book.text = form_data['text']
            
        # Handle audio content
        if 'audiofile' in files_data and files_data['audiofile']:
            file_info = files_data['audiofile']
            if isinstance(file_info, dict) and 'content' in file_info:
                # For async processing where content is stored in dict
                # Create a dummy FileStorage object to pass to save_audio_file
                from werkzeug.datastructures import FileStorage
                from io import BytesIO
                dummy_file = FileStorage(
                    stream=BytesIO(file_info['content']),
                    filename=file_info.get('filename', 'upload.mp3'),
                    content_type='application/octet-stream'
                )
                book.audio_filename = self.save_audio_file(dummy_file)
            elif isinstance(file_info, FileStorage):
                # For direct file upload
                book.audio_filename = self.save_audio_file(file_info)
        
        # Handle TTS generation flag
        book.generate_tts = bool(form_data.get('generate_tts'))
        
        try:
            created_book = self.import_book(book, session, progress_callback)
                
            # Report completion
            if progress_callback:
                progress_callback(100, "Book creation complete!")
                
            # Clean up temporary files if they were created
            if hasattr(book, 'text_source_path') and book.text_source_path:
                try:
                    os.unlink(book.text_source_path)
                except:
                    pass
            if hasattr(book, 'audio_source_path') and book.audio_source_path:
                try:
                    os.unlink(book.audio_source_path)
                except:
                    pass
            return created_book
        except Exception as e:
            # Clean up temporary files if they were created
            if hasattr(book, 'text_source_path') and book.text_source_path:
                try:
                    os.unlink(book.text_source_path)
                except:
                    pass
            if hasattr(book, 'audio_source_path') and book.audio_source_path:
                try:
                    os.unlink(book.audio_source_path)
                except:
                    pass
            raise e
