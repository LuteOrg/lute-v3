"""
Test dictionary popup window reuse.
"""


def test_dictionary_popup_reuses_window(luteclient):
    """
    Verify that subsequent lookups reuse the same popup dictionary window.
    """
    # 1. Update Spanish dictionary to be popuphtml
    luteclient.visit(
        "dev_api/execsql/UPDATE%20languagedicts%20SET%20LdType%20%3D%20%27popuphtml%27"
    )

    # 2. Create a book in Spanish
    luteclient.make_book("Hola", "Hola. Adios.", "Spanish")

    # 3. Click the word "Hola" to load the term form in the iframe 'wordframe'
    luteclient.click_word("Hola")

    # Get browser context to count the open pages/tabs
    context = luteclient.page.context
    initial_page_count = len(context.pages)

    # Wait for the dictionary button in the main page and click it
    dict_btn = luteclient.page.locator(".dict-btn-external").first

    # 5. Click the dict button and expect a popup window to open
    with luteclient.page.expect_popup():
        dict_btn.click()

    # Check that a new page was opened
    assert len(context.pages) == initial_page_count + 1

    # 6. Now click the word "Adios" in the reading pane to switch to editing "Adios"
    luteclient.click_word("Adios")

    # Wait for the dictionary button in the main page again
    dict_btn_2 = luteclient.page.locator(".dict-btn-external").first

    # 7. Click the dict button again
    dict_btn_2.click()

    # Let's wait to see if any new window opens
    luteclient.sleep(1)

    # Assert that there is still only one popup window (the first one was reused)
    assert len(context.pages) == initial_page_count + 1


def test_dictionary_popup_closed_on_unload(luteclient):
    """
    Verify that popup dictionary windows are closed when navigating away from the book.
    """
    # 1. Update Spanish dictionary to be popuphtml
    luteclient.visit(
        "dev_api/execsql/UPDATE%20languagedicts%20SET%20LdType%20%3D%20%27popuphtml%27"
    )

    # 2. Create Book 1 in Spanish
    luteclient.make_book("Hola", "Hola. Adios.", "Spanish")
    luteclient.click_word("Hola")

    # Wait for the dictionary button in the main page and click it
    dict_btn = luteclient.page.locator(".dict-btn-external").first

    context = luteclient.page.context
    initial_page_count = len(context.pages)

    # Click the dict button and expect a popup window to open
    with luteclient.page.expect_popup():
        dict_btn.click()

    # Check that a new page was opened
    assert len(context.pages) == initial_page_count + 1

    # 3. Navigate back to Home
    # Find home button/link. The logo or title has title="Home".
    luteclient.page.locator('[title="Home"]').first.click()
    luteclient.sleep(1)  # wait for page transition and unload event

    # The popup should be closed automatically on unload
    assert len(context.pages) == initial_page_count
