"""
Verification that Lute is running correctly.

Used in github actions to verify running app.

Usage:

python -m utils.verify
"""

import json
import requests
from lute.config.app_config import AppConfig


def verify():
    """
    Check the /info page.
    """

    app_config = AppConfig.create_from_config()
    port = app_config.port
    url = f"http://localhost:{port}/info"
    resp = requests.get(url, timeout=5)
    c = resp.status_code

    if c != 200:
        raise RuntimeError(f"Code {c} for url {url}")

    print("Lute is running:")
    print(json.dumps(resp.json(), indent=2))


if __name__ == "__main__":
    verify()
