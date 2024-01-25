"""
Text tests.
"""

from datetime import datetime
from lute.models.book import Book, Text


def transform_sentence(s):
    zws = chr(0x200B)  # zero-width space
    return s.text_content.replace(zws, "/")


def test_sentence_lifecycle(english):
    """
    Sentences must be generated when a Text is saved with the ReadDate saved.
    Sentences are only used for reference lookups.
    """
    b = Book("hola", english)
    t = Text(b, "Tienes un perro. Un gato.")

    assert len(t.sentences) == 0, "no sentences"

    t.read_date = datetime.now()
    assert len(t.sentences) == 2, "sentences are created when read_date is set"

    assert (
        transform_sentence(t.sentences[0]) == "/Tienes/ /un/ /perro/./"
    ), "1st sentence"
    assert transform_sentence(t.sentences[1]) == "/Un/ /gato/./", "2"

    t.text = "Tengo un coche."
    assert len(t.sentences) == 1, "changed"

    assert transform_sentence(t.sentences[0]) == "/Tengo/ /un/ /coche/./", "changed"
