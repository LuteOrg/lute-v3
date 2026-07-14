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


def test_fts_search_ui_elements(app, app_context):
    """
    Assert that the Content search page contains the Clean Selection button
    and the filter loading spinner indicator.
    """
    client = app.test_client()
    response = client.get("/book/search")
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")

    # Assert Clean Selection button exists
    clear_btn = soup.find(id="clearBookSelection")
    assert (
        clear_btn is not None
    ), "Clean Selection button #clearBookSelection should be present"

    # Assert loading spinner exists
    waiting_spinner = soup.find(id="filterWaiting")
    assert (
        waiting_spinner is not None
    ), "Loading spinner #filterWaiting should be present"


def test_fts_peek_page_highlight(app, app_context, spanish):
    """
    Ensure that peeking a page with ?highlight=term passes the highlight term
    to the client-side JavaScript.
    """
    b1 = make_book(
        "Test Highlight Book", ["Este es un libro con la palabra prueba."], spanish
    )
    for text_obj in b1.texts:
        text_obj.load_sentences()
    db.session.add(b1)
    db.session.commit()

    client = app.test_client()
    url = f"/read/{b1.id}/peek/1?highlight=prueba"
    response = client.get(url)
    assert response.status_code == 200
    assert b'window.tempHighlightTerm = "prueba";' in response.data


def test_fts_peek_page_phrase_highlight(app, app_context, spanish):
    """
    Verify that peeking a page with a full sentence highlight passes the entire
    phrase to client-side JavaScript.
    """
    b1 = make_book(
        "Test Highlight Book", ["Este es un libro con la palabra prueba."], spanish
    )
    for text_obj in b1.texts:
        text_obj.load_sentences()
    db.session.add(b1)
    db.session.commit()

    client = app.test_client()
    phrase = "Este es un libro con la palabra prueba."
    url = f"/read/{b1.id}/peek/1?highlight={phrase}"
    response = client.get(url)
    assert response.status_code == 200
    expected_js = f'window.tempHighlightTerm = "{phrase}";'.encode("utf-8")
    assert expected_js in response.data


def test_fts_search_table_phrase_link(app, app_context):
    """
    Ensure search.html template DataTable renders click navigation action passing
    the full row.text rather than just the search term keyword.
    """
    client = app.test_client()
    response = client.get("/book/search")
    assert response.status_code == 200
    expected_js = b"highlight=${encodeURIComponent(row.text)}"
    assert expected_js in response.data


def test_fts_search_multiple_highlights_js(app, app_context):
    """
    Verify that search.html contains regex logic to replace multiple occurrences of a term.
    """
    client = app.test_client()
    response = client.get("/book/search")
    assert response.status_code == 200
    # Before the fix, the template contains indexOf logic;
    # after the fix, it should use RegExp global matching.
    assert b"new RegExp" in response.data


def test_fts_delegated_click_handler(app, app_context, spanish):
    """
    Ensure index.html has a delegated click handler for fts-goto-arrow.
    """
    b1 = make_book("Test Click Handler Book", ["Book text."], spanish)
    for text_obj in b1.texts:
        text_obj.load_sentences()
    db.session.add(b1)
    db.session.commit()

    client = app.test_client()
    response = client.get(f"/read/{b1.id}")
    assert response.status_code == 200
    # The template should contain delegated event registration
    assert b"$('#bookSearchTable').on('click', '.fts-goto-arrow'" in response.data


def test_fts_magnifier_conditional_search_behavior(app, app_context, spanish):
    """
    Verify that index.html implements conditional search restore on magnifier click
    and cleans up sessionStorage when returning to reading mode.
    """
    b1 = make_book("Test Search Restore Book", ["Book text."], spanish)
    for text_obj in b1.texts:
        text_obj.load_sentences()
    db.session.add(b1)
    db.session.commit()

    client = app.test_client()
    response = client.get(f"/read/{b1.id}")
    assert response.status_code == 200

    # The template should check returnToReadingBanner visibility on magnifier click
    assert b"$('#returnToReadingBanner').is(':visible')" in response.data
    # The returnToReadingPage function should clear lastBookSearchQuery from sessionStorage
    assert b"sessionStorage.removeItem(`lastBookSearchQuery-" in response.data
