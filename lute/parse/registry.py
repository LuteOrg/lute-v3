"""
Parser registry.

List of available parsers.
"""

from lute.parse.base import AbstractParser
from lute.parse.space_delimited_parser import SpaceDelimitedParser, TurkishParser
from lute.parse.mecab_parser import JapaneseParser
from lute.parse.character_parser import ClassicalChineseParser


# List of ALL parsers available, not necessarily all supported.
# This design feels fishy, but it suffices for now.
parsers = {
    "spacedel": SpaceDelimitedParser,
    "turkish": TurkishParser,
    "japanese": JapaneseParser,
    "classicalchinese": ClassicalChineseParser,
}


def _supported_parsers():
    "Get the supported parsers."
    ret = {}
    for k, v in parsers.items():
        if v.is_supported():
            ret[k] = v
    return ret


def get_parser(parser_name) -> AbstractParser:
    "Return the supported parser with the given name."
    if parser_name in _supported_parsers():
        pclass = parsers[parser_name]
        return pclass()
    raise ValueError(f"Unknown parser type '{parser_name}'")


def is_supported(parser_name) -> bool:
    "Return True if the specified parser is supported, false otherwise or if not found."
    if parser_name not in parsers:
        return False
    p = parsers[parser_name]
    return p.is_supported()


def supported_parsers():
    """
    Dictionary of supported parser strings and class names, for UI.

    For select list entries, use supported_parsers().items().
    """
    ret = []
    for k, v in _supported_parsers().items():
        ret.append([k, v.name()])
    return ret


def supported_parser_types():
    """
    List of supported Language.parser_types
    """
    return list(_supported_parsers().keys())
