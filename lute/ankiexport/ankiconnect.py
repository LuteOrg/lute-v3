"""
Wrapper methods around AnkiConnect to allow for mocking.
"""

import requests


class AnkiConnectWrapper:
    "Wrapper."

    def __init__(self, anki_connect_url):
        self.anki_connect_url = anki_connect_url

    def _do_post(self, json):
        "Do post, get result."
        ret = requests.post(self.anki_connect_url, json=json, timeout=5)
        return ret.json()

    def is_running(self):
        "True if Anki version check returns data."
        try:
            p = {"action": "version", "version": 6}
            self._do_post(p)
            return True
        except requests.exceptions.ConnectionError:
            return False

    def deck_names(self):
        "Get deck names."
        p = {"action": "deckNames", "version": 6}
        ret = self._do_post(p)
        return ret["result"]

    def note_types(self):
        "Get note types."
        p = {"action": "modelNames", "version": 6}
        ret = self._do_post(p)
        return ret["result"]

    def note_fields(self, note_type):
        "Get valid fields for model."
        p = {
            "action": "modelFieldNames",
            "version": 6,
            "params": {"modelName": note_type},
        }
        ret = self._do_post(p)
        return ret["result"]


if __name__ == "__main__":
    # Sanity check only, assumes ankiconnect running on default port.
    w = AnkiConnectWrapper("http://localhost:8765")
    print("Running -------------------------")
    print(w.is_running())
    print("Deck names -------------------------")
    print(w.deck_names())
    print("Note types -------------------------")
    nt = w.note_types()
    print(nt)
    print("Fields -------------------------")
    for n in nt:
        print(n)
        print(w.note_fields(n))
