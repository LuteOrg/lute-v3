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
import re
import json
import requests
import pyparsing as pp
from pyparsing import (
    quotedString,
    Suppress,
)
from pyparsing.exceptions import ParseException

from lute.models.term import Term
from lute.models.language import Language
from lute.models.repositories import TermRepository
from lute.term.model import ReferencesRepository
import lute.app_factory
from lute.db import db

from lute.ankiexport.selector import evaluate_selector
from lute.ankiexport.mapper import mapping_as_array
from lute.ankiexport.exceptions import AnkiExportConfigurationError


IMAGE_ROOT_DIR = "/Users/jeff/Documents/Projects/lute-v3/data/userimages"
ANKI_CONNECT_URL = "http://localhost:8765"


def anki_is_running():
    "True if Anki version check returns data."
    try:
        p = {"action": "version", "version": 6}
        requests.post(ANKI_CONNECT_URL, json=p, timeout=5)
        return True
    except requests.exceptions.ConnectionError:
        return False


def validate_mapping(m):
    "Check that the mapping is good."
    verify_anki_model_exists(m["note_type"])
    verify_anki_deck_exists(m["deck_name"])
    mapping_array = mapping_as_array(m["mapping"])
    fieldnames = [m.fieldname for m in mapping_array]
    verify_anki_model_fields_exist(m["note_type"], fieldnames)
    verify_valid_mapping_parsing(m)


def _verify_anki_item_exists(p, name, category_name):
    "Check collection contains the given name."
    ret = requests.post(ANKI_CONNECT_URL, json=p, timeout=5)
    rj = ret.json()
    if name not in rj["result"]:
        msg = f"Bad {category_name}: {name}"
        raise AnkiExportConfigurationError(msg)


def verify_anki_model_exists(model_name):
    "Throws if some anki models don't exist."
    p = {"action": "modelNames", "version": 6}
    _verify_anki_item_exists(p, model_name, "note type")


def verify_anki_deck_exists(deck_name):
    "Throws if some anki decks don't exist."
    p = {"action": "deckNames", "version": 6}
    _verify_anki_item_exists(p, deck_name, "deck name")


def verify_anki_model_fields_exist(model_name, fieldnames):
    "Throws if some anki models don't exist."
    p = {"action": "modelFieldNames", "version": 6, "params": {"modelName": model_name}}
    ret = requests.post(ANKI_CONNECT_URL, json=p, timeout=5)
    rj = ret.json()
    # print(rj)
    existing_field_names = rj["result"]
    bad_field_names = [f for f in fieldnames if f not in existing_field_names]
    if len(bad_field_names) != 0:
        raise AnkiExportConfigurationError(
            f"Bad field names: {', '.join(bad_field_names)}"
        )


def all_terms(term):
    "Term and any parents."
    ret = [term]
    ret.extend(term.parents)
    return ret


def all_tags(term):
    "Tags for term and all parents."
    ret = [tt.text for t in all_terms(term) for tt in t.term_tags]
    return list(set(ret))


# pylint: disable=too-many-arguments,too-many-positional-arguments
def get_values_and_media_mapping(term, refsrepo, mapping_string):
    """
    Get the value replacements to be put in the mapping, and build
    dict of new filenames to original filenames.
    """

    def all_translations():
        ret = [term.translation or ""]
        for p in term.parents:
            if p.translation not in ret:
                ret.append(p.translation or "")
        return [r for r in ret if r.strip() != ""]

    def parse_keys_needing_calculation(calculate_keys, media_mappings):
        """
        Build a parser for some keys in the mapping string, return
        calculated value to use in the mapping.  SIDE EFFECT:
        adds ankiconnect post actions to post_actions if needed
        (e.g. for image uploads).

        e.g. the mapping "article: {{ tags["der", "die", "das"] }}"
        needs to be parsed to extract certain tags from the current
        term.
        """

        def get_filtered_tags(tagvals):
            "Get term tags matching the list."
            # tagvals is a pyparsing ParseResults, use list() to convert to strings.
            ftags = [tt for tt in all_tags(term) if tt in list(tagvals)]
            return ", ".join(ftags)

        def handle_image(_):
            id_images = [
                (t, t.get_current_image())
                for t in all_terms(term)
                if t.get_current_image() is not None
            ]
            image_srcs = []
            for t, imgfilename in id_images:
                new_filename = f"LUTE_TERM_{t.id}.jpg"
                image_path = os.path.join(str(t.language.id), imgfilename)
                media_mappings[new_filename] = image_path
                image_srcs.append(f'<img src="{new_filename}">')

            return "".join(image_srcs)

        def handle_sentences(_):
            "Get sample sentence for term."
            if term.id is None:
                # Dummy parse.
                return ""
            refs = refsrepo.find_references_by_id(term.id)
            term_refs = refs["term"] or []
            if len(term_refs) == 0:
                return ""
            return term_refs[0].sentence

        quotedString.setParseAction(pp.removeQuotes)
        tag_matcher = (
            Suppress("tags")
            + Suppress(":")
            + Suppress("[")
            + pp.delimitedList(quotedString)
            + Suppress("]")
        )
        image = Suppress("image")
        sentence = Suppress("sentence")

        matcher = (
            tag_matcher.set_parse_action(get_filtered_tags)
            | image.set_parse_action(handle_image)
            | sentence.set_parse_action(handle_sentences)
        )

        calc_replacements = {
            # Matchers return the value that should be used as the
            # replacement value for the given mapping string.  e.g.
            # tags["der", "die"] returns "der" if term.tags = ["der", "x"]
            k: matcher.parseString(k).asList()[0]
            for k in calculate_keys
        }

        return calc_replacements

    # One-for-one replacements in the mapping string.
    # e.g. "{{ id }}" is replaced by term.termid.
    replacements = {
        "id": term.id,
        "term": term.text,
        "language": term.language.name,
        "parents": ", ".join([p.text for p in term.parents]),
        "tags": ", ".join(all_tags(term)),
        "translation": "<br>".join(all_translations()),
    }

    calc_keys = [
        k
        for k in set(re.findall(r"{{\s*(.*?)\s*}}", mapping_string))
        if k not in replacements
    ]

    media_mappings = {}
    calc_replacements = parse_keys_needing_calculation(calc_keys, media_mappings)

    return ({**replacements, **calc_replacements}, media_mappings)


