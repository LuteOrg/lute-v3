"""
Smoke tests.
"""

def test_hit_main_page(chromebrowser, request):
    "Hit the main page, sanity check only."
    useport = request.config.getoption("--port")
    url = f"http://localhost:{useport}/"
    chromebrowser.visit(url)
    assert chromebrowser.is_text_present('Lute'), 'have main page.'


def test_create_book(chromebrowser, luteclient):
    "Try creating a book."
    luteclient.visit('/')
    assert chromebrowser.is_text_present('Lute'), 'have main page.'
    luteclient.make_book('Hola', 'Hola. Adios amigo.', 'Spanish')
    assert chromebrowser.title == 'Reading "Hola (1/1)"', 'title'
    assert chromebrowser.is_text_present('Hola')
    assert 'Hola/. /Adios/ /amigo/.' == luteclient.displayed_text()

    updates = {
        'translation': 'hello',
        'parents': [ 'adios', 'amigo' ]
    }
    luteclient.click_word_fill_form('Hola', updates)
    luteclient.click_word_fill_form('Adios', { 'translation': 'goodbye' })

    displayed = luteclient.displayed_text()
    assert 'Hola (1)/. /Adios (1)/ /amigo (1)/.' == displayed
