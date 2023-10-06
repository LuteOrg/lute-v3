"""
Language model tests - getting, saving, etc.

Low value but ensure that the db mapping is correct.
"""

import os
import pytest

from lute.models.language import Language
from lute.db import db
from tests.dbasserts import assert_sql_result


def test_demo_has_preloaded_languages(_demo_db):
    """
    When users get the initial demo, it has English, French, etc,
    pre-defined.
    """
    sql = """
    select LgName
    from languages
    where LgName in ('English', 'French')
    order by LgName
    """
    assert_sql_result(sql, [ 'English', 'French' ], 'sanity check loaded')


def test_new_language_has_sane_defaults():
    """
    Only validates the call to __init__.  Sqlalchemy mappings aren't used during the constuctor.
    """
    lang = Language()
    assert lang.character_substitutions == "´='|`='|’='|‘='|...=…|..=‥"
    assert lang.regexp_split_sentences == '.!?'
    assert lang.exceptions_split_sentences == 'Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.'
    assert lang.word_characters == 'a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ'
    assert lang.remove_spaces is False
    assert lang.split_each_char is False
    assert lang.right_to_left is False
    assert lang.show_romanization is False
    assert lang.parser_type == 'spacedel'


def test_save_new_language_smoke_test(_empty_db):
    """
    Validating model save.
    When a new language is created and saved,
    the defaults are saved in the db.
    """
    sql = "select LgName, LgRightToLeft, LgRegexpSplitSentences from languages"
    assert_sql_result(sql, [], 'empty table')

    lang = Language()
    lang.name = 'abc'
    lang.dict_1_uri = 'something'

    db.session.add(lang)
    db.session.commit()

    assert_sql_result(sql, ['abc; 0; .!?'], 'have language, default saved')

    lang.right_to_left = True

    db.session.add(lang)
    db.session.commit()
    assert_sql_result(sql, ['abc; 1; .!?'], 'rtl is True')


@pytest.fixture(name="yaml_folder")
def fixture_yaml_folder():
    "Path to the demo files."
    lang_path = "../../../demo/languages/"
    absolute_path = os.path.abspath(os.path.join(os.path.dirname(__file__), lang_path))
    return absolute_path


def test_new_english_from_yaml_file(yaml_folder):
    """
    Smoke test, can load a new language from yaml definition.
    """
    f = os.path.join(yaml_folder, 'english.yaml')
    lang = Language.from_yaml(f)

    # Replace the following assertions with your specific expectations
    assert lang.name == "English"
    assert lang.dict_1_uri == "https://en.thefreedictionary.com/###"
    assert lang.sentence_translate_uri == "*https://www.deepl.com/translator#en/en/###"
    assert lang.show_romanization is False, 'uses default'
    assert lang.right_to_left is False, 'uses default'


def test_get_predefined():
    """
    Returns all the languages using the files in the demo folder.
    """
    langs = Language.get_predefined()
    langnames = [lang.name for lang in langs]
    for expected in [ 'English', 'French', 'Turkish' ]:
        assert expected in langnames, expected
