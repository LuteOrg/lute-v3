"""
Term Repository tests.

Tests lute.term.model.Term *domain* objects being saved
and retrieved from DB.
"""

from datetime import datetime
import pytest

from lute.models.term import Term as DBTerm, TermTag
from lute.db import db
from lute.term.model import Term, Repository
from tests.dbasserts import assert_sql_result, assert_record_count_equals
from tests.utils import add_terms, make_text


@pytest.fixture(name="repo")
def fixture_repo():
    return Repository(db)


@pytest.fixture(name="hello_term")
def fixture_hello_term(english):
    """
    Term business object with some defaults,
    no tags or parents.
    """
    t = Term()
    t.language_id = english.id
    t.text = "HELLO"
    t.translation = "greeting"
    t.current_image = "hello.png"
    t.flash_message = "hello flash"
    return t


def test_save_new(app_context, hello_term, repo):
    """
    Saving a simple Term object loads the database.
    """
    sql = "select WoText, WoTextLC, WoTokenCount from words"
    assert_sql_result(sql, [], "empty table")

    repo.add(hello_term)
    assert_sql_result(sql, [], "Still empty")

    repo.commit()
    assert_sql_result(sql, ["HELLO; hello; 1"], "Saved")

    term = repo.find(hello_term.language_id, hello_term.text)
    assert term.text == hello_term.text


def test_save_new_multiword(app_context, hello_term, repo):
    """
    Zero-width strings are added between parsed tokens.
    """
    sql = "select WoText, WoTextLC, WoTokenCount from words"
    assert_sql_result(sql, [], "empty table")

    hello_term.text = "HELLO THERE"
    repo.add(hello_term)
    assert_sql_result(sql, [], "Still empty")

    repo.commit()
    # Assert replaces zws with '/'
    assert_sql_result(sql, ["HELLO/ /THERE; hello/ /there; 3"], "Saved")


def test_save_updates_existing(english, app_context, hello_term, repo):
    """
    Saving Term updates an existing term if the text and lang
    matches.
    """

    term = DBTerm(english, "HELLO")
    db.session.add(term)
    db.session.commit()
    sql = "select WoID, WoText, WoStatus from words"
    assert_sql_result(sql, [f"{term.id}; HELLO; 1"], "have term")

    hello_term.language_id = english.id
    hello_term.text = "hello"
    hello_term.status = 5

    repo.add(hello_term)
    repo.commit()
    assert_sql_result(sql, [f"{term.id}; hello; 5"], "have term, status changed")


def test_save_existing_replaces_tags(english, app_context, repo):
    """
    If the db has a term with tags, and the business term changes
    those, the existing tags are replaced.
    """
    dbterm = DBTerm(english, "HELLO")
    dbterm.add_term_tag(TermTag("a"))
    dbterm.add_term_tag(TermTag("b"))
    db.session.add(dbterm)
    db.session.commit()
    sql = f"""select TgText from tags
    inner join wordtags on WtTgID = TgID
    where WtWoID = {dbterm.id}"""
    assert_sql_result(sql, ["a", "b"], "have term tags")

    term = repo.load(dbterm.id)
    assert term.term_tags == ["a", "b"]

    term.term_tags = ["a", "c"]
    repo.add(term)
    repo.commit()
    assert_sql_result(sql, ["a", "c"], "term tags changed")

    term.term_tags = []
    repo.add(term)
    repo.commit()
    assert_sql_result(sql, [], "term tags removed")

    sql = "select TgText from tags order by TgText"
    assert_sql_result(sql, ["a", "b", "c"], "Source tags still exist")


def test_save_uses_existing_TermTags(app_context, repo, hello_term):
    "Don't create new TermTag records if they already exist."
    db.session.add(TermTag("a"))
    db.session.commit()

    sql = """select TgID, TgText, WoText
    from tags
    left join wordtags on WtTgID = TgID
    left join words on WoID = WtWoID
    order by TgText"""
    assert_sql_result(sql, ["1; a; None"], "a tag exists")

    hello_term.term_tags = ["a", "b"]
    repo.add(hello_term)
    repo.commit()
    assert_sql_result(sql, ["1; a; HELLO", "2; b; HELLO"], "a used, b created")


