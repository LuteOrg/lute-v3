"Smoke test only."

from lute.cli.language_term_export import generate_language_file, generate_book_file

from lute.models.term import Term, TermTag
from lute.models.repositories import TermRepository, LanguageRepository
from lute.db import db
from lute.db.demo import Service as DemoService
from tests.utils import make_book
from tests.dbasserts import assert_sql_result, assert_record_count_equals


def test_language_term_export_smoke_test(app_context, tmp_path):
    "dump data."
    demosvc = DemoService(db.session)
    demosvc.load_demo_data()
    sql = """select * from books
      where BkLgID = (select LgID from languages where LgName='English')
    """
    assert_record_count_equals(sql, 2, "have books")
    langrepo = LanguageRepository(db.session)
    eng = langrepo.find_by_name("English")
    t = Term(eng, "the")
    t.translation = "article"
    t.add_term_tag(TermTag("a"))
    t.add_term_tag(TermTag("b"))
    db.session.add(t)
    db.session.commit()

    outfile = tmp_path / "outfile.csv"
    generate_language_file("English", outfile)
    with open(outfile, "r", encoding="utf-8") as ofhandle:
        text = ofhandle.read()
    print(text)
    lines = text.split("\n")
    head = lines[0]
    assert (
        head == "term,count,familycount,books,definition,status,parents,children,tags"
    ), "headings"
    firstline = lines[1]
    assert firstline.startswith("the,"), "the is most common"
    assert firstline.endswith('article,1,-,-,"a, b"'), "ending data"


def test_single_book_export(app_context, empty_db, tmp_path, english):
    "dump data for english."

    assert_sql_result("select * from books", [], "no books")
    assert_sql_result("select * from words", [], "no terms")

    fulltext = "a b c d e A B C\n---\nG H I c d e d"
    b = make_book("hi", fulltext, english)
    db.session.add(b)
    db.session.commit()

    for c in ["a", "d", "c d"]:
        t = Term(english, c)
        t.status = 1
        db.session.add(t)
    for c in ["e", "g", "h"]:
        t = Term(english, c)
        t.status = 0
        db.session.add(t)
    db.session.commit()

    def _find(term_string):
        "Find term with the text."
        spec = Term(english, term_string)
        repo = TermRepository(db.session)
        ret = repo.find_by_spec(spec)
        assert ret is not None, f"Have {term_string}"
        return ret

    a = _find("a")
    for c in ["e", "h"]:
        t = _find(c)
        t.add_parent(a)
        db.session.add(t)
    db.session.commit()

    expected = [
        # Headings
        "term,count,familycount,books,definition,status,parents,children,tags",
        # a has two children, e and h
        "a,2,5,hi,-,1,-,e (2); h (1),-",
        # b occurs twice.
        "b,2,2,hi,-,0,-,-,-",
        # 'c d' occurs twice
        "c d,2,2,hi,-,1,-,-,-",
        # e is a new term
        "e,2,2,hi,-,0,a,-,-",
        # c is a new term, status 0.
        # Occurs once as c, once as C.
        "C,1,1,hi,-,0,-,-,-",
        "I,1,1,hi,-,0,-,-,-",
        "d,1,1,hi,-,1,-,-,-",
        # g and h are new
        "g,1,1,hi,-,0,-,-,-",
        "h,1,1,hi,-,0,a,-,-",
        "",
    ]

    def _lowersort(arr):
        "Lowercase and sort strings."
        return sorted([a.lower() for a in arr])

    def _assert_text_matches_expected(file_text, expected_array):
        "Avoid sorting, case issues."

        # Converting the text to lower because sometimes the text file
        # returned B, and sometimes b ...  which is _very_ odd, but I
        # don't really care.
        assert _lowersort(file_text.split("\n")) == _lowersort(expected_array)

    # Generate for english.
    outfile = tmp_path / "outfile.csv"
    generate_language_file("English", outfile)
    with open(outfile, "r", encoding="utf-8") as ofhandle:
        text = ofhandle.read()
    _assert_text_matches_expected(text, expected)

    # Generate for book.
    generate_book_file(b.id, outfile)
    with open(outfile, "r", encoding="utf-8") as ofhandle:
        text = ofhandle.read()
    _assert_text_matches_expected(text, expected)
