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


## Component term checks.


def make_terms(term_trans_pairs, spanish):
    "Make test data"
    for c in term_trans_pairs:
        ct = Term(spanish, c[0])
        ct.translation = c[1]
        db.session.add(ct)


def assert_components(d, expected, msg=""):
    "Check components."

    def _c_to_string(c):
        s = "; ".join([c["term"], c["trans"]])
        zws = chr(0x200B)
        return s.replace(zws, "")

    actual = [_c_to_string(c) for c in d["components"]]
    assert actual == expected, msg


def test_single_term_not_included_in_own_components(spanish, app_context):
    "Keep the lights on test, smoke only."
    t = Term(spanish, "gato")
    db.session.add(t)
    db.session.commit()

    d = get_popup_data(t.id)
    assert d["components"] == [], "no components"


def test_component_without_translation_not_returned(spanish, app_context):
    "Component word is returned."
    t = Term(spanish, "un gato")
    db.session.add(t)
    make_terms([("gato", "")], spanish)
    db.session.commit()

    d = get_popup_data(t.id)
    assert d["components"] == [], "no data"


def test_component_word_with_translation_returned(spanish, app_context):
    "Component word is returned."
    t = Term(spanish, "un gato")
    db.session.add(t)
    make_terms([("gato", "cat")], spanish)
    db.session.commit()

    d = get_popup_data(t.id)
    assert_components(d, ["gato; cat"], "one component")


def test_nested_multiword_components(spanish, app_context):
    "Complete components are returned."
    t = Term(spanish, "un gato gordo")
    db.session.add(t)
    make_terms([("gato", "cat"), ("gat", "x"), ("un gato", "a cat")], spanish)
    db.session.commit()

    d = get_popup_data(t.id)
    assert_components(d, ["un gato; a cat", "gato; cat"], "components")


def test_multiword_components_returned_in_order_of_appearance(spanish, app_context):
    "Complete components are returned."
    t = Term(spanish, "un gato gordo")
    db.session.add(t)
    make_terms(
        [
            ("gato", "cat"),
            ("gat", "x"),
            ("gato gordo", "fat"),
            ("un gato", "a cat"),
        ],
        spanish,
    )
    db.session.commit()

    d = get_popup_data(t.id)
    assert_components(
        d, ["un gato; a cat", "gato gordo; fat", "gato; cat"], "components"
    )


def test_components_only_returned_once(spanish, app_context):
    "Component not returned multiple times if present multiple times."
    t = Term(spanish, "un gato gordo gato")
    db.session.add(t)
    make_terms([("gato", "cat")], spanish)
    db.session.commit()

    d = get_popup_data(t.id)
    assert_components(d, ["gato; cat"], "components")
