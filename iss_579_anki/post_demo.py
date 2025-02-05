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

import os
import json
import requests

from lute.models.repositories import TermRepository
from lute.term.model import ReferencesRepository
import lute.app_factory
from lute.db import db

from lute.ankiexport.selector import evaluate_selector
from lute.ankiexport.mapper import (
    mapping_as_array,
    get_values_and_media_mapping,
    validate_mapping,
    get_fields_and_final_values,
)
from lute.ankiexport.ankiconnect import AnkiConnectWrapper
from lute.ankiexport.exceptions import AnkiExportConfigurationError

ANKI_CONNECT_URL = "http://localhost:8765"
IMAGE_ROOT_DIR = "/Users/jeff/Documents/Projects/lute-v3/data/userimages"

anki_connect = AnkiConnectWrapper(ANKI_CONNECT_URL)


def validate_mapping_and_anki(m):
    "Check that the mapping is good."
    validate_mapping(m["mapping"])
    _verify_anki_model_exists(m["note_type"])
    _verify_anki_deck_exists(m["deck_name"])
    mapping_array = mapping_as_array(m["mapping"])
    fieldnames = [m.fieldname for m in mapping_array]
    _verify_anki_model_fields_exist(m["note_type"], fieldnames)


def _verify_anki_model_exists(model_name):
    "Throws if some anki models don't exist."
    if model_name not in anki_connect.note_types():
        msg = f"Bad note type: {model_name}"
        raise AnkiExportConfigurationError(msg)


def _verify_anki_deck_exists(deck_name):
    "Throws if some anki decks don't exist."
    if deck_name not in anki_connect.deck_names():
        msg = f"Bad deck name: {deck_name}"
        raise AnkiExportConfigurationError(msg)


def _verify_anki_model_fields_exist(model_name, fieldnames):
    "Throws if the model doesn't contain all fields in fieldnames."
    existing_field_names = anki_connect.note_fields(model_name)
    bad_field_names = [f for f in fieldnames if f not in existing_field_names]
    if len(bad_field_names) != 0:
        raise AnkiExportConfigurationError(
            f"Bad field names: {', '.join(bad_field_names)}"
        )


def _all_terms(term):
    "Term and any parents."
    ret = [term]
    ret.extend(term.parents)
    return ret


def _all_tags(term):
    "Tags for term and all parents."
    ret = [tt.text for t in _all_terms(term) for tt in t.term_tags]
    return list(set(ret))


# pylint: disable=too-many-arguments,too-many-positional-arguments
def _build_ankiconnect_post_json(
    mapping_array,
    media_mappings,
    lute_and_term_tags,
    deck_name,
    model_name,
):
    "Build post json for term using the mappings."

    post_actions = []
    for new_filename, original_file in media_mappings.items():
        hsh = {
            "action": "storeMediaFile",
            "params": {
                "filename": new_filename,
                "path": original_file,
            },
        }
        post_actions.append(hsh)

    post_actions.append(
        {
            "action": "addNote",
            "params": {
                "note": {
                    "deckName": deck_name,
                    "modelName": model_name,
                    "fields": {m.fieldname: m.value.strip() for m in mapping_array},
                    "tags": lute_and_term_tags,
                }
            },
        }
    )

    return {"action": "multi", "params": {"actions": post_actions}}


# pylint: disable=too-many-locals
def get_selected_post_data(db_session, term_ids, all_mapping_data):
    "Run test."
    repo = TermRepository(db_session)
    refsrepo = ReferencesRepository(db_session)
    terms = [repo.find(termid) for termid in term_ids]

    ret = []
    for t in terms:
        # print(t)
        use_mappings = [
            m
            for m in all_mapping_data
            if m["active"] and evaluate_selector(m["selector"], t)
        ]
        for m in use_mappings:
            replacements, mmap = get_values_and_media_mapping(t, refsrepo, m["mapping"])
            for k, v in mmap.items():
                mmap[k] = os.path.join(IMAGE_ROOT_DIR, v)
            mapping_array = get_fields_and_final_values(m["mapping"], replacements)
            tags = ["lute"] + _all_tags(t)

            p = _build_ankiconnect_post_json(
                mapping_array,
                mmap,
                tags,
                m["deck_name"],
                m["note_type"],
            )
            ret.append(p)

    return ret


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

    active_mappings = [m for m in all_mapping_data if m["active"]]
    valid_mappings = []
    errors = []
    for m in active_mappings:
        try:
            validate_mapping_and_anki(m)
            valid_mappings.append(m)
        except AnkiExportConfigurationError as ex:
            errors.append([m["name"], ex])
    if len(errors) != 0:
        print(errors)
        return

    kinder = 143771
    kind = 143770
    termids = [kind, kinder]

    app = lute.app_factory.create_app()
    with app.app_context():
        jsons = get_selected_post_data(db.session, termids, valid_mappings)

    print("=" * 25)
    print(json.dumps(jsons, indent=2))
    print("=" * 25)

    # pylint: disable=unreachable
    print("\n\nNOT POSTING")
    return
    for p in jsons:
        ret = anki_connect.post(p)
        print(ret)


if __name__ == "__main__":
    if anki_connect.is_running():
        print("is running")
    else:
        print("not running")

    try:
        run_test()
    except requests.exceptions.ConnectionError as ex:
        print("Anki not running???")
        print(ex)
