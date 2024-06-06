"""
Render service tests.
"""

from lute.parse.base import ParsedToken
from lute.read.render.service import find_all_Terms_in_string, get_paragraphs
from lute.db import db
from lute.models.term import Term

from tests.utils import add_terms, make_text, assert_rendered_text_equals
from tests.dbasserts import assert_sql_result


def _run_scenario(language, content, expected_found, msg=""):
    """
    Given some pre-saved terms in language,
    find_all method returns the expected_found terms that
    exist in the content string.
    """
    found_terms = find_all_Terms_in_string(content, language)
    assert len(found_terms) == len(expected_found), "found count, " + msg
    zws = "\u200B"  # zero-width space
    found_terms = [t.text.replace(zws, "") for t in found_terms]
    assert found_terms is not None, msg
    assert expected_found is not None, msg
    found_terms.sort()
    expected_found.sort()
    assert found_terms == expected_found, msg


def test_smoke_tests(english, app_context):
    "Check bounds, ensure no false matches, etc."
    add_terms(english, ["a", "at", "xyz"])

    _run_scenario(english, "attack cat", [], "no matches, not standalone")
    _run_scenario(english, "at", ["at"], "a doesn't match, not standalone")
    _run_scenario(english, "A", ["a"], "case ignored")
    _run_scenario(english, "AT A", ["a", "at"], "case, order ignored")
    _run_scenario(english, "aatt", [], "no match")
    _run_scenario(english, "Xyz", ["xyz"], "case ignored 2")
    _run_scenario(english, "XyZ", ["xyz"], "case ignored 3")
    _run_scenario(english, "      A     at    x", ["a", "at"], "spaces ignored")

    _run_scenario(english, "a dog here", ["a"], "bounds check, found at start")
    _run_scenario(english, "dog a here", ["a"], "bounds check, found at start")
    _run_scenario(english, "dog here a", ["a"], "bounds check, found at end")
    _run_scenario(english, "a a a a a a a", ["a"], "return once only")

    add_terms(english, ["ab xy"])
    _run_scenario(english, "ab xy", ["ab xy"], "with space")
    _run_scenario(english, "cab xy", [], "extra at start")
    _run_scenario(english, "cab xyq", [], "no match, not the same")
    _run_scenario(english, "ab xyq", [], "extra stuff at end")


def test_spanish_find_all_in_string(spanish, app_context):
    "Given various pre-saved terms, find_all returns those in the string."
    add_terms(spanish, ["perro", "gato", "un gato"])

    _run_scenario(spanish, "Hola tengo un gato", ["gato", "un gato"])
    _run_scenario(spanish, "gato gato gato", ["gato"])
    _run_scenario(spanish, "No tengo UN PERRO", ["perro"])
    _run_scenario(spanish, "Hola tengo un    gato", ["gato", "un gato"])
    _run_scenario(spanish, "No tengo nada", [])

    add_terms(spanish, ["échalo", "ábrela"])

    _run_scenario(spanish, '"Échalo", me dijo.', ["échalo"])
    _run_scenario(spanish, "gato ábrela Ábrela", ["gato", "ábrela"])


def test_english_find_all_in_string(english, app_context):
    "Can find a term with an apostrophe in string."
    add_terms(english, ["the cat's pyjamas"])

    _run_scenario(english, "This is the cat's pyjamas.", ["the cat's pyjamas"])


def test_turkish_find_all_in_string(turkish, app_context):
    "Finds terms, handling case conversion."
    add_terms(turkish, ["ışık", "için"])

    _run_scenario(turkish, "Işık İçin.", ["ışık", "için"])


def test_smoke_get_paragraphs(spanish, app_context):
    """
    Smoke test to get paragraph information.
    """
    add_terms(spanish, ["tengo un", "un gato"])
    perro = Term(spanish, "perro")
    perro.status = 0
    db.session.add(perro)

    content = "Tengo un gato. Hay un perro.\nTengo un perro."
    t = make_text("Hola", content, spanish)
    db.session.add(t)
    db.session.commit()

    sql = "select WoText from words order by WoText"
    assert_sql_result(sql, ["perro", "tengo/ /un", "un/ /gato"], "initial")

    ParsedToken.reset_counters()
    paras = get_paragraphs(t.text, t.book.language)
    assert len(paras) == 2

    def stringize(t):
        zws = chr(0x200B)
        parts = [
            f"[{t.display_text.replace(zws, '/')}(",
            f"{t.para_id}.{t.se_id}",
            ")]",
        ]
        return "".join(parts)

    sentences = [item for sublist in paras for item in sublist]
    actual = []
    for sent in sentences:
        actual.append("".join(map(stringize, sent.textitems)))

    expected = [
        "[Tengo/ /un(0.0)][ /gato(0.0)][. (0.0)]",
        "[Hay(0.1)][ (0.1)][un(0.1)][ (0.1)][perro(0.1)][.(0.1)]",
        "[Tengo/ /un(1.3)][ (1.3)][perro(1.3)][.(1.3)]",
    ]
    assert actual == expected

    assert_sql_result(sql, ["perro", "tengo/ /un", "un/ /gato"], "No new terms")


def test_smoke_rendered(spanish, app_context):
    """
    Smoke test to get paragraph information.
    """
    add_terms(spanish, ["tengo un", "un gato"])
    content = ["Tengo un gato. Hay un perro.", "Tengo un perro."]
    text = make_text("Hola", "\n".join(content), spanish)
    db.session.add(text)
    db.session.commit()

    expected = ["Tengo un(1)/ gato(1)/. /Hay/ /un/ /perro/.", "Tengo un(1)/ /perro/."]
    assert_rendered_text_equals(text, expected)


def test_rendered_leaves_blank_lines(spanish, app_context):
    """
    Smoke test to get paragraph information.
    """
    add_terms(spanish, ["tengo un", "un gato"])
    content = ["Tengo un gato. Hay un perro.", "", "Tengo un perro."]
    text = make_text("Hola", "\n".join(content), spanish)
    db.session.add(text)
    db.session.commit()

    expected = [
        "Tengo un(1)/ gato(1)/. /Hay/ /un/ /perro/.",
        "",
        "Tengo un(1)/ /perro/.",
    ]
    assert_rendered_text_equals(text, expected)
