"""
Smoke tests, just hitting various pages and ensuring things work.
"""

def _run_checks(client, pagechecks):
    """
    Check all pages return 200, have content.
    """
    for p, checks in pagechecks.items():
        resp = client.get(p)
        assert resp.status_code == 200, f"{p} OK"
        for c in checks:
            assert bytes(c, 'utf-8') in resp.data, f"{p} content"


def test_smoke_pages(demo_client):
    "Hit pages, ensure 200 status, and expected content is present."
    pagechecks = {
        '/': [ 'Lute' ],  # TODO smoke: add_Tutorial_check
        '/language/index': [ 'English' ],
        '/language/new': [ 'Create new Language' ],
        '/language/new/English': [ 'Create new Language', 'https://en.thefreedictionary.com/###' ],
        '/language/edit/1': [ 'Edit Language' ],
    }
    _run_checks(demo_client, pagechecks)


def test_smoke_empty_db_pages(empty_client):
    "Some pages have special content blocks when no data is defined."
    pagechecks = {
        '/': [ 'Lute' ],  # TODO smoke: add_no_books_check
        '/language/index': [ 'No languages defined' ],
    }
    _run_checks(empty_client, pagechecks)
