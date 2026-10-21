"""
Test main entry point.
"""

import os
import sqlite3
from contextlib import closing
import pytest

from lute.config.app_config import AppConfig
from lute.app_factory import create_app, data_initialization
from lute.db import db
from lute.models.book import Text
from lute.models.language import Language
from tests.utils import make_text


def test_init_no_existing_database(testconfig):
    """
    If no db exists, init should:
    - do the db setup
    - create the flask app
    """
    if os.path.exists(testconfig.dbfilename):
        os.unlink(testconfig.dbfilename)

    config_file = AppConfig.default_config_filename()
    app = create_app(config_file)

    assert os.path.exists(testconfig.dbfilename) is True, "db exists"
    assert testconfig.dbname.startswith("test_")

    def assert_tables_exist(msg: str):
        with closing(sqlite3.connect(testconfig.dbfilename)) as conn:
            cur = conn.cursor()
            sql = """SELECT name FROM sqlite_master
            WHERE type='table' AND name in ('words', 'languages')
            order by name;"""
            tnames = cur.execute(sql).fetchall()
            tnames = [t[0] for t in tnames]
            assert tnames == ["languages", "words"], msg

    assert_tables_exist("db set up correctly")

    client = app.test_client()
    response = client.get("/")
    assert b"Lute" in response.data


def _language_form_data(language):
    "Build language editor form data from saved settings."
    form = {
        field: getattr(language, field)
        for field in [
            "name",
            "parser_type",
            "character_substitutions",
            "regexp_split_sentences",
            "exceptions_split_sentences",
            "word_characters",
        ]
    }
    for i, dictionary in enumerate(language.dictionaries):
        for field in ["usefor", "dicttype", "dicturi", "sort_order"]:
            form[f"dictionaries-{i}-{field}"] = getattr(dictionary, field)
        if dictionary.is_active:
            form[f"dictionaries-{i}-is_active"] = "y"
    return form


@pytest.mark.parametrize(
    "setting,value",
    [
        ("word_characters", r"\p{Han}\p{Katakana}\p{Hiragana}"),
        ("exceptions_split_sentences", "("),
    ],
)
def test_startup_with_invalid_language_regex(spanish, english, setting, value):
    "Invalid settings must not prevent startup or access to the language editor."
    invalid_text = make_text("Invalid settings", "Hola amigo.", spanish)
    valid_text = make_text("Valid settings", "Hello my friend.", english)
    db.session.add_all([invalid_text, valid_text])
    db.session.commit()
    invalid_text.word_count = None
    valid_text.word_count = None
    original = getattr(spanish, setting)
    setattr(spanish, setting, value)
    db.session.commit()
    lang_id = spanish.id
    text_ids = invalid_text.id, valid_text.id

    # Follow the real startup sequence using the existing database.
    app = create_app(AppConfig.default_config_filename())
    messages = []
    with app.app_context():
        data_initialization(db.session, messages.append)
        language = db.session.get(Language, lang_id)
        assert getattr(language, setting) == value
        assert db.session.get(Text, text_ids[0]).word_count is None
        assert db.session.get(Text, text_ids[1]).word_count == 3

        assert "Spanish" in "\n".join(messages)
        assert "regular expression" in "\n".join(messages)
        assert "language settings" in "\n".join(messages)

        client = app.test_client()
        assert client.get("/", follow_redirects=True).status_code == 200
        edit_url = f"/language/edit/{lang_id}"
        assert client.get(edit_url).status_code == 200
        assert value.encode() in client.get(edit_url).data

        form = _language_form_data(language)
        form[setting] = original
        assert client.post(edit_url, data=form).status_code == 302

    # A later startup retries the missing count after the settings are repaired.
    app = create_app(AppConfig.default_config_filename())
    with app.app_context():
        data_initialization(db.session)
        assert db.session.get(Text, text_ids[0]).word_count == 2
        assert db.session.get(Text, text_ids[1]).word_count == 3
