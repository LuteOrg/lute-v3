"""
Term parent map file generation tests.
"""

import os
import tempfile
import pytest
from lute.term_parent_map.service import export_unknown_terms
from tests.utils import add_terms, make_book


@pytest.fixture(name="output_tempfile")
def fixture_temp_file():
    "Yield a temp file."
    with tempfile.NamedTemporaryFile() as t:
        f = t.name
    yield f
    os.unlink(f)


@pytest.fixture(name="_book")
def fixture_terms_and_book(spanish):
    "Create a book."
    spanish_terms = ["gato", "lista", "tiene una", "listo"]
    add_terms(spanish, spanish_terms)
    content = "Hola tengo un gato.  No tengo una lista.\nElla tiene una bebida."
    book = make_book("Hola", content, spanish)
    yield book


def assert_file_content(fname, expected):
    "Assert file name fname contains expected."
    expected.sort()
    with open(fname, "r", encoding="utf-8") as f:
        actual = f.read().splitlines()
        actual.sort()
        assert expected == actual, "contents"


def test_smoke_book_file_created(app_context, _book, output_tempfile):
    "Smoke test only."
    export_unknown_terms(_book, output_tempfile)
    expected = ["hola", "tengo", "un", "no", "una", "ella", "tiene", "bebida"]
    assert_file_content(output_tempfile, expected)
