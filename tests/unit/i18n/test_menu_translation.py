"""
UI translation of the main menu.
"""


def test_menu_defaults_to_english(client):
    "No Accept-Language header => English."
    html = client.get("/").get_data(as_text=True)
    assert "Settings" in html
    assert "Paramètres" not in html


def test_menu_uses_browser_language(client):
    "French browser => French menu."
    resp = client.get("/", headers={"Accept-Language": "fr-FR,fr;q=0.9"})
    html = resp.get_data(as_text=True)
    assert "Paramètres" in html


def test_unsupported_language_falls_back_to_english(client):
    "No translation for the browser language => English."
    resp = client.get("/", headers={"Accept-Language": "ja"})
    html = resp.get_data(as_text=True)
    assert "Settings" in html
