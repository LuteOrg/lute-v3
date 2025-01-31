"Mapping field demo."

import json
import re
import requests
import pyparsing as pp
from pyparsing import (
    quotedString,
    Suppress,
)


def build_ankiconnect_post_json(
    term, mapping_string, img_root_dir, deck_name, model_name
):
    "Build post json for term using the mappings."

    def get_filtered_tags(tagvals):
        "Get tags matching the spec."
        # tagvals is a pyparsing ParseResults, convert to strings.
        real_tagvals = list(tagvals)
        ftags = [t for t in term.tags if t in real_tagvals]
        # print(f"got filtered tags {ftags}")
        return ", ".join(ftags)

    # List of ankiconnect "media actions" (file uploads) to execute.
    # Appended to during handle_image().
    media_actions = []

    def handle_image(_):
        if term.image is None:
            return ""

        # print(f"handling image with args: {args}")
        new_filename = f"LUTE_TERM_{term.termid}.jpg"
        hsh = {"filename": new_filename, "path": img_root_dir + term.image}
        media_actions.append(hsh)
        return f'<img src="{new_filename}">'

    quotedString.setParseAction(pp.removeQuotes)
    tag_matcher = (
        Suppress("tags")
        + Suppress("[")
        + pp.delimitedList(quotedString)
        + Suppress("]")
    )
    image_matcher = Suppress("image")

    matcher = tag_matcher.set_parse_action(
        get_filtered_tags
    ) | image_matcher.set_parse_action(handle_image)

    pattern = r"{{\s*(.*?)\s*}}"
    keys = set(re.findall(pattern, mapping_string))

    # One-for-one replacements in the mapping string.
    # e.g. "{{ id }}" is replaced by term.termid.
    replacements = {
        "id": term.termid,
        "term": term.text,
        "language": term.language,
        "parents": ", ".join(term.parents),
        "tags": ", ".join(term.tags),
        "translation": term.translation,
    }

    calc_replacements = {
        k: matcher.parseString(k).asList()[0] for k in keys if k not in replacements
    }
    # print(calc_replacements)

    replacements = {**replacements, **calc_replacements}

    final = mapping_string
    for k, v in replacements.items():
        pattern = rf"{{{{\s*{re.escape(k)}\s*}}}}"
        final = re.sub(pattern, f"{v}", final)

    postjson = {}
    mappings = [s.strip() for s in final.split("\n") if s.strip() != ""]
    for s in mappings:
        # print(f"handling '{s}'")
        field, val = s.split(":", 1)
        postjson[field.strip()] = val.strip()

    # print("=" * 25)
    # print(final)
    # print("=" * 25)
    # print(postjson)
    # print("=" * 25)
    # print(media_actions)
    # print("=" * 25)

    all_actions = [{"action": "storeMediaFile", "params": p} for p in media_actions]
    all_actions.append(
        {
            "action": "addNote",
            "params": {
                "note": {
                    "deckName": deck_name,
                    "modelName": model_name,
                    "fields": postjson,
                    "tags": ["lute"] + term.tags,
                }
            },
        }
    )

    return {"action": "multi", "params": {"actions": all_actions}}


class Term:
    "Stub term class."

    def __init__(self):
        self.termid = None
        self.language = None
        self.text = None
        self.tags = []
        self.parents = []
        self.image = None
        self.translation = None


the = Term()
the.termid = 43
the.text = "aucher"
the.language = "German"
the.parents = ["hello", "there"]
the.translation = 'also "here"'
the.tags = ["der", "blah", "xxx", "yyy"]
# TODO - need to fix this URL trash stored in the table, should just store the filename
the.image = "/userimages/3/Geschenk.jpeg"

# images served from userimages in app_config
IMAGE_ROOT_DIR = "/Users/jeff/Documents/Projects/lute/data"

test_string = """\
Extra_info_back: {{ id }}
Word: {{ term }}
Plural: some value {{ parents }}
Article: {{ tags["der", "die", "das"] }}: {{ term }}
Picture: {{ image }}
Sentence: some text {{ parents }} more text {{ parents }}
Definition: {{ translation }}
"""

p = build_ankiconnect_post_json(
    the, test_string, IMAGE_ROOT_DIR, "zzTestAnkiConnect", "Basic_vocab"
)
print("=" * 25)
print(json.dumps(p, indent=2))
print("=" * 25)


do_post = False
if do_post:
    ANKI_CONNECT_URL = "http://localhost:8765"
    ret = requests.post(ANKI_CONNECT_URL, json=p, timeout=5)
    rj = ret.json()
    print(rj)
