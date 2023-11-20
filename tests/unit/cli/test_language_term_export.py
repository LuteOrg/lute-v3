"Smoke test only."

from lute.cli.language_term_export import generate_file


def test_smoke_test(app_context, tmp_path):
    "dump data."
    outfile = tmp_path / "outfile.csv"
    generate_file("English", outfile)
    with open(outfile, "r", encoding="utf-8") as ofhandle:
        text = ofhandle.read()
    print(text)
    lines = text.split("\n")
    assert (
        lines[0] == "term,count,familycount,books,definition,status,children"
    ), "headings"
    assert lines[1].startswith("the,"), "the is most common"
