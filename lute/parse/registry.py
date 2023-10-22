"""
Parser registry.

List of available parsers.
"""

from lute.parse.base import AbstractParser
from lute.parse.space_delimited_parser import SpaceDelimitedParser, TurkishParser


parsers = {
    'spacedel': SpaceDelimitedParser,
    'turkish': TurkishParser
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
    "Dictionary of supported parser strings and class names, for UI."
    return _supported_parsers()
