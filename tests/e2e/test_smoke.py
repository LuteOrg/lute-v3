"""
Smoke tests, just hitting various pages and ensuring things work.
"""

def test_smoke_pages(demo_client):
    """
    All pages should work.
    """

    checks = {
        '/': [ 'Lute' ],  # TODO:add_Tutorial_check
        '/language/index': [ 'English' ],
    }
    for p in checks.keys():
        resp = demo_client.get(p)
        assert resp.status_code == 200, f"{p} OK"
        for c in checks[p]:
            assert bytes(c, 'utf-8') in resp.data, f"{p} content"


def test_smoke_empty_db_pages(empty_client):
    """
    All pages should work.
    """

    checks = {
        '/': [ 'Lute' ],  # TODO:add_Tutorial_check
        '/language/index': [ 'No languages defined' ],
    }
    for p in checks.keys():
        resp = empty_client.get(p)
        assert resp.status_code == 200, f"{p} OK"
        for c in checks[p]:
            assert bytes(c, 'utf-8') in resp.data, f"{p} content"
