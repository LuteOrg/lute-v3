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
    if parser_name in parsers:
        return parsers[parser_name]()
    else:
        raise ValueError(f"Unknown parser type '{parser_name}'")


def available_parsers():
    ret = {}
    for k in parsers:
        n = parsers[k]().name
        ret[k] = n
    return ret
