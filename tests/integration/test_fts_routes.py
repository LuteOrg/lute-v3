"""
Integration tests for FTS search routes.
"""

from bs4 import BeautifulSoup
from lute.db import db
from tests.utils import make_book


def test_fts_search_route(app, app_context, spanish):
    """
    Verify search rendering and search_datatables endpoint.
    """
    # Create a book to search
    b1 = make_book(
        "Test Search Book", ["Este es un libro de prueba.", "Hola amigo."], spanish
    )
    for text_obj in b1.texts:
        text_obj.load_sentences()
    db.session.add(b1)
    db.session.commit()

    client = app.test_client()

    # Test FTS search template route
    response = client.get("/book/search")
    assert response.status_code == 200
    assert b"Content search" in response.data

    # Test datatables search route
    search_url = (
        f"/book/search_datatables?term=libro&book_id={b1.id}&draw=1&start=0&length=10"
    )
    response2 = client.get(search_url)
    assert response2.status_code == 200
    data = response2.get_json()

    assert data["draw"] == 1
    assert data["recordsTotal"] == 1
    assert data["recordsFiltered"] == 1
    assert data["data"][0]["title"] == "Test Search Book"
    assert data["data"][0]["text"] == "Este es un libro de prueba."
    assert data["data"][0]["page"] == 1


def test_fts_modal_table_visibility(app, app_context, spanish):
    """
    Ensure the book search table in read/index.html does not have display: none inline style.
    """
    b1 = make_book("Test Table Visibility", ["Este es un libro."], spanish)
    for text_obj in b1.texts:
        text_obj.load_sentences()
    db.session.add(b1)
    db.session.commit()

    client = app.test_client()
    response = client.get(f"/read/{b1.id}")
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find(id="bookSearchTable")
    assert table is not None, "bookSearchTable should be present in the DOM"

    style = table.get("style", "")
    assert "display: none" not in style, "Search table has display: none style"


def test_fts_search_archived_books(app, app_context, spanish):
    """
    Verify search_datatables filters archived books by default, and returns them when requested.
    """
    b1 = make_book("Archived Book", ["Este es un libro archivado."], spanish)
    for text_obj in b1.texts:
        text_obj.load_sentences()
    b1.archived = True
    db.session.add(b1)
    db.session.commit()

    client = app.test_client()

    # Search with show_archived=false (default) -> should not return the archived book
    url_hidden = (
        "/book/search_datatables"
        "?term=libro&show_archived=false&draw=1&start=0&length=10"
    )
    res_hidden = client.get(url_hidden)
    assert res_hidden.status_code == 200
    data_hidden = res_hidden.get_json()
    assert data_hidden["recordsTotal"] == 0

    # Search with show_archived=true -> should return the archived book
    url_shown = (
        "/book/search_datatables"
        "?term=libro&show_archived=true&draw=1&start=0&length=10"
    )
    res_shown = client.get(url_shown)
    assert res_shown.status_code == 200
    data_shown = res_shown.get_json()
    assert data_shown["recordsTotal"] == 1
    assert data_shown["data"][0]["title"] == "Archived Book"
