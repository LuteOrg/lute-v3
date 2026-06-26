"Testing full text search."

from sqlalchemy import text
import pytest
from lute.db import db
from lute.models.language import Language

from tests.utils import make_book


@pytest.fixture(name="english")
def _english(app_context):
    "Setup English language."
    lg = Language()
    lg.name = "English"
    lg.character_substitutions = "´='|`='"
    lg.regexp_split_sentences = ".!?"
    lg.exceptions_split_sentences = "Mr.|Mrs."
    lg.regexp_word_characters = "a-zA-Z"
    lg.right_to_left = False
    db.session.add(lg)
    db.session.commit()
    return lg


def test_fts_sync_insert_update_delete(english):
    """
    Verify that FTS5 table and triggers sync inserts, updates, and deletes correctly.
    """
    # 1. Create a book
    b = make_book("My Book Title", "This is the content of text 1.", english)
    db.session.add(b)
    db.session.commit()

    # The book should automatically populate the texts_fts table
    # Retrieve the text ID
    tx = b.texts[0]
    tx_id = tx.id

    result = db.session.execute(
        text("SELECT BkTitle, TxText FROM texts_fts WHERE rowid = :tx_id"),
        {"tx_id": tx_id},
    ).fetchone()

    assert result is not None
    assert result[0] == "My Book Title"
    assert result[1] == "This is the content of text 1."

    # 2. Update text content
    tx.text = "Updated text content."
    db.session.add(tx)
    db.session.commit()

    result = db.session.execute(
        text("SELECT BkTitle, TxText FROM texts_fts WHERE rowid = :tx_id"),
        {"tx_id": tx_id},
    ).fetchone()
    assert result[1] == "Updated text content."

    # 3. Update book title
    b.title = "Updated Book Title"
    db.session.add(b)
    db.session.commit()

    result = db.session.execute(
        text("SELECT BkTitle, TxText FROM texts_fts WHERE rowid = :tx_id"),
        {"tx_id": tx_id},
    ).fetchone()
    assert result[0] == "Updated Book Title"

    # 4. Search via FTS5
    search_result = db.session.execute(
        text(
            "SELECT rowid FROM texts_fts WHERE texts_fts MATCH 'Updated' ORDER BY rank"
        )
    ).fetchall()
    assert len(search_result) > 0
    assert search_result[0][0] == tx_id

    # 5. Delete the book (and therefore the text)
    db.session.delete(b)
    db.session.commit()

    result = db.session.execute(
        text("SELECT COUNT(*) FROM texts_fts WHERE rowid = :tx_id"), {"tx_id": tx_id}
    ).scalar()
    assert result == 0
