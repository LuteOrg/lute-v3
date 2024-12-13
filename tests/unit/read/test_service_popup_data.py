"""
Term popup data tests.
"""

import pytest
from lute.models.term import Term, TermTag, Status
from lute.read.service import Service
from lute.db import db


@pytest.fixture(name="service")
def fixture_svc(app_context):
    "Service"
    return Service(db.session)


def test_popup_data_is_none_if_no_data(spanish, app_context, service):
    "Return None if no popup."
    t = Term(spanish, "gato")
    db.session.add(t)
    db.session.commit()

    d = service.get_popup_data(t.id)
    assert d is None, "No data, no popup"

    t.translation = "hello"
    d = service.get_popup_data(t.id)
    assert d is not None, "Have data, popup"


def test_popup_data_shown_if_have_tag(spanish, app_context, service):
    "Return None if no popup."
    t = Term(spanish, "gato")
    t.add_term_tag(TermTag("animal"))
    db.session.add(t)
    db.session.commit()
    d = service.get_popup_data(t.id)
    assert d is not None, "Have tag, show popup"
    assert d["term_tags"] == ["animal"]


def test_popup_shown_if_parent_exists_even_if_no_other_data(
    spanish, app_context, service
):
    "I always want to know if a parent has been set."
    t = Term(spanish, "gato")
    db.session.add(t)
    db.session.commit()
    d = service.get_popup_data(t.id)
    assert d is None, "No data, no popup"

    p = Term(spanish, "perro")
    t.parents.append(p)
    db.session.add(t)
    db.session.commit()
    d = service.get_popup_data(t.id)
    assert d is not None, "Has parent, popup, even if no other data."


def test_popup_data_is_shown_if_have_data_regardless_of_status(
    spanish, app_context, service
):
    "Return None if no-popup statuses."
    t = Term(spanish, "gato")
    t.translation = "hello"
    for s in [1, Status.UNKNOWN, Status.IGNORED]:
        t.status = s
        db.session.add(t)
        db.session.commit()
        d = service.get_popup_data(t.id)
        assert d is not None, f"Have data for status {s}"


def test_term_with_no_parents(spanish, app_context, service):
    "Keep the lights on test, smoke only."
    t = Term(spanish, "gato")
    t.translation = "cat"
    db.session.add(t)
    db.session.commit()

    d = service.get_popup_data(t.id)
    assert d["parentdata"] == [], "no parents"
    assert d["parentterms"] == "", "no parents"


def test_single_parent_data_not_added_if_same_translation(
    spanish, app_context, service
):
    "Extra data added for display."
    t = Term(spanish, "gato")
    t.translation = "cat"
    p = Term(spanish, "perro")
    p.translation = "cat"
    t.parents.append(p)
    db.session.add(t)
    db.session.commit()

    d = service.get_popup_data(t.id)
    assert d["parentdata"] == [], "no extra parent data"
    assert d["parentterms"] == "perro", "one parent"


def test_parent_data_added_if_parent_translation_is_different(
    spanish, app_context, service
):
    "Extra data added for display."
    t = Term(spanish, "gato")
    t.translation = "cat"
    p = Term(spanish, "perro")
    p.translation = "kitty"
    t.parents.append(p)
    db.session.add(t)
    db.session.commit()

    d = service.get_popup_data(t.id)
    expected_p_data = {
        "term": "perro",
        "roman": None,
        "trans": "kitty",
        "tags": [],
    }
    assert d["parentdata"] == [expected_p_data], "extra parent data added"
    assert d["parentterms"] == "perro", "one parent"


def test_parent_data_always_added_if_multiple_parents(spanish, app_context, service):
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

    d = service.get_popup_data(t.id)
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


def test_single_term_not_included_in_own_components(spanish, app_context, service):
    "Keep the lights on test, smoke only."
    t = Term(spanish, "gato")
    t.translation = "cat"
    db.session.add(t)
    db.session.commit()

    d = service.get_popup_data(t.id)
    assert d["components"] == [], "no components"


def test_component_without_translation_not_returned(spanish, app_context, service):
    "Component word is returned."
    t = Term(spanish, "un gato")
    t.translation = "a cat"
    db.session.add(t)
    make_terms([("gato", "")], spanish)
    db.session.commit()

    d = service.get_popup_data(t.id)
    assert d["components"] == [], "no data"


def test_component_word_with_translation_returned(spanish, app_context, service):
    "Component word is returned."
    t = Term(spanish, "un gato")
    t.translation = "a cat"
    db.session.add(t)
    make_terms([("gato", "cat")], spanish)
    db.session.commit()

    d = service.get_popup_data(t.id)
    assert_components(d, ["gato; cat"], "one component")


def test_nested_multiword_components(spanish, app_context, service):
    "Complete components are returned."
    t = Term(spanish, "un gato gordo")
    t.translation = "a fat cat"
    db.session.add(t)
    make_terms([("gato", "cat"), ("gat", "x"), ("un gato", "a cat")], spanish)
    db.session.commit()

    d = service.get_popup_data(t.id)
    assert_components(d, ["un gato; a cat", "gato; cat"], "components")


def test_multiword_components_returned_in_order_of_appearance(
    spanish, app_context, service
):
    "Complete components are returned."
    t = Term(spanish, "un gato gordo")
    t.translation = "a fat cat"
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

    d = service.get_popup_data(t.id)
    assert_components(
        d, ["un gato; a cat", "gato gordo; fat", "gato; cat"], "components"
    )


def test_components_only_returned_once(spanish, app_context, service):
    "Component not returned multiple times if present multiple times."
    t = Term(spanish, "un gato gordo gato")
    t.translation = "a cat fat cat"
    db.session.add(t)
    make_terms([("gato", "cat")], spanish)
    db.session.commit()

    d = service.get_popup_data(t.id)
    assert_components(d, ["gato; cat"], "components")
