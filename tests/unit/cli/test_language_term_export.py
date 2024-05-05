"Smoke test only."

from lute.cli.language_term_export import generate_file

from lute.models.term import Term, TermTag
from lute.db import db


def test_smoke_test(app_context, tmp_path, english):
    "dump data."
    t = Term(english, "the")
    t.translation = "article"
    t.add_term_tag(TermTag("a"))
    t.add_term_tag(TermTag("b"))
    db.session.add(t)
    db.session.commit()

    outfile = tmp_path / "outfile.csv"
    generate_file("English", outfile)
    with open(outfile, "r", encoding="utf-8") as ofhandle:
        text = ofhandle.read()
    print(text)
    lines = text.split("\n")
    assert (
        lines[0] == "term,count,familycount,books,definition,status,children,tags"
    ), "headings"
    firstline = lines[1]
    assert firstline.startswith("the,"), "the is most common"
    assert firstline.endswith('article,1,-,"a, b"'), "ending data"
