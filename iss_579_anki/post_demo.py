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
from typing import Callable, Iterable
from dataclasses import dataclass
import json
import requests
import pyparsing as pp
from pyparsing import (
    infixNotation,
    opAssoc,
    Keyword,
    Word,
    # ParserElement,
    nums,
    one_of,
    quotedString,
    QuotedString,
    Suppress,
    Literal,
)
from pyparsing.exceptions import ParseException

from lute.models.term import Term
from lute.models.language import Language
from lute.models.repositories import TermRepository
from lute.term.model import ReferencesRepository
import lute.app_factory
from lute.db import db


IMAGE_ROOT_DIR = "/Users/jeff/Documents/Projects/lute-v3/data/userimages"
ANKI_CONNECT_URL = "http://localhost:8765"


class AnkiExportConfigurationError(Exception):
    """
    Raised if the config for the export is bad.
    """


def verify_all_anki_models_exists(model_names):
    "Throws if some anki models don't exist."
    p = {"action": "modelNames", "version": 6}
    ret = requests.post(ANKI_CONNECT_URL, json=p, timeout=5)
    rj = ret.json()
    # print(rj)
    existing_model_names = rj["result"]
    bad_model_names = [m for m in model_names if m not in existing_model_names]
    if len(bad_model_names) != 0:
        raise AnkiExportConfigurationError(
            f"Bad model names: {', '.join(bad_model_names)}"
        )


@dataclass
class FieldMappingData:
    "Data class"
    fieldname: str = None
    value: str = None
    processed_value: str = None


def mapping_as_array(field_mapping):
    """
    Given "a: {{ somefield }}", returns
    [ ("a", "{{ somefield }}") ]

    Raises config error if dup fields.
    """
    ret = []
    lines = [
        s.strip()
        for s in field_mapping.split("\n")
        if s.strip() != "" and not s.strip().startswith("#")
    ]
    for lin in lines:
        parts = lin.split(":", 1)
        if len(parts) != 2:
            raise AnkiExportConfigurationError(f'Bad mapping line "{lin}" in mapping')
        field, val = parts
        if field in [fmd.fieldname for fmd in ret]:
            raise AnkiExportConfigurationError(f"Dup field {field} in mapping")
        fmd = FieldMappingData()
        fmd.fieldname = field
        fmd.value = val
        ret.append(fmd)
    return ret


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


def evaluate_selector(s, term):
    "Parse the selector, return True or False for the given term."
    # pylint: disable=too-many-locals

    print(f"selector: {s}")

    def has_any_matching_tags(tagvals):
        term_tags = [t.text for t in term.term_tags]
        return any(e in term_tags for e in tagvals)

    def matches_lang(lang):
        return term.language.name == lang[0]

    def check_has_images():
        "True if term or any parent has image."
        pi = [p.get_current_image() is not None for p in term.parents]
        return term.get_current_image() is not None or any(pi)

    def check_has(args):
        "Check has:x"
        has_item = args[0]
        if has_item == "image":
            return check_has_images()
        raise RuntimeError(f"Unhandled has check for {has_item}")

    def check_parent_count(args):
        "Check parents."
        opMap = {
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
            "!=": lambda a, b: a != b,
            "=": lambda a, b: a == b,
            "==": lambda a, b: a == b,
        }
        opstring, val = args
        oplambda = opMap[opstring]
        pcount = len(term.parents)
        return oplambda(pcount, val)

    ### class BoolNot:
    ###     "Not unary operator."
    ###     def __init__(self, t):
    ###         self.arg = t[0][1]
    ###     def __bool__(self) -> bool:
    ###         v = bool(self.arg)
    ###         return not v
    ###     def __str__(self) -> str:
    ###         return "~" + str(self.arg)
    ###     __repr__ = __str__

    class BoolBinOp:
        "Binary operation."
        repr_symbol: str = ""
        eval_fn: Callable[[Iterable[bool]], bool] = lambda _: False

        def __init__(self, t):
            self.args = t[0][0::2]

        def __str__(self) -> str:
            sep = f" {self.repr_symbol} "
            return f"({sep.join(map(str, self.args))})"

        def __bool__(self) -> bool:
            return self.eval_fn(bool(a) for a in self.args)

    class BoolAnd(BoolBinOp):
        repr_symbol = "&"
        eval_fn = all

    class BoolOr(BoolBinOp):
        repr_symbol = "|"
        eval_fn = any

    quoteval = QuotedString(quoteChar='"')
    quotedString.setParseAction(pp.removeQuotes)
    list_of_values = pp.delimitedList(quotedString)

    tagvallist = Suppress("[") + list_of_values + Suppress("]")
    tagcrit = tagvallist | quoteval

    tag_matcher = Suppress("tags") + Suppress(":") + tagcrit

    lang_matcher = Suppress("language") + Suppress(":") + quoteval

    has_options = Literal("image")
    has_matcher = Suppress("has") + Suppress(":") + has_options

    comparison_op = one_of("< <= > >= != = == <>")
    integer = Word(nums).setParseAction(lambda x: int(x[0]))

    parent_count_matcher = (
        Suppress("parents")
        + Suppress(".")
        + Suppress("count")
        + comparison_op
        + integer
    )

    and_keyword = Keyword("and")
    or_keyword = Keyword("or")

    multi_check = infixNotation(
        tag_matcher.set_parse_action(has_any_matching_tags)
        | lang_matcher.set_parse_action(matches_lang)
        | has_matcher.set_parse_action(check_has)
        | parent_count_matcher.set_parse_action(check_parent_count),
        [
            (and_keyword, 2, opAssoc.LEFT, BoolAnd),
            (or_keyword, 2, opAssoc.LEFT, BoolOr),
        ],
    )

    result = multi_check.parseString(s)
    print(f"{result}, {result[0]}")
    # print(bool(result[0]))
    return bool(result[0])


