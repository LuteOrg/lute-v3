"""
Playwright check: Tibetan text uses Tibetan-capable fonts.

Requires the app running locally (same assumption as other Playwright tests).
"""

import re

from playwright.sync_api import sync_playwright


BASE_URL = "http://localhost:5001"

# Anything containing these indicates a Tibetan-capable font was picked up.
TIBETAN_FONT_CUES = [
    "Lute Tibetan Fallback",
    "Noto Sans Tibetan",
    "Noto Serif Tibetan",
    "Kailasa",
    "Microsoft Himalaya",
    "Jomolhari",
    "Tibetan Machine Uni",
]

# Cues that the theme stack is still present for non-Tibetan text.
THEME_FONT_CUES = [
    "Rubik",
    "Lucida Grande",
    "Georgia",
    "Times New Roman",
    "Arial",
    "Segoe UI",
    "-apple-system",
    "BlinkMacSystemFont",
]


def _load_tibetan_book(page):
    """
    Reset demo data, load predefined Tibetan language (with sample book),
    and navigate to its first book page.
    """
    page.goto(f"{BASE_URL}/dev_api/load_demo")
    page.goto(f"{BASE_URL}/language/load_predefined/Tibetan")
    page.goto(BASE_URL + "/")

    # Click the Tibetan book link (title starts with Tibetan characters).
    tibetan_title_pattern = re.compile(r"[\u0f00-\u0fff]+")
    page.get_by_role("link", name=tibetan_title_pattern).click()

    # Wait for reading text to be present.
    page.wait_for_selector("#thetext span.textitem")


def test_tibetan_font_fallback():
    """
    Tibetan characters should render using a Tibetan-capable font
    (from the fallback stack), not the default theme font.
    """
    with sync_playwright() as sp:
        browser = sp.chromium.launch()
        page = browser.new_page()
        _load_tibetan_book(page)

        font = page.locator("#thetext span.textitem").first.evaluate(
            "el => getComputedStyle(el).fontFamily"
        )
        assert any(cue in font for cue in TIBETAN_FONT_CUES), (
            "Expected a Tibetan-capable font in computed font-family; " f"got: {font}"
        )

        # Sanity: non-Tibetan UI text (body) should still include a theme/system font.
        ui_font = page.locator("body").evaluate("el => getComputedStyle(el).fontFamily")
        assert any(cue in ui_font for cue in THEME_FONT_CUES), (
            "Expected theme/system font cues in UI computed font-family; "
            f"got: {ui_font}"
        )

        browser.close()
