"""
Read service tests.
"""

from lute.models.term import Term
from lute.parse.base import ParsedToken
from lute.read.service import find_all_Terms_in_string, get_paragraphs
from lute.db import db

from tests.utils import add_terms, make_text, assert_rendered_text_equals


def _run_scenario(language, content, expected_found):
    """
    Given some pre-saved terms in language,
    find_all method returns the expected_found terms that
    exist in the content string.
    """
    found_terms = find_all_Terms_in_string(content, language)
    assert len(found_terms) == len(expected_found), "found count"
    zws = "\u200B"  # zero-width space
    found_terms = [t.text.replace(zws, "") for t in found_terms]
    assert found_terms is not None
    assert expected_found is not None
    found_terms.sort()
    expected_found.sort()
    assert found_terms == expected_found


def test_spanish_find_all_in_string(spanish, app_context):
    "Given various pre-saved terms, find_all returns those in the string."
    terms = ["perro", "gato", "un gato"]
    for term in terms:
        t = Term(spanish, term)
        db.session.add(t)
    db.session.commit()

    _run_scenario(spanish, "Hola tengo un gato", ["gato", "un gato"])
    _run_scenario(spanish, "gato gato gato", ["gato"])
    _run_scenario(spanish, "No tengo UN PERRO", ["perro"])
    _run_scenario(spanish, "Hola tengo un    gato", ["gato", "un gato"])
    _run_scenario(spanish, "No tengo nada", [])

    terms = ["échalo", "ábrela"]
    for term in terms:
        t = Term(spanish, term)
        db.session.add(t)
    db.session.commit()

    _run_scenario(spanish, '"Échalo", me dijo.', ["échalo"])
    _run_scenario(spanish, "gato ábrela Ábrela", ["gato", "ábrela"])


def test_english_find_all_in_string(english, app_context):
    "Can find a term with an apostrophe in string."
    terms = ["the cat's pyjamas"]
    for term in terms:
        t = Term(english, term)
        db.session.add(t)
    db.session.commit()

    _run_scenario(english, "This is the cat's pyjamas.", ["the cat's pyjamas"])


def test_turkish_find_all_in_string(turkish, app_context):
    "Finds terms, handling case conversion."
    terms = ["ışık", "için"]
    for term in terms:
        t = Term(turkish, term)
        db.session.add(t)
    db.session.commit()

    content = "Işık İçin."
    _run_scenario(turkish, content, ["ışık", "için"])


def test_smoke_get_paragraphs(spanish, app_context):
    """
    Smoke test to get paragraph information.
    """
    add_terms(spanish, ["tengo un", "un gato"])

    content = "Tengo un gato. Hay un perro.\nTengo un perro."
    t = make_text("Hola", content, spanish)
    db.session.add(t)
    db.session.commit()

    ParsedToken.reset_counters()
    paras = get_paragraphs(t)
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
