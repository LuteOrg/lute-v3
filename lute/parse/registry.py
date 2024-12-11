"""
Parser registry.

List of available parsers.
"""

from importlib.metadata import entry_points
from sys import version_info

from lute.parse.base import AbstractParser
from lute.parse.space_delimited_parser import SpaceDelimitedParser, TurkishParser
from lute.parse.mecab_parser import JapaneseParser
from lute.parse.character_parser import ClassicalChineseParser


__LUTE_PARSERS__ = {
    "spacedel": SpaceDelimitedParser,
    "turkish": TurkishParser,
    "japanese": JapaneseParser,
    "classicalchinese": ClassicalChineseParser,
}


def init_parser_plugins():
    """
    Initialize parsers from plugins
    """

    # Handle API breakage of entry_points.
    # pylint: disable=no-member
    vmaj = version_info.major
    vmin = version_info.minor
    if vmaj == 3 and vmin in (8, 9, 10, 11):
        custom_parser_eps = entry_points().get("lute.plugin.parse")
    elif (vmaj == 3 and vmin >= 12) or (vmaj >= 4):
        # Can't be sure this will always work, API may change again,
        # but can't plan for the unforseeable everywhere.
        custom_parser_eps = entry_points().select(group="lute.plugin.parse")
    else:
        # earlier version of python than 3.8?  What madness is this?
        # Not going to throw, just print and hope the user sees it.
        msg = f"Unable to load plugins for python {vmaj}.{vmin}, please upgrade to 3.8+"
        print(msg, flush=True)
        return

    if custom_parser_eps is None:
        return

    for custom_parser_ep in custom_parser_eps:
        name = custom_parser_ep.name
        klass = custom_parser_ep.load()
        if issubclass(klass, AbstractParser):
            __LUTE_PARSERS__[name] = klass
        else:
            raise ValueError(f"{name} is not a subclass of AbstractParser")


def get_parser(parser_name) -> AbstractParser:
    "Return the supported parser with the given name."
    if parser_name not in __LUTE_PARSERS__:
        raise ValueError(f"Unknown parser type '{parser_name}'")
    pclass = __LUTE_PARSERS__[parser_name]
    if not pclass.is_supported():
        raise ValueError(f"Unsupported parser type '{parser_name}'")
    return pclass()


def is_supported(parser_name) -> bool:
    "Return True if the specified parser is present and supported."
    if parser_name not in __LUTE_PARSERS__:
        return False
    p = __LUTE_PARSERS__[parser_name]
    return p.is_supported()


def supported_parsers():
    """
    List of supported parser strings and classes.
    """
    return [(k, v) for k, v in __LUTE_PARSERS__.items() if v.is_supported()]


def supported_parser_types():
    """
    List of supported Language.parser_types
    """
    return list(a[0] for a in supported_parsers())
