"""
Term Repository tests.

Tests lute.term.model.Term *domain* objects being saved
and retrieved from DB.
"""

from datetime import datetime
import pytest

from lute.db import db
from lute.term.model import Term, Repository, ReferencesRepository
from tests.dbasserts import assert_record_count_equals
from tests.utils import add_terms, make_text


@pytest.fixture(name="repo")
def fixture_repo():
    return Repository(db.session)


@pytest.fixture(name="refsrepo")
def fixture_refs_repo():
    return ReferencesRepository(db.session)


## Sentences


def full_refs_to_string(refs):
    "Convert refs to strings for simpler testing."

    def to_string(r):
        return f"{r.title}, {r.sentence}"

    def refs_to_string(refs_array):
        ret = [to_string(r) for r in refs_array]
        ret.sort()
        return ret

    def parent_refs_to_string(prefs):
        ret = []
        for p in prefs:
            ret.append({"term": p["term"], "refs": refs_to_string(p["refs"])})
        return ret

    return {
        "term": refs_to_string(refs["term"]),
        "children": refs_to_string(refs["children"]),
        "parents": parent_refs_to_string(refs["parents"]),
    }


@pytest.mark.sentences
def test_get_all_references(spanish, repo, refsrepo):
    "Check references with parents and children."
    text = make_text(
        "hola", "Tengo un gato.  Ella tiene un perro.  No quiero tener nada.", spanish
    )
    archtext = make_text("luego", "Tengo un coche.", spanish)
    archtext.book.archived = True
    db.session.add(archtext.book)

    for t in [text, archtext]:
        t.read_date = datetime.now()
        db.session.add(t)

    db.session.commit()

    tengo = Term()
    tengo.language_id = spanish.id
    tengo.text = "tengo"
    tengo.parents = ["tener"]
    repo.add(tengo)

    tiene = Term()
    tiene.language_id = spanish.id
    tiene.text = "tiene"
    tiene.parents = ["tener"]
    repo.add(tiene)

    repo.commit()

    refs = refsrepo.find_references(tengo)
    assert full_refs_to_string(refs) == {
        "term": [
            "hola (1/1), <b>Tengo</b> un gato.",
            "luego (1/1), <b>Tengo</b> un coche.",
        ],
        "children": [],
        "parents": [
            {
                "term": "tener",
                "refs": [
                    "hola (1/1), Ella <b>tiene</b> un perro.",
                    "hola (1/1), No quiero <b>tener</b> nada.",
                ],
            }
        ],
    }, "term tengo"

    tener = repo.find(spanish.id, "tener")
    refs = refsrepo.find_references(tener)
    assert full_refs_to_string(refs) == {
        "term": ["hola (1/1), No quiero <b>tener</b> nada."],
        "children": [
            "hola (1/1), <b>Tengo</b> un gato.",
            "hola (1/1), Ella <b>tiene</b> un perro.",
            "luego (1/1), <b>Tengo</b> un coche.",
        ],
        "parents": [],
    }, "term tener"


@pytest.mark.sentences
def test_multiword_reference(spanish, repo, refsrepo):
    "Ensure zws-delimiters are respected."
    text = make_text("hola", "Yo tengo un gato.", spanish)
    text.read_date = datetime.now()
    db.session.add(text)
    db.session.commit()

    t = Term()
    t.language_id = spanish.id
    t.text = "TENGO UN"
    repo.add(t)
    repo.commit()

    refs = refsrepo.find_references(t)
    assert full_refs_to_string(refs) == {
        "term": ["hola (1/1), Yo <b>tengo un</b> gato."],
        "children": [],
        "parents": [],
    }, "term tengo"


@pytest.mark.sentences
def test_get_references_only_includes_read_texts(spanish, repo, refsrepo):
    "Like it says above."
    text = make_text("hola", "Tengo un gato.  No tengo un perro.", spanish)

    tengo = Term()
    tengo.language_id = spanish.id
    tengo.text = "tengo"
    repo.add(tengo)
    repo.commit()

    refs = refsrepo.find_references(tengo)
    keys = refs.keys()
    for k in keys:
        assert len(refs[k]) == 0, f"{k}, no matches for unread texts"

    text.read_date = datetime.now()
    db.session.add(text)
    db.session.commit()

    refs = refsrepo.find_references(tengo)
    assert len(refs["term"]) == 2, "have refs once text is read"