def test_save_with_no_flash_message(app_context, repo, hello_term):
    "Saving with flash = None removes the flash record."
    hello_term.flash_message = "hi there"
    repo.add(hello_term)
    repo.commit()
    sql = "select WfMessage from wordflashmessages"
    assert_sql_result(sql, ["hi there"], "record exists")

    hello_term.flash_message = None
    repo.add(hello_term)
    repo.commit()
    assert_sql_result(sql, [], "removed")


## Deletes.


def test_delete(app_context, repo, hello_term):
    "Removes record from db."
    repo.add(hello_term)
    repo.commit()
    sql = "select WoTextLC, WoStatus from words"
    assert_sql_result(sql, ["hello; 1"], "record exists")

    repo.delete(hello_term)
    repo.commit()
    assert_sql_result(sql, [], "deleted")


def test_delete_leaves_parent(app_context, repo, hello_term):
    "Parent is left."
    hello_term.parents.append("parent")
    repo.add(hello_term)
    repo.commit()
    sql = "select WoTextLC from words"
    assert_sql_result(sql, ["hello", "parent"], "records exists")

    repo.delete(hello_term)
    repo.commit()
    assert_sql_result(sql, ["parent"], "parent stays")


## Saving and images.


def test_save_term_image_saved_and_replaced(app_context, repo, hello_term):
    "Saving puts record in image table."
    sql = "select WiSource from wordimages"
    assert_sql_result(sql, [], "nothing present")
    repo.add(hello_term)
    repo.commit()
    assert_sql_result(sql, ["hello.png"], "image saved")


def test_save_term_image_set_to_blank_removes_record(app_context, repo, hello_term):
    "Saving puts record in image table."
    sql = "select WiSource from wordimages"
    repo.add(hello_term)
    repo.commit()
    assert_sql_result(sql, ["hello.png"], "image saved")

    hello_term.current_image = ""
    repo.add(hello_term)
    repo.commit()
    assert_sql_result(sql, [], "record removed")

    hello_term.current_image = "new.png"
    repo.add(hello_term)
    repo.commit()
    assert_sql_result(sql, ["new.png"], "image saved")

    hello_term.current_image = None
    repo.add(hello_term)
    repo.commit()
    assert_sql_result(sql, [], "record removed again")


## Saving and parents.


def test_save_with_new_parent(app_context, repo, hello_term):
    """
    Given a Term with parents = [ 'newparent' ],
    new parent DBTerm is created, and is assigned translation and image and tag.
    """
    hello_term.parents = ["parent"]
    hello_term.term_tags = ["a", "b"]
    repo.add(hello_term)
    repo.commit()
    assert_sql_result("select WoText from words", ["HELLO", "parent"], "parent created")

    parent = repo.find(hello_term.language_id, "parent")
    assert isinstance(parent, Term), "is a Term bus. object"
    assert parent.text == "parent"
    assert parent.term_tags == hello_term.term_tags
    assert parent.term_tags == ["a", "b"]  # just spelling it out.
    assert parent.translation == hello_term.translation
    assert parent.current_image == hello_term.current_image
    assert parent.parents == []


def test_save_with_existing_but_unknown_parent(app_context, repo, english, hello_term):
    "Existing parent with status 0 is bumped to status 1."
    p = DBTerm(english, "parent")
    p.status = 0
    db.session.add(p)
    db.session.commit()

    hello_term.parents = ["parent"]
    hello_term.term_tags = ["a", "b"]
    repo.add(hello_term)
    repo.commit()

    sql = "select WoText, WoStatus from words order by WoText"
    assert_sql_result(sql, ["HELLO; 1", "parent; 1"], "parent status set to 1")


def test_save_remove_parent_breaks_link(app_context, repo, hello_term):
    "Parent is left."
    hello_term.parents.append("parent")
    repo.add(hello_term)
    repo.commit()
    sql = "select WoTextLC from words"
    assert_sql_result(sql, ["hello", "parent"], "records exists")
    assert_record_count_equals("wordparents", 1, "linked")

    hello_term.parents.remove("parent")
    repo.add(hello_term)
    repo.commit()
    assert_sql_result(sql, ["hello", "parent"], "both stay")
    assert_record_count_equals("wordparents", 0, "link broken")