# pylint: disable=too-many-arguments,too-many-positional-arguments
def build_ankiconnect_post_json(
    term, refsrepo, mapping_string, img_root_dir, deck_name, model_name
):
    "Build post json for term using the mappings."

    def all_terms():
        "Term and any parents."
        all_terms = [term]
        all_terms.extend(term.parents)
        return all_terms

    def all_tags():
        "Tags for term and all parents."
        ret = [tt.text for t in all_terms() for tt in t.term_tags]
        return list(set(ret))

    def all_translations():
        ret = [term.translation or ""]
        for p in term.parents:
            if p.translation not in ret:
                ret.append(p.translation or "")
        return [r for r in ret if r.strip() != ""]

    def parse_keys_needing_calculation(calculate_keys, post_actions):
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
            ftags = [tt for tt in all_tags() if tt in list(tagvals)]
            return ", ".join(ftags)

        def handle_image(_):
            id_images = [
                (t, t.get_current_image())
                for t in all_terms()
                if t.get_current_image() is not None
            ]
            image_srcs = []
            for t, imgfilename in id_images:
                new_filename = f"LUTE_TERM_{t.id}.jpg"
                image_path = os.path.join(img_root_dir, str(t.language.id), imgfilename)
                hsh = {
                    "action": "storeMediaFile",
                    "params": {
                        "filename": new_filename,
                        "path": image_path,
                    },
                }
                post_actions.append(hsh)
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
        "tags": ", ".join(all_tags()),
        "translation": "<br>".join(all_translations()),
    }

    calc_keys = [
        k
        for k in set(re.findall(r"{{\s*(.*?)\s*}}", mapping_string))
        if k not in replacements
    ]

    post_actions = []
    calc_replacements = parse_keys_needing_calculation(calc_keys, post_actions)

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
                    "fields": get_field_mapping_json(
                        mapping_string, {**replacements, **calc_replacements}
                    ),
                    "tags": ["lute"] + all_tags(),
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
    t = Term(Language(), "")
    refsrepo = None
    try:
        p = build_ankiconnect_post_json(
            t,
            refsrepo,
            m["mapping"],
            IMAGE_ROOT_DIR,
            m["deck_name"],
            m["note_type"],
        )
    except ParseException as ex:
        msg = f'Invalid mapping value "{ex.line}". '
        raise AnkiExportConfigurationError(msg + str(ex))


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

    verify_all_anki_models_exists(m["note_type"] for m in active_mappings)
    for m in active_mappings:
        mapping_array = mapping_as_array(m["mapping"])
        fieldnames = [m.fieldname for m in mapping_array]
        verify_anki_model_fields_exist(m["note_type"], fieldnames)
        verify_valid_mapping_parsing(m)

    kinder = 143771
    kind = 143770
    termids = [kind, kinder]

    app = lute.app_factory.create_app()
    with app.app_context():
        jsons = get_selected_post_data(db.session, termids, all_mapping_data)

    print("=" * 25)
    print(json.dumps(jsons, indent=2))
    print("=" * 25)

    print("\n\nNOT POSTING")
    return
    for p in jsons:
        ret = requests.post(ANKI_CONNECT_URL, json=p, timeout=5)
        rj = ret.json()
        print(rj)


if __name__ == "__main__":
    run_test()
