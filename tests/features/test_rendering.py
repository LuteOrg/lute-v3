from pytest_bdd import given, when, then, scenarios, parsers

from lute.db import db
from lute.models.language import Language
from lute.models.term import Term
from lute.term.model import Repository
from lute.read.service import get_paragraphs, set_unknowns_to_known

from tests.utils import add_terms, make_text
from tests.dbasserts import assert_sql_result


# The current language being used.
language = None

# The Text object
text = None

scenarios('rendering.feature')


@given('demo data')
def given_demo_data(app_context):
    "Calling app_context loads the demo data."

@given(parsers.parse('language {langname}'))
def given_lang(langname):
    global language
    lang = db.session.query(Language).filter(Language.name == langname).first()
    assert lang.name == langname, 'sanity check'
    language = lang


@given(parsers.parse('terms:\n{content}'))
def given_terms(content):
    terms = content.split("\n")
    add_terms(language, terms)


@given(parsers.parse('term "{content}" with status {status}'))
def given_terms(content, status):
    r = Repository(db)
    t = r.find_or_new(language.id, content)
    t.status = int(status)
    r.add(t)
    r.commit()


@given(parsers.parse('text:\n{content}'))
def given_text(content):
    global text
    text = make_text('test', content, language)
    db.session.add(text)
    db.session.commit()


@given('all unknowns are set to known')
def set_to_known():
    global text
    set_unknowns_to_known(text)


@then(parsers.parse('rendered should be:\n{content}'))
def then_rendered_should_be(content):
    def stringize(ti):
        zws = '\u200B'
        status = ''
        if ti.wo_status not in [ None, 0 ]:
            status = f'({ti.wo_status})'
        return ti.display_text.replace(zws, '') + status

    global text
    paras = get_paragraphs(text)
    ret = []
    for p in paras:
        tis = [t for s in p for t in s.textitems]
        ss = [stringize(ti) for ti in tis]
        ret.append('/'.join(ss))
    actual = '/<PARA>/'.join(ret)

    expected = content.split("\n")
    assert actual == "/<PARA>/".join(expected)


@then(parsers.parse('words table should contain:\n{text_lc_content}'))
def then_words_table_contains_WoTextLC(text_lc_content):
    expected = text_lc_content.split("\n")
    sql = "select WoTextLC from words order by WoTextLC"
    assert_sql_result(sql, expected)