def test_save_change_parent_breaks_old_link(app_context, repo, hello_term):
    "Parent is left."
    hello_term.parents.append("parent")
    repo.add(hello_term)
    repo.commit()
    sql = "select WoTextLC from words order by WoTextLC"
    assert_sql_result(sql, ["hello", "parent"], "records exists")

    sqlparent = """
    select c.WoTextLC, p.WoTextLC
    from wordparents
    inner join words as c on WpWoID = c.WoID
    inner join words as p on WpParentWoID = p.WoID
    """
    assert_sql_result(sqlparent, ["hello; parent"], "records exists")

    hello_term.parents.remove("parent")
    hello_term.parents.append("new")
    repo.add(hello_term)
    repo.commit()
    assert_sql_result(sql, ["hello", "new", "parent"], "all stay")
    assert_sql_result(sqlparent, ["hello; new"], "changed")


def test_save_term_with_multiple_parents_unsets_sync_status(
    app_context, repo, hello_term
):
    "Ensure DB data is good on save."
    hello_term.parents.append("parent")
    hello_term.sync_status = True
    repo.add(hello_term)
    repo.commit()

    sql = "select WoTextLC, WoSyncStatus from words where WoTextLC = 'hello'"
    assert_sql_result(sql, ["hello; 1"], "link set")

    hello_term.parents.append("parent2")
    hello_term.sync_status = True
    repo.add(hello_term)
    repo.commit()
    assert_sql_result(sql, ["hello; 0"], "link UN-set")


def test_cant_set_term_as_its_own_parent(app_context, repo, hello_term):
    """
    Would create obvious circular ref
    """
    hello_term.parents = [hello_term.text]
    repo.add(hello_term)
    repo.commit()
    assert_sql_result("select WoText from words", ["HELLO"], "term entered")
    assert_sql_result("select * from wordparents", [], "no records")


@pytest.fixture(name="_existing_parent")
def fixture_existing_parent(app_context, english):
    "Create an existing parent."
    term = DBTerm(english, "parent")
    db.session.add(term)
    db.session.commit()
    return term


def test_save_with_existing_parent_creates_link(
    app_context, repo, hello_term, _existing_parent
):
    """
    new parent link is created, and is assigned translation and image and tag.
    """

    sql = "select WoID, WoText from words"
    assert_sql_result(sql, ["1; parent"], "initial state")

    hello_term.parents = ["parent"]
    hello_term.term_tags = ["a", "b"]
    dbterm = repo.add(hello_term)
    repo.commit()

    assert_sql_result(sql, ["1; parent", "2; HELLO"], "new record added")
    assert len(dbterm.parents) == 1
    assert dbterm.parents[0].text == "parent"


def test_save_existing_parent_gets_translation_if_missing(
    app_context, repo, hello_term, _existing_parent
):
    """
    Translation and image applied if missing.
    """

    sql = "select WoID, WoText, WoTranslation from words"
    assert_sql_result(sql, ["1; parent; None"], "initial state")

    hello_term.parents = ["parent"]
    hello_term.term_tags = ["a", "b"]
    repo.add(hello_term)
    repo.commit()

    assert_sql_result(
        sql, ["1; parent; greeting", "2; HELLO; greeting"], "transl saved"
    )


## Find tests.


def test_load(empty_db, english, repo):
    "Smoke test."
    t = DBTerm(english, "Hello")
    t.set_current_image("hello.png")
    t.add_term_tag(TermTag("a"))
    t.add_term_tag(TermTag("b"))
    db.session.add(t)
    db.session.commit()
    assert t.id is not None, "ID assigned"

    term = repo.load(t.id)
    assert term.id == t.id
    assert term.language.id == t.language.id, "lang object set"
    assert term.language_id == english.id
    assert term.text == "Hello"
    assert term.original_text == "Hello"
    assert term.current_image == "hello.png"
    assert len(term.parents) == 0
    assert term.term_tags == ["a", "b"]


def test_load_throws_if_bad_id(app_context, repo):
    "If app says term id = 7 exists, and it doesn't, that's a problem."
    with pytest.raises(ValueError):
        repo.load(9876)


def test_find_is_found(spanish, app_context, repo):
    "Find by text finds regardless of case."
    add_terms(spanish, ["PARENT"])
    cases = ["PARENT", "parent", "pAReNt"]
    for c in cases:
        p = repo.find(spanish.id, c)
        assert p is not None, f"parent found for case {c}"
        assert p.text == "PARENT", f"parent found for case {c}"