def _make_read_text(title, body, lang):
    "Make a text, mark it read."
    text = make_text(title, body, lang)
    text.read_date = datetime.now()
    db.session.add(text)
    db.session.commit()
    return text


@pytest.mark.sentences
def test_issue_531_spanish_ref_search_case_insens_normal(spanish, refsrepo):
    "Spanish was finding 'normal' upper/lower chars that sqlite could handle."
    _make_read_text("hola", "TENGO.  tengo.", spanish)
    t = add_terms(spanish, ["tengo"])[0]

    refs = refsrepo.find_references(t)
    assert len(refs["term"]) == 2, "both found"


@pytest.mark.sentences
def test_issue_531_spanish_ref_search_case_insens_accented(spanish, refsrepo):
    "Spanish wasn't finding different case of accented chars."
    _make_read_text("hola", "Ábrelo.  ábrelo.", spanish)
    t = add_terms(spanish, ["ábrelo"])[0]
    refs = refsrepo.find_references(t)
    assert len(refs["term"]) == 2, "both found"


@pytest.mark.sentences
def test_issue_531_turkish_ref_search_is_case_insensitive(turkish, refsrepo):
    "Turkish upper/lower case letters are quite different!."
    _make_read_text("Test", "ışık. Işık", turkish)
    t = add_terms(turkish, ["ışık"])[0]
    refs = refsrepo.find_references(t)
    assert len(refs["term"]) == 2, "both found"


@pytest.mark.sentences
def test_get_references_only_includes_refs_in_same_language(
    spanish, english, repo, refsrepo
):
    "Like it says above."
    text1 = make_text("hola", "Tengo un gato.  No tengo un perro.", spanish)
    text2 = make_text("hola", "Tengo in english.", english)

    tengo = Term()
    tengo.language_id = spanish.id
    tengo.text = "tengo"
    repo.add(tengo)
    repo.commit()

    text1.read_date = datetime.now()
    text2.read_date = datetime.now()
    db.session.add(text1)
    db.session.add(text2)
    db.session.commit()

    refs = refsrepo.find_references(tengo)
    assert len(refs["term"]) == 2, "only have 2 refs (spanish)"
    sentences = [r.sentence for r in refs["term"]]
    expected = [
        "<b>Tengo</b> un gato.",
        "No <b>tengo</b> un perro.",
    ]
    assert sentences == expected


@pytest.mark.sentences
def test_get_references_new_term(spanish, refsrepo):
    "Check references with parents and children."
    text = make_text("hola", "Tengo un gato.", spanish)
    text.read_date = datetime.now()
    db.session.add(text)

    tengo = Term()
    tengo.language_id = spanish.id
    tengo.text = "tengo"

    refs = refsrepo.find_references(tengo)
    assert full_refs_to_string(refs) == {
        "term": ["hola (1/1), <b>Tengo</b> un gato."],
        "children": [],
        "parents": [],
    }, "term tengo"


@pytest.mark.sentences
def test_can_get_references_by_term_id_including_unread(spanish):
    "Like it says above."
    text = make_text("hola", "Tengo un gato.  No tengo un perro.", spanish)
    text.load_sentences()
    db.session.add(text)
    db.session.commit()
    # pylint: disable=unbalanced-tuple-unpacking
    [tengo] = add_terms(spanish, ["tengo"])

    assert_record_count_equals("select * from sentences", 2, "sanity check")

    refsrepo = ReferencesRepository(db.session, limit=1, include_unread=False)
    refs = refsrepo.find_references_by_id(tengo.id)
    sentences = [r.sentence for r in refs["term"]]
    expected = []
    assert sentences == expected, "not including unread texts"

    refsrepo = ReferencesRepository(db.session, limit=1, include_unread=True)
    refs = refsrepo.find_references_by_id(tengo.id)
    sentences = [r.sentence for r in refs["term"]]
    expected = ["<b>Tengo</b> un gato."]
    assert sentences == expected, "including unread"
