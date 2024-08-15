"""
TermTage mapping tests.
"""

from sqlalchemy import text
from lute.models.term import Term, TermTag
from lute.db import db
from tests.dbasserts import assert_record_count_equals

# from lute.termtag.routes import delete as route_delete


def test_deleting_termtag_removes_wordtags_table_record(empty_db, spanish):
    """
    Association record should be deleted if tag is deleted.

    Annoying test ... during unit testing, deleting TermTag entity
    causes the association table records wordtags to be deleted
    correctly, but during actual operation -- i.e., deletion of a
    TermTag through the UI -- the records aren't being deleted.
    Can't explain why, and I don't want to waste more time trying
    to figure it out.
    """

    tg = TermTag("tag")
    db.session.add(tg)
    db.session.commit()

    term = Term(spanish, "HOLA")
    term.add_term_tag(tg)
    db.session.add(term)
    db.session.commit()

    # The tag association for HOLA is getting deleted correctly
    # when the "tag" tag is deleted, which is odd because it's
    # not getting deleted when the action is called from the UI
    # (ref https://github.com/LuteOrg/lute-v3/issues/455).
    #
    # Trying adding another term, with directly inserting
    # the data in the table, to see if that is deleted correctly ...
    # ... and it is.
    perro = Term(spanish, "perro")
    db.session.add(perro)
    db.session.commit()

    sql = f"insert into wordtags (WtWoID, WtTgID) values ({perro.id}, {tg.id})"
    db.session.execute(text(sql))
    db.session.commit()

    # Trying loading data directly into the DB, so that the db session orm
    # isn't aware of a Term.  This too is deleted correctly.
    sql = f"""insert into words (WoLgID, WoText, WoTextLC, WoStatus)
      values ({spanish.id}, 'gato', 'gato', 1)"""
    db.session.execute(text(sql))
    db.session.commit()

    sql = f"insert into wordtags (WtWoID, WtTgID) values ({perro.id + 1}, {tg.id})"
    db.session.execute(text(sql))
    db.session.commit()

    sqltags = "select * from tags"
    assert_record_count_equals(sqltags, 1, "tag sanity check on save")

    sqlassoc = "select * from wordtags"
    assert_record_count_equals(sqlassoc, 3, "word tag associations exist")

    termtag = TermTag.find(tg.id)
    # route_delete(tg.id)
    db.session.delete(termtag)
    db.session.commit()

    assert_record_count_equals(sqltags, 0, "tag removed")
    assert_record_count_equals(sqlassoc, 0, "associations removed")