def test_find_not_found_returns_none(spanish, repo):
    "No match = none."
    p = repo.find(spanish.id, "unknown_term")
    assert p is None, "nothing found"


def test_find_only_looks_in_specified_language(spanish, english, repo):
    "Only search language."
    add_terms(english, ["hola"])
    p = repo.find(spanish.id, "hola")
    assert p is None, "english terms not checked"


def test_find_existing_multi_word(spanish, repo):
    """
    Domain objects DO have zero-width strings in them.

    This is necessary to disambiguate terms such as
    "集めれ" and "集め/れ", both of which are valid
    parser results (though perhaps not *useful* parser
    results, but that's a different question).
    """
    add_terms(spanish, ["una bebida"])
    zws = "\u200B"
    term_with_zws = f"una{zws} {zws}bebida"
    t = repo.find(spanish.id, term_with_zws)
    assert t.id > 0
    assert t.text == term_with_zws

    t = repo.find(spanish.id, "una bebida")
    assert t.id > 0
    assert t.text == term_with_zws


## Find or new tests.


def test_find_or_new_existing_word(spanish, repo):
    "Existing term is found."
    add_terms(spanish, ["BEBIDA"])
    t = repo.find_or_new(spanish.id, "bebida")
    assert t.id > 0, "exists"
    assert t.text == "BEBIDA"
    assert t.language.id == spanish.id, "lang object set"


def test_find_or_new_non_existing(spanish, repo):
    "Returns new term."
    t = repo.find_or_new(spanish.id, "TENGO")
    assert t.id is None
    assert t.text == "TENGO"
    assert t.language.id == spanish.id, "lang object set"


def test_find_or_new_existing_multi_word(spanish, repo):
    "Spaces etc handled correctly."
    add_terms(spanish, ["una bebida"])
    zws = "\u200B"
    term_with_zws = f"una{zws} {zws}bebida"
    t = repo.find_or_new(spanish.id, f"una{zws} {zws}bebida")
    assert t.id > 0
    assert t.text == term_with_zws

    t = repo.find_or_new(spanish.id, "una bebida")
    assert t.id > 0
    assert t.text == term_with_zws


def test_find_or_new_new_multi_word(spanish, repo):
    "ZWS added correctly."
    zws = "\u200B"
    t = repo.find_or_new(spanish.id, f"una{zws} {zws}bebida")
    assert t.id is None
    assert t.text == f"una{zws} {zws}bebida"

    t = repo.find_or_new(spanish.id, "una bebida")
    assert t.id is None
    assert t.text == f"una{zws} {zws}bebida"


def test_find_or_new_ambiguous_japanese_terms(japanese, repo):
    """
    Characterization test only: behaviour of find_or_new for
    ambiguously parsable 集めれ terms

    See comments in find_or_new for notes.
    """
    s = "集めれ"
    term = DBTerm.create_term_no_parsing(japanese, s)
    db.session.add(term)
    db.session.commit()

    t = repo.find_or_new(japanese.id, s)
    assert t.id is None, "do _not_ have term, searching for string without context"
    zws = "\u200B"
    assert t.text == f"集め{zws}れ", "returns a new term"


## Matches tests.


@pytest.fixture(name="_multiple_terms")
def fixture_multiple(english, spanish, app_context):
    "Create multiple terms for find_matches tests."
    add_terms(english, ["parent"])
    add_terms(spanish, ["parent", "pare", "gato", "tengo uno"])


@pytest.mark.find_match
def test_find_matches_only_returns_language_matches(spanish, repo, _multiple_terms):
    "Searches match the start of string."
    for c in ["PARE", "pare", "PAR"]:
        matches = repo.find_matches(spanish.id, c)
        assert len(matches) == 2, c
        assert matches[0].text == "pare"
        assert matches[0].language_id == spanish.id, "language included"


@pytest.mark.find_match
def test_find_matches_returns_empty_if_no_match_or_empty_string(
    spanish, repo, _multiple_terms
):
    "Empty if no match."
    for c in ["", "x"]:
        matches = repo.find_matches(spanish.id, c)
        assert len(matches) == 0, c


@pytest.mark.find_match
def test_find_matches_multiword_respects_zws(spanish, repo, _multiple_terms):
    "zws handled correctly in search."
    zws = "\u200B"
    for c in [f"tengo{zws} {zws}uno", "tengo uno", "tengo"]:
        matches = repo.find_matches(spanish.id, c)
        assert len(matches) == 1, f'have match for case "{c}"'
        assert matches[0].text == f"tengo{zws} {zws}uno"


