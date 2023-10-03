"""
Smoke tests, just hitting various pages and ensuring things work.
"""

def test_smoke_pages(demo_client):
    """
    All pages should work.
    """

    check_pages = [
        '/language/index'
    ]
    for p in check_pages:
        assert demo_client.get(p).status_code == 200, f"Check {p}"
