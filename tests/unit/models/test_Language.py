"""
Language model tests - getting, saving, etc.

Low value but ensure that the db mapping is correct.
"""

from lute.db import db
from lute.db.demo import Service as DemoService
from lute.models.language import Language
from lute.models.repositories import LanguageRepository
from tests.dbasserts import assert_sql_result


def test_demo_has_preloaded_languages(app_context):
    """
    When users get the initial demo, it has English, French, etc,
    pre-defined.
    """
    demosvc = DemoService(db.session)
    demosvc.load_demo_data()
    sql = """
    select LgName
    from languages
    where LgName in ('English', 'French')
    order by LgName
    """
    assert_sql_result(sql, ["English", "French"], "sanity check loaded")


def test_new_language_has_sane_defaults():
    """
    Only validates the call to __init__.  Sqlalchemy mappings aren't used during the constuctor.
    """
    lang = Language()
    assert lang.character_substitutions == "´='|`='|’='|‘='|...=…|..=‥"
    assert lang.regexp_split_sentences == ".!?"
    assert lang.exceptions_split_sentences == "Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds."
    assert lang.word_characters == "a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ"
    assert lang.right_to_left is False
    assert lang.show_romanization is False
    assert lang.parser_type == "spacedel"


def test_can_find_lang_by_name(app_context):
    """
    Returns lang if found, or None
    """
    lang = Language()
    lang.name = "English"
    db.session.add(lang)
    db.session.commit()
    repo = LanguageRepository(db.session)
    e = repo.find_by_name("English")
    assert e.name == "English", "case match"

    e_lc = repo.find_by_name("english")
    assert e_lc.name == "English", "case-insensitive"

    nf = repo.find_by_name("notfound")
    assert nf is None, "not found"


def test_language_word_char_regex_returns_python_compatible_regex(app_context):
    """
    Old Lute v2 ran in php, so the language word chars regex
    could look like this:

    x{0600}-x{06FF}x{FE70}-x{FEFC}  (where x = backslash-x)

    This needs to be converted to the python equivalent, e.g.

    u0600-u06FFuFE70-uFEFC  (where u = backslash-u)
    """
    demosvc = DemoService(db.session)
    demosvc.load_demo_data()
    repo = LanguageRepository(db.session)
    a = repo.find_by_name("Arabic")
    # pylint: disable=line-too-long
    assert (
        a.word_characters
        == r"\u0600-\u0608\u060B\u060E-\u061A\u061C\u0620-\u0669\u066E-\u06D3\u06D5-\u06FF\uFE70-\uFEFC"
    )


def test_lang_to_dict_from_dict_returns_same_thing(app_context):
    """
    Lang can be exported to yaml and imported from yaml.
    A dictionary is used as the intermediary form, so the
    same language should return the same data.
    """
    demosvc = DemoService(db.session)
    demosvc.load_demo_data()
    repo = LanguageRepository(db.session)
    e = repo.find_by_name("English")
    e_dict = e.to_dict()
    e_from_dict = Language.from_dict(e_dict)
    e_back_to_dict = e_from_dict.to_dict()
    assert e_dict == e_back_to_dict, "Same thing returned"
