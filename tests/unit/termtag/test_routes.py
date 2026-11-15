"""
TermTage mapping tests.
"""

from lute.models.term import Term, TermTag
from lute.db import db
from lute.termtag.routes import delete as route_delete
from tests.dbasserts import assert_record_count_equals, assert_sql_result


def test_deleting_termtag_removes_wordtags_table_record(empty_db, spanish):
    "Association record should be deleted if tag is deleted."

    tg = TermTag("tag")
    db.session.add(tg)
    db.session.commit()

    term = Term(spanish, "HOLA")
    term.add_term_tag(tg)
    db.session.add(term)
    db.session.commit()

    sqlterms = "select * from words"
    assert_record_count_equals(sqlterms, 1, "term sanity check on save")

    sqltags = "select * from tags"
    assert_record_count_equals(sqltags, 1, "tag sanity check on save")

    sqlassoc = "select * from wordtags"
    assert_record_count_equals(sqlassoc, 1, "word tag associations exist")

    route_delete(tg.id)

    assert_record_count_equals(sqlterms, 1, "term stays")
    assert_record_count_equals(sqltags, 0, "tag removed")
    assert_record_count_equals(sqlassoc, 0, "associations removed")


def test_edit_duplicate_tag_text_is_rejected(app, empty_db, spanish):
    "A colliding rename is rejected and leaves the tag and its terms in place."
    kept = TermTag("alpha", "keep-comment")
    other = TermTag("beta", "other-comment")
    db.session.add(kept)
    db.session.add(other)
    db.session.commit()

    term = Term(spanish, "HOLA")
    term.add_term_tag(kept)
    db.session.add(term)
    db.session.commit()

    response = app.test_client().post(
        f"/termtag/edit/{kept.id}",
        data={"text": other.text, "comment": "should-not-save"},
    )

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Tag already exists" in body
    assert "/term/index" in body
    assert_sql_result(
        "select TgID, TgText, TgComment from tags order by TgID",
        [
            f"{kept.id}; alpha; keep-comment",
            f"{other.id}; beta; other-comment",
        ],
        "edited tag unchanged",
    )
    assert_sql_result(
        "select WtTgID from wordtags",
        [f"{kept.id}"],
        "term stays linked only to the edited tag",
    )


def test_edit_tag_to_free_name_keeps_wordtags(app, empty_db, spanish):
    "A free name saves, keeps the tag id, and leaves the term link in place."
    tag = TermTag("alpha", "keep-comment")
    db.session.add(tag)
    db.session.commit()

    term = Term(spanish, "HOLA")
    term.add_term_tag(tag)
    db.session.add(term)
    db.session.commit()

    response = app.test_client().post(
        f"/termtag/edit/{tag.id}",
        data={"text": "gamma", "comment": "keep-comment"},
    )

    assert response.status_code == 302
    assert "/termtag/index" in response.location
    assert_sql_result(
        "select TgID, TgText, TgComment from tags",
        [f"{tag.id}; gamma; keep-comment"],
        "renamed in place",
    )
    assert_sql_result(
        "select WtTgID from wordtags",
        [f"{tag.id}"],
        "wordtags stay on the same tag",
    )


def test_edit_tag_same_text_updates_comment_only(app, empty_db):
    "Saving a tag's own name updates the comment only."
    tag = TermTag("alpha", "old-comment")
    db.session.add(tag)
    db.session.commit()

    response = app.test_client().post(
        f"/termtag/edit/{tag.id}",
        data={"text": "alpha", "comment": "new-comment"},
    )

    assert response.status_code == 302
    assert "/termtag/index" in response.location
    assert_sql_result(
        "select TgID, TgText, TgComment from tags",
        [f"{tag.id}; alpha; new-comment"],
        "comment updated",
    )


def test_new_duplicate_tag_text_is_rejected(app, empty_db):
    "Creating a tag with an existing name is rejected and inserts nothing."
    existing = TermTag("alpha", "keep-comment")
    db.session.add(existing)
    db.session.commit()

    response = app.test_client().post(
        "/termtag/new",
        data={"text": "alpha", "comment": "should-not-save"},
    )

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Tag already exists" in body
    assert "/term/index" in body
    assert_sql_result(
        "select TgText, TgComment from tags",
        ["alpha; keep-comment"],
        "no tag inserted",
    )


def test_edit_tag_different_case_saves(app, empty_db):
    "A different case is a different tag and saves."
    existing = TermTag("Hola", "hola-comment")
    edited = TermTag("other", "other-comment")
    db.session.add(existing)
    db.session.add(edited)
    db.session.commit()

    response = app.test_client().post(
        f"/termtag/edit/{edited.id}",
        data={"text": "hola", "comment": "other-comment"},
    )

    assert response.status_code == 302
    assert "/termtag/index" in response.location
    assert_sql_result(
        "select TgID, TgText from tags order by TgID",
        [f"{existing.id}; Hola", f"{edited.id}; hola"],
        "case-different name saved",
    )
