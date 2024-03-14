"""
Term popup data tests.
"""

from lute.models.term import Term
from lute.read.service import get_popup_data
from lute.db import db


def test_term_with_no_parents(spanish, app_context):
    "Keep the lights on test, smoke only."
    t = Term(spanish, "gato")
    db.session.add(t)
    db.session.commit()

    d = get_popup_data(t.id)
    assert d["parentdata"] == [], "no parents"
    assert d["parentterms"] == "", "no parents"


def test_single_parent_data_not_added_if_same_translation(spanish, app_context):
    "Extra data added for display."
    t = Term(spanish, "gato")
    t.translation = "cat"
    p = Term(spanish, "perro")
    p.translation = "cat"
    t.parents.append(p)
    db.session.add(t)
    db.session.commit()

    d = get_popup_data(t.id)
    assert d["parentdata"] == [], "no extra parent data"
    assert d["parentterms"] == "perro", "one parent"


def test_parent_data_added_if_parent_translation_is_different(spanish, app_context):
    "Extra data added for display."
    t = Term(spanish, "gato")
    t.translation = "cat"
    p = Term(spanish, "perro")
    p.translation = "kitty"
    t.parents.append(p)
    db.session.add(t)
    db.session.commit()

    d = get_popup_data(t.id)
    expected_p_data = {
        "term": "perro",
        "roman": None,
        "trans": "kitty",
        "tags": [],
    }
    assert d["parentdata"] == [expected_p_data], "extra parent data added"
    assert d["parentterms"] == "perro", "one parent"


def test_parent_data_always_added_if_multiple_parents(spanish, app_context):
    "Extra data added for display."
    t = Term(spanish, "gato")
    t.translation = "cat"
    p = Term(spanish, "perro")
    p.translation = "kitty"
    p2 = Term(spanish, "hombre")
    p2.translation = "kitteh"
    t.parents.append(p)
    t.parents.append(p2)
    db.session.add(t)
    db.session.commit()

    d = get_popup_data(t.id)
    expected_p1_data = {"term": "perro", "roman": None, "trans": "kitty", "tags": []}
    expected_p2_data = {"term": "hombre", "roman": None, "trans": "kitteh", "tags": []}
    expected = [expected_p1_data, expected_p2_data]
    assert d["parentdata"] == expected, "extra parent data added"
    assert d["parentterms"] == "perro, hombre", "parents"


# TODO tests:
# two words single component match
# multiword with other multiword components


def test_single_term_not_included_in_own_components(spanish, app_context):
    "Keep the lights on test, smoke only."
    t = Term(spanish, "gato")
    db.session.add(t)
    db.session.commit()

    d = get_popup_data(t.id)
    assert d["components"] == [], "no components"
