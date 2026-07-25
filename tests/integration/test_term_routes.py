"""
Integration tests for term routes.
"""

from lute.models.book import Book, Text
from lute.db import db


def test_mark_current_page(client, empty_db, spanish):
    "Can mark current page of a book via AJAX endpoint."
    book = Book("Integration Test Book", spanish)
    page1 = Text(book, "Hola tengo un gato.", 1)
    page2 = Text(book, "Adiós tengo un perro.", 2)
    db.session.add(book)
    db.session.commit()

    # Initial state
    assert book.current_tx_id in (page1.id, 0)

    # Mark page 2 as current
    response = client.post(f"/term/mark_current_page/{book.id}/2")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["pagenum"] == 2

    # Refresh from db
    db.session.refresh(book)
    assert book.current_tx_id == page2.id


def test_term_index_contains_books_json(client, empty_db, spanish):
    "Index route returns books JSON."
    book = Book("Another Integration Test Book", spanish)
    Text(book, "Test page.", 1)
    db.session.add(book)
    db.session.commit()

    response = client.get("/term/index")
    assert response.status_code == 200
    assert b"Another Integration Test Book" in response.data