# pylint: disable=too-many-arguments,too-many-positional-arguments
def build_ankiconnect_post_json(
    term, refsrepo, mapping_string, img_root_dir, deck_name, model_name
):
    "Build post json for term using the mappings."

    replacements, media_mappings = get_values_and_media_mapping(
        term, refsrepo, mapping_string
    )

    post_actions = []
    for new_filename, original_file in media_mappings.items():
        orig_full_path = os.path.join(img_root_dir, original_file)
        hsh = {
            "action": "storeMediaFile",
            "params": {
                "filename": new_filename,
                "path": orig_full_path,
            },
        }
        post_actions.append(hsh)

    def get_field_mapping_json(map_string, replacements):
        "Apply the replacements in the mapping string, return field: value json."
        mapping = mapping_as_array(map_string)
        postjson = {}
        for m in mapping:
            value = m.value
            for k, v in replacements.items():
                pattern = rf"{{{{\s*{re.escape(k)}\s*}}}}"
                value = re.sub(pattern, f"{v}", value)
            postjson[m.fieldname] = value.strip()
        return postjson

    post_actions.append(
        {
            "action": "addNote",
            "params": {
                "note": {
                    "deckName": deck_name,
                    "modelName": model_name,
                    "fields": get_field_mapping_json(mapping_string, replacements),
                    "tags": ["lute"] + all_tags(term),
                }
            },
        }
    )

    return {"action": "multi", "params": {"actions": post_actions}}


def get_selected_mappings(mappings, term):
    """
    Get all mappings where the selector is True.
    """
    return [
        m for m in mappings if m["active"] and evaluate_selector(m["selector"], term)
    ]


def get_selected_post_data(db_session, term_ids, all_mapping_data):
    "Run test."
    repo = TermRepository(db_session)
    refsrepo = ReferencesRepository(db_session)
    terms = [repo.find(termid) for termid in term_ids]

    ret = []
    for t in terms:
        print(t)
        use_mappings = get_selected_mappings(all_mapping_data, t)
        for m in use_mappings:
            p = build_ankiconnect_post_json(
                t,
                refsrepo,
                m["mapping"],
                IMAGE_ROOT_DIR,
                m["deck_name"],
                m["note_type"],
            )
            ret.append(p)

    return ret


def verify_valid_mapping_parsing(m):
    "Check mapping with a dummy Term."
    t = Term(Language(), "")
    refsrepo = None
    try:
        build_ankiconnect_post_json(
            t,
            refsrepo,
            m["mapping"],
            IMAGE_ROOT_DIR,
            m["deck_name"],
            m["note_type"],
        )
    except ParseException as ex:
        msg = f'Invalid mapping value "{ex.line}". '
        raise AnkiExportConfigurationError(msg + str(ex)) from ex


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
            validate_mapping(m)
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
        ret = requests.post(ANKI_CONNECT_URL, json=p, timeout=5)
        rj = ret.json()
        print(rj)


if __name__ == "__main__":
    if anki_is_running():
        print("is running")
    else:
        print("not running")

    try:
        run_test()
    except requests.exceptions.ConnectionError as ex:
        print("Anki not running???")
        print(ex)
