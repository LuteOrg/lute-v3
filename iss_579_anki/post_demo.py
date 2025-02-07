"""
Demo posting a term.

Given term ID, get the term object:

- use selectors to determine what mappings should be used
- then generate the post bodies for anki connect
- do post

> select woid, wolgid, wotext from words where wotextlc in ['kinder', 'kind'];
143771|3|Kinder
143770|3|Kind

To run this: from root directory:

python -m iss_579_anki.post_demo

"""

import json
import requests

import lute.app_factory
from lute.db import db

from lute.ankiexport.service import Service
from lute.ankiexport.routes import _fake_export_specs

ANKI_CONNECT_URL = "http://localhost:8765"
IMAGE_ROOT_DIR = "/Users/jeff/Documents/Projects/lute-v3/data/userimages"


# pylint: disable=too-many-locals
def run_test():
    "Run it."
    active_specs = _fake_export_specs()

    # js would supply these ...
    anki_deck_names = ["zzTestAnkiConnect", "some_other_deck"]
    anki_note_types = {
        "Lute_Basic_vocab": [
            "Back",
            "Definition",
            "Front",
            "Lute_term_id",
            "Picture",
            "Sentence",
        ],
        "note 2": ["a", "b", "c"],
    }

    svc = Service(anki_deck_names, anki_note_types, active_specs)
    validation_results = svc.validate_specs()
    if len(validation_results) != 0:
        print("Errors:")
        print(validation_results)
        return

    kinder = 143771
    kind = 143770
    termids = [kind, kinder]

    app = lute.app_factory.create_app()
    with app.app_context():
        jsons = svc.get_ankiconnect_post_data(termids, db.session)

    print("=" * 25)
    print(json.dumps(jsons, indent=2))
    print("=" * 25)

    # pylint: disable=unreachable
    print("\n\nNOT POSTING")
    return
    for p in jsons:
        ret = requests.post(ANKI_CONNECT_URL, json=p, timeout=5)
        print(ret)


if __name__ == "__main__":
    try:
        run_test()
    except requests.exceptions.ConnectionError as ex:
        print("Anki not running???")
        print(ex)
