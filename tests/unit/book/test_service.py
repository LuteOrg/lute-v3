"""
Book service tests.
"""

import os
from contextlib import ExitStack
from lute.db import db
from lute.models.repositories import BookRepository
from lute.book.model import Book
from lute.book.service import Service


def get_test_files():
    "Return test files pair."
    thisdir = os.path.dirname(os.path.realpath(__file__))
    sample_files = os.path.join(thisdir, "..", "..", "acceptance", "sample_files")
    text_path = os.path.join(sample_files, "hola.txt")
    mp3_path = os.path.join(sample_files, "fake.mp3")
    with open(text_path, "r", encoding="utf-8") as fp:
        assert fp.read().strip() == "Tengo un amigo.", "Sanity check only."
    with open(mp3_path, "r", encoding="utf-8") as fp:
        assert fp.read().strip() == "fake mp3 file", "Sanity check only."
    return (text_path, mp3_path)


def test_create_book_from_file_paths(app, app_context, spanish):
    "Create a book using the DTO, to be populated by the form."
    text_path, mp3_path = get_test_files()

    b = Book()
    b.title = "Hola"
    b.language_id = spanish.id
    b.text_source_path = text_path
    b.audio_source_path = mp3_path

    svc = Service()
    svc.import_book(b, db.session)

    repo = BookRepository(db.session)
    book = repo.find_by_title("Hola", spanish.id)
    assert book.title == "Hola", "title"
    assert book.texts[0].text == "Tengo un amigo.", "Got content"

    assert book.audio_filename is not None, "Have audio file"
    assert book.audio_filename.endswith("mp3"), "still an mp3"
    useraudiopath = app.env_config.useraudiopath
    full_audio_path = os.path.join(useraudiopath, book.audio_filename)
    assert os.path.exists(full_audio_path), "file saved"

    with open(full_audio_path, "r", encoding="utf-8") as fp:
        assert fp.read().strip() == "fake mp3 file", "correct content copied."


def test_create_book_from_streams(app, app_context, spanish):
    "Create a book using streams, as given by the form."
    text_path, mp3_path = get_test_files()

    b = Book()
    b.title = "Hola"
    b.language_id = spanish.id
    with ExitStack() as stack:
        b.text_stream = stack.enter_context(open(text_path, mode="rb"))
        b.text_stream_filename = "blah.txt"
        b.audio_stream = stack.enter_context(open(mp3_path, mode="rb"))
        b.audio_stream_filename = "blah.mp3"
        svc = Service()
        svc.import_book(b, db.session)

    repo = BookRepository(db.session)
    book = repo.find_by_title("Hola", spanish.id)
    assert book.title == "Hola", "title"
    assert book.texts[0].text == "Tengo un amigo.", "Got content"

    assert book.audio_filename is not None, "Have audio file"
    assert book.audio_filename.endswith("mp3"), "still an mp3"
    useraudiopath = app.env_config.useraudiopath
    full_audio_path = os.path.join(useraudiopath, book.audio_filename)
    assert os.path.exists(full_audio_path), "file saved"
    with open(full_audio_path, "r", encoding="utf-8") as fp:
        assert fp.read().strip() == "fake mp3 file", "correct content copied."