def assert_find_matches_returns(term_repo, spanish, s, expected):
    "Helper, assert returns expected content."
    matches = term_repo.find_matches(spanish.id, s)
    actual = ", ".join([t.text for t in matches])
    assert ", ".join(expected) == actual


def test_find_matches_starting_matches_sort_to_top(spanish, repo):
    "All matches return, but words that start with the same thing sort to top."
    add_terms(spanish, ["tener", "contener", "sostener", "ten", "contengo", "xxx"])
    assert_find_matches_returns(
        repo, spanish, "ten", ["ten", "tener", "contener", "contengo", "sostener"]
    )
    assert_find_matches_returns(repo, spanish, "ene", ["contener", "sostener", "tener"])
    assert_find_matches_returns(repo, spanish, "x", ["xxx"])


@pytest.mark.find_match
def test_find_matches_initial_check(spanish, repo):
    "Searches match any part of string."
    add_terms(spanish, ["abc", "abcd", "bcd"])

    assert_find_matches_returns(repo, spanish, "ab", ["abc", "abcd"])
    assert_find_matches_returns(repo, spanish, "abcd", ["abcd"])
    assert_find_matches_returns(repo, spanish, "bcd", ["bcd", "abcd"])
    assert_find_matches_returns(repo, spanish, "yy", [])


@pytest.mark.find_match
def test_find_matches_terms_with_children_go_to_top(spanish, repo):
    """
    Parents go to the top, then the rest ... but exact matches trumps parent.
    """
    terms = [("abc", "abcParent"), ("axy", "axyParent")]
    for term, parent in terms:
        t = Term()
        t.language = spanish
        t.language_id = spanish.id
        t.text = term
        t.parents.append(parent)
        repo.add(t)
    repo.commit()

    assert_find_matches_returns(
        repo, spanish, "a", ["abcParent", "axyParent", "abc", "axy"]
    )
    assert_find_matches_returns(repo, spanish, "ab", ["abcParent", "abc"])
    assert_find_matches_returns(repo, spanish, "abc", ["abc", "abcParent"])


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
def test_get_all_references(spanish, repo):
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

    refs = repo.find_references(tengo)
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
    refs = repo.find_references(tener)
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
def test_multiword_reference(spanish, repo):
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

    refs = repo.find_references(t)
    assert full_refs_to_string(refs) == {
        "term": ["hola (1/1), Yo <b>tengo un</b> gato."],
        "children": [],
        "parents": [],
    }, "term tengo"


@pytest.mark.sentences
def test_get_references_only_includes_read_texts(spanish, repo):
    "Like it says above."
    text = make_text("hola", "Tengo un gato.  No tengo un perro.", spanish)

    tengo = Term()
    tengo.language_id = spanish.id
    tengo.text = "tengo"
    repo.add(tengo)
    repo.commit()

    refs = repo.find_references(tengo)
    keys = refs.keys()
    for k in keys:
        assert len(refs[k]) == 0, f"{k}, no matches for unread texts"

    text.read_date = datetime.now()
    db.session.add(text)
    db.session.commit()

    refs = repo.find_references(tengo)
    assert len(refs["term"]) == 2, "have refs once text is read"


@pytest.mark.sentences
def test_get_references_only_includes_refs_in_same_language(spanish, english, repo):
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

    refs = repo.find_references(tengo)
    assert len(refs["term"]) == 2, "only have 2 refs (spanish)"
    sentences = [r.sentence for r in refs["term"]]
    assert "<b>Tengo</b> un gato." in sentences
    assert "No <b>tengo</b> un perro." in sentences
    assert "<b>Tengo</b> in english." not in sentences


@pytest.mark.sentences
def test_get_references_new_term(spanish, repo):
    "Check references with parents and children."
    text = make_text("hola", "Tengo un gato.", spanish)
    text.read_date = datetime.now()
    db.session.add(text)

    tengo = Term()
    tengo.language_id = spanish.id
    tengo.text = "tengo"

    refs = repo.find_references(tengo)
    assert full_refs_to_string(refs) == {
        "term": ["hola (1/1), <b>Tengo</b> un gato."],
        "children": [],
        "parents": [],
    }, "term tengo"
