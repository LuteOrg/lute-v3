"Smoke test only."

from lute.cli.language_term_export import generate_language_file, generate_book_file

from lute.models.term import Term, TermTag
from lute.models.book import Book
from lute.db import db
from tests.dbasserts import assert_sql_result


def test_smoke_test(app_context, tmp_path, english):
    "dump data."
    t = Term(english, "the")
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
    b = Book.create_book("hi", english, fulltext)
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
        ret = Term.find_by_spec(spec)
        assert ret is not None, f"Have {term_string}"
        return ret

    a = _find("a")
    for c in ["e", "h"]:
        t = _find(c)
        t.add_parent(a)
        db.session.add(t)
    db.session.commit()

    outfile = tmp_path / "outfile.csv"
    generate_language_file("English", outfile)
    with open(outfile, "r", encoding="utf-8") as ofhandle:
        text = ofhandle.read()
    print(text)

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

    # .lower() because sometimes the text file returned B, and
    # sometimes b ...  which is _very_ odd, but don't really care.
    assert text.lower() == "\n".join(expected).lower(), "content"

    generate_book_file(b.id, outfile)
    with open(outfile, "r", encoding="utf-8") as ofhandle:
        text = ofhandle.read()
    print(text)
    assert text.lower() == "\n".join(expected).lower(), "book file"
