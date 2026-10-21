"Data cleanup tests."

from datetime import datetime
import pytest
from sqlalchemy import text as sqltext
from lute.db import db
from lute.db.data_cleanup import clean_data
from lute.models.language import Language
from tests.utils import make_text
from tests.dbasserts import assert_sql_result


def test_cleanup_does_not_hide_unexpected_parser_errors(spanish, monkeypatch):
    "Only regular expression errors can be skipped during word count cleanup."
    text = make_text("test", "Hola amigo.", spanish)
    text.word_count = None
    db.session.add(text)
    db.session.commit()

    def fail_parse(*args):
        raise ValueError("Unexpected parser failure")

    monkeypatch.setattr(Language, "get_parsed_tokens", fail_parse)
    with pytest.raises(ValueError, match="Unexpected parser failure"):
        clean_data(db.session, lambda message: None)


# Cleaning up missing sentence.SeTextLC records.


def test_cleanup_loads_missing_sentence_textlc(app_context, spanish):
    """
    Load the sentence.SeTextLC.

    If the sqlite LOWER(SeText) would be the same as the parser-generated lowercase text,
    store the special char '*' only, don't waste file space storing the parser-generated lc text.
    """

    t = make_text("test", "gato. Ábrelo. tengo. QUIERO. Ábrela. ábrela.", spanish)
    t.read_date = datetime.now()
    db.session.add(t)
    db.session.commit()

    # Force re-calc.
    sqlhack = """
    update sentences set SeTextLC = null
    where SeText not like '%gato%' and SeText not like '%brelo%'
    """
    db.session.execute(sqltext(sqlhack))
    db.session.commit()
    sql = "select SeText, SeTextLC from sentences order by SeID"
    preclean = [
        "/gato/./; *",
        "/Ábrelo/./; /ábrelo/./",
        "/tengo/./; None",
        "/QUIERO/./; None",
        "/Ábrela/./; None",
        "/ábrela/./; None",
    ]
    assert_sql_result(sql, preclean, "pre-clean")

    def _output(s):
        print(s, flush=True)

    clean_data(db.session, _output)

    postclean = [
        "/gato/./; *",
        "/Ábrelo/./; /ábrelo/./",
        "/tengo/./; *",
        "/QUIERO/./; *",
        "/Ábrela/./; /ábrela/./",
        "/ábrela/./; *",
    ]
    assert_sql_result(sql, postclean, "post-clean")
