"""
Creating, updating languages.
"""

import pytest


@pytest.fixture(name="dummy_lang")
def fixture_dummy_lang():
    """
    A full set of language data to be posted.
    """
    return {
        "name": "updated_name",
        "dict_1_uri": "a",
        "dict_2_uri": "b",
        "sentence_translate_uri": "c",
        "show_romanization": True,
        "right_to_left": False,

        "parser_type": "turkish",
        "character_substitutions": "",

        "regexp_split_sentences": "",
        "exceptions_split_sentences": "",
        "word_characters": "a-z",
    }


def test_edit_language(client, dummy_lang):
    "Edit one of the demo languages."
    response = client.post(
        "language/edit/1",
        data=dummy_lang,
        follow_redirects=True
    )

    assert response.status_code == 200
    print(response.data)
    assert b'Language index' in response.data, "title content"
    assert b'updated_name' in response.data, "name content"


def test_new_language(client, dummy_lang):
    "Post a new language returns to the index."
    response = client.post(
        "language/new",
        data=dummy_lang,
        follow_redirects=True
    )

    assert response.status_code == 200
    print(response.data)
    assert b'Language index' in response.data, "title content"
    assert b'updated_name' in response.data, "name content"
