"""
Step defs for term_rendering.feature.
"""
# pylint: disable=missing-function-docstring

from pytest_bdd import given, then, scenarios, parsers

from lute.db import db
from lute.models.language import Language
from lute.term.model import Repository
from lute.read.render.service import get_paragraphs
from lute.read.service import set_unknowns_to_known, bulk_status_update

from tests.utils import add_terms, make_text
from tests.dbasserts import assert_sql_result


# The current language being used.
language = None

# The Text object
text = None

scenarios("rendering.feature")


@given("demo data")
def given_demo_data(app_context):
    "Calling app_context loads the demo data."


@given(parsers.parse("language {langname}"))
def given_lang(langname):
    global language  # pylint: disable=global-statement
    lang = db.session.query(Language).filter(Language.name == langname).first()
    assert lang.name == langname, "sanity check"
    language = lang


@given(parsers.parse("terms:\n{content}"))
def given_terms(content):
    terms = content.split("\n")
    add_terms(language, terms)


@given(parsers.parse('term "{content}" with status {status} and parent "{parenttext}"'))
def given_term_with_status_and_parent(content, status, parenttext):
    r = Repository(db)
    t = r.find_or_new(language.id, content)
    t.status = int(status)
    t.parents.append(parenttext)
    r.add(t)
    r.commit()


@given(parsers.parse('term "{content}" with status {status}'))
def given_term_with_status(content, status):
    r = Repository(db)
    t = r.find_or_new(language.id, content)
    t.status = int(status)
    r.add(t)
    r.commit()


@given(parsers.parse("text:\n{content}"))
def given_text(content):
    global text  # pylint: disable=global-statement
    text = make_text("test", content, language)
    db.session.add(text)
    db.session.commit()


@given("all unknowns are set to known")
def set_to_known():
    set_unknowns_to_known(text)


@given(parsers.parse("bulk status {newstatus} update for terms:\n{terms}"))
def update_status(newstatus, terms):
    bulk_status_update(text, terms.split("\n"), int(newstatus))


def _assert_stringized_equals(stringizer, joiner, expected):
    """
    Get paragraphs and stringize all textitems,
    join and assert equals expected.
    """
    paras = get_paragraphs(text.text, text.book.language)
    ret = []
    for p in paras:
        tis = [t for s in p for t in s.textitems]
        ss = [stringizer(ti) for ti in tis]
        ret.append(joiner.join(ss))
    actual = "/<PARA>/".join(ret)

    expected = expected.split("\n")
    assert actual == "/<PARA>/".join(expected)


@then(parsers.parse("rendered should be:\n{expected}"))
def then_rendered_should_be(expected):
    """
    Renders /term(status)/ /term/ /term/, compares with expected.
    """

    def stringize(ti):
        zws = "\u200B"
        status = ""
        if ti.wo_status not in [None, 0]:
            status = f"({ti.wo_status})"
        return ti.display_text.replace(zws, "") + status

    _assert_stringized_equals(stringize, "/", expected)


@then(parsers.parse("known-only rendered should be:\n{expected}"))
def known_only_rendered_should_be(expected):
    def stringize(ti):
        s = ti.display_text
        if ti.wo_status not in [None, 0]:
            s = f"[[{s}]]"
        zws = "\u200B"
        return s.replace(zws, "")

    _assert_stringized_equals(stringize, "", expected)


@then(parsers.parse("words table should contain:\n{text_lc_content}"))
def then_words_table_contains_WoTextLC(text_lc_content):
    expected = text_lc_content.split("\n")
    sql = "select WoTextLC from words order by WoTextLC"
    assert_sql_result(sql, expected)
