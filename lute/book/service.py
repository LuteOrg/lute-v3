"""
book helper routines.
"""

import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from flask import current_app, flash
from werkzeug.utils import secure_filename
from lute.book.model import Book


def _secure_unique_fname(filename):
    """
    Return secure name pre-pended with datetime string.
    """
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
    f = "_".join([formatted_datetime, secure_filename(filename)])
    return f


def save_audio_file(audio_file_field_data):
    """
    Save the file to disk, return its filename.
    """
    filename = _secure_unique_fname(audio_file_field_data.filename)
    fp = os.path.join(current_app.env_config.useraudiopath, filename)
    audio_file_field_data.save(fp)
    return filename


def get_epub_content(epub_file_field_data):
    """
    Get the content of the epub as a single string.
    """
    raise ValueError("TODO epub: to be implemented.")


def book_from_url(url):
    "Parse the url and load a new Book."
    s = None
    try:
        timeout = 20  # seconds
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        s = response.text
    except requests.exceptions.RequestException as e:
        msg = f"Could not parse {url} (error: {str(e)})"
        flash(msg, "notice")
        return Book()

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

    b = Book()
    b.title = short_title
    b.source_uri = url
    b.text = "\n\n".join(extracted_text)
    return b
