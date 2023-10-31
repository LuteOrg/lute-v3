"""
Smoke tests.
"""

def test_hit_main_page(browser):
    "Hit the main page."
    url = "http://localhost:9876/"
    browser.visit(url)
    assert browser.is_text_present('Lute'), 'have main page.'
