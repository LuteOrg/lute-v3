"""
Smoke tests.
"""


def test_smoke_test(chromebrowser, luteclient):
    "Hit the main page, create a book, update a term."
    luteclient.visit("/")
    assert chromebrowser.is_text_present("Lute"), "have main page."
    luteclient.make_book("Hola", "Hola. Adios amigo.", "Spanish")
    assert chromebrowser.title == 'Reading "Hola"', "title"
    assert chromebrowser.is_text_present("Hola")
    assert "Hola/. /Adios/ /amigo/." == luteclient.displayed_text()

    updates = {"translation": "hello", "parents": ["adios", "amigo"]}
    luteclient.click_word_fill_form("Hola", updates)
    luteclient.click_word_fill_form("Adios", {"status": "2", "translation": "goodbye"})

    displayed = luteclient.displayed_text()
    assert "Hola (1)/. /Adios (2)/ /amigo (1)/." == displayed


def test_unsupported_language_not_shown(luteclient, _restore_jp_parser):
    "Missing mecab means no Japanese."
    luteclient.load_demo_stories()

    luteclient.change_parser_registry_key("japanese", "disabled_japanese")
    luteclient.visit("/")
    assert not luteclient.browser.is_text_present("Japanese"), "no Japanese demo book."
    assert luteclient.browser.is_text_present(
        "Tutorial"
    ), "Tutorial is available though."
