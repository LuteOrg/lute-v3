"""
Verification that Lute is running correctly.

Used in github actions to verify running app.

Usage:

python -m utils.verify [port]
"""

import sys
import json
import requests


def verify(port):
    """
    Check the /info page.
    """

    url = f"http://localhost:{port}/info"
    resp = requests.get(url, timeout=5)
    c = resp.status_code

    if c != 200:
        raise RuntimeError(f"Code {c} for url {url}")

    print("Lute is running:")
    print(json.dumps(resp.json(), indent=2))


if __name__ == "__main__":
    useport = None
    if len(sys.argv) == 2:
        useport = sys.argv[1]
    else:
        print("Must supply port as argument")
        sys.exit(1)
    verify(useport)
