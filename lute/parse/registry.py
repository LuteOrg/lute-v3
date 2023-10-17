"""
Parser registry.

List of available parsers.
"""

from lute.parse.base import AbstractParser
from lute.parse.space_delimited_parser import SpaceDelimitedParser


parsers = {
    'spacedel': SpaceDelimitedParser
}


def get_parser(parser_name) -> AbstractParser:
    "Return the parser with the given name."
    if parser_name in parsers:
        return parsers[parser_name]()
    raise ValueError(f"Unknown parser type '{parser_name}'")


def available_parsers():
    "Dictionary of parser strings and class names, for UI."
    ret = {}
    for key, cls in parsers.items():
        ret[key] = cls().name
    return ret
