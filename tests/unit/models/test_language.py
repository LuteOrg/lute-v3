"""
Language model tests - getting, saving, etc.

Low value but ensure that the db mapping is correct.
"""

import pytest
import os

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


def test_save_new_language_smoke_test(_empty_db):
    """
    Validating model save only.
    """
    sql = "select LgName, LgRightToLeft from languages"
    assert_sql_result(sql, [], 'empty table')

    lang = Language()
    lang.name = 'abc'
    lang.dict_1_uri = 'something'

    db.session.add(lang)
    db.session.commit()

    assert_sql_result(sql, ['abc; 0'], 'have language')

    lang.right_to_left = True

    db.session.add(lang)
    db.session.commit()
    assert_sql_result(sql, ['abc; 1'], 'rtl is True')


@pytest.fixture
def yaml_test_file():
    test_file_path = "../../../demo/languages/english.yaml"
    absolute_path = os.path.abspath(os.path.join(os.path.dirname(__file__), test_file_path))
    return absolute_path


def test_new_language_from_yaml_file(yaml_test_file):
    """
    Can load a new language from yaml definition.
    """
    lang = Language.fromYaml(yaml_test_file)

    # Replace the following assertions with your specific expectations
    assert lang.lgName == "Some Name"
    assert lang.lgDict1URI == "Dict1 URI"
    assert lang.lgDict2URI == "Dict2 URI"
    # Add more assertions for other attributes as needed
