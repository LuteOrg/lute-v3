"""
Acceptance test fixtures.
"""

import requests
import time
import pytest
from selenium.webdriver.common.keys import Keys
from splinter import Browser
from selenium.webdriver.chrome.options import Options as ChromeOptions

from tests.acceptance.lute_test_client import LuteTestClient

def pytest_addoption(parser):
    """
    Command-line args for pytest runs.
    """
    parser.addoption("--port", action="store", type=int, help="Specify the port number")
    parser.addoption("--headless", action='store_true', help="Run the test as headless")


@pytest.fixture(name='chromebrowser', scope='session')
def session_chrome_browser(request):
    """
    Create a chrome browser.

    For some weird reason, this performs **MUCH**
    better than the default "browser" fixture provided by
    splinter/pytest-splinter:

    "with self.browser.get_iframe('wordframe') as iframe"
      - Without this custom fixture: 5+ seconds!
      - With this fixture: 0.03 seconds

    The times were consistent with various options: headless,
    non, virus scanning on/off, etc.
    """
    chrome_options = ChromeOptions()

    headless = request.config.getoption("--headless")
    if headless:
        chrome_options.add_argument('--headless')  # Enable headless mode

    # Initialize the browser with ChromeOptions
    browser = Browser('chrome', options=chrome_options)

    # Set up and clean up the browser
    def fin():
        browser.quit()
    request.addfinalizer(fin)

    return browser



@pytest.fixture(name='luteclient')
def fixture_lute_client(request, chromebrowser):
    """
    Start the lute browser.
    """
    useport = request.config.getoption("--port")
    if useport is None:
        # Need to specify the port, e.g.
        # pytest tests/acceptance --port=1234
        # Acceptance tests run using 'inv accept' sort this out automatically.
        pytest.exit("--port not set")
    c = LuteTestClient(chromebrowser, f'http://localhost:{useport}/')
    yield c
