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

from lute.models.srsexport import SrsExportSpec
import lute.app_factory
from lute.db import db

from lute.ankiexport.service import Service

ANKI_CONNECT_URL = "http://localhost:8765"
IMAGE_ROOT_DIR = "/Users/jeff/Documents/Projects/lute-v3/data/userimages"


# pylint: disable=too-many-locals
def run_test():
    "Sample mapping and terms."
    gender_card_mapping = """\
      Lute_term_id: {{ id }}
      Front: {{ term }}: der, die, oder das?
      Picture: {{ image }}
      Definition: {{ translation }}
      Back: {{ tags:["der", "die", "das"] }} {{ term }}
      Sentence: {{ sentence }}
    """

    plural_card_mapping = """\
      Lute_term_id: {{ id }}
      Front: {{ tags:["der", "die", "das"] }} {{ parents }}, plural
      Picture: {{ image }}
      Definition: {{ translation }}
      Back: die {{ term }}
      Sentence: {{ sentence }}
    """

    all_mapping_data = [
        {
            "name": "Gender",
            "selector": 'language:"German" and tags:["der", "die", "das"] and has:image',
            "deck_name": "zzTestAnkiConnect",
            "note_type": "Lute_Basic_vocab",
            "mapping": gender_card_mapping,
            "active": True,
        },
        {
            "name": "Pluralization",
            "selector": (
                'language:"German" and parents.count = 1 '
                + 'and has:image and tags:["plural", "plural and singular"]'
            ),
            "deck_name": "zzTestAnkiConnect",
            "note_type": "Lute_Basic_vocab",
            "mapping": plural_card_mapping,
            "active": True,
        },
        {
            "name": "m3",
            "selector": "sel here",
            "deck_name": "x",
            "note_type": "y",
            "mapping": "some mapping here",
            "active": False,
        },
    ]

    export_specs = []
    for md in all_mapping_data:
        spec = SrsExportSpec()
        spec.id = len(export_specs) + 1
        spec.export_name = md["name"]
        spec.criteria = md["selector"]
        spec.deck_name = md["deck_name"]
        spec.note_type = md["note_type"]
        spec.field_mapping = md["mapping"]
        spec.active = md["active"]
        export_specs.append(spec)

    active_specs = [m for m in export_specs if m.active]

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
