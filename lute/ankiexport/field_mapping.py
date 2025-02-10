"""Field to value mapper.

e.g. given dict like

{
  "lute_term_id": "{ id }",
  "term": "{ term }",
  "tags": "{ tags:["masc", "fem"] }"
}

extracts data from the given term and generates a mapping of field to
actual values to send to AnkiConnect.
"""

import re
import pyparsing as pp
from pyparsing import (
    quotedString,
    Suppress,
)
from pyparsing.exceptions import ParseException
from lute.models.term import Term
from lute.models.language import Language
from lute.ankiexport.exceptions import AnkiExportConfigurationError


def _all_terms(term):
    "Term and any parents."
    ret = [term]
    ret.extend(term.parents)
    return ret


def _all_tags(term):
    "Tags for term and all parents."
    ret = [tt.text for t in _all_terms(term) for tt in t.term_tags]
    return sorted(list(set(ret)))


def get_values_and_media_mapping(term, refsrepo, mapping):
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

        e.g. the mapping "article: { tags["der", "die", "das"] }"
        needs to be parsed to extract certain tags from the current
        term.
        """

        def get_filtered_tags(tagvals):
            "Get term tags matching the list."
            # tagvals is a pyparsing ParseResults, use list() to convert to strings.
            ftags = [tt for tt in _all_tags(term) if tt in list(tagvals)]
            return ", ".join(ftags)

        def handle_image(_):
            id_images = [
                (t, t.get_current_image())
                for t in _all_terms(term)
                if t.get_current_image() is not None
            ]
            image_srcs = []
            for t, imgfilename in id_images:
                new_filename = f"LUTE_TERM_{t.id}.jpg"
                image_url = f"/userimages/{t.language.id}/{imgfilename}"
                media_mappings[new_filename] = image_url
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
    # e.g. "{ id }" is replaced by term.termid.
    replacements = {
        "id": term.id,
        "term": term.text,
        "language": term.language.name,
        "parents": ", ".join([p.text for p in term.parents]),
        "tags": ", ".join(_all_tags(term)),
        "translation": "<br>".join(all_translations()),
    }

    mapping_string = "; ".join(mapping.values())
    calc_keys = [
        k
        for k in set(re.findall(r"{\s*(.*?)\s*}", mapping_string))
        if k not in replacements
    ]

    media_mappings = {}
    calc_replacements = parse_keys_needing_calculation(calc_keys, media_mappings)

    return ({**replacements, **calc_replacements}, media_mappings)


def validate_mapping(mapping):
    "Check mapping with a dummy Term."
    t = Term(Language(), "")
    refsrepo = None
    try:
        get_values_and_media_mapping(t, refsrepo, mapping)
    except ParseException as ex:
        msg = f'Invalid field mapping "{ex.line}"'
        raise AnkiExportConfigurationError(msg) from ex


def get_fields_and_final_values(mapping, replacements):
    "Break mapping string into fields, apply replacements."
    ret = {}
    for fieldname, value in mapping.items():
        subbed_value = value
        for k, v in replacements.items():
            pattern = rf"{{\s*{re.escape(k)}\s*}}"
            subbed_value = re.sub(pattern, f"{v}", subbed_value)
        if subbed_value.strip() != "":
            ret[fieldname.strip()] = subbed_value.strip()
    return ret
