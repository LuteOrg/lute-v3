"""
Demo posting a term.

Given term ID, get the term object:

- use selectors to determine what mappings should be used
- then generate the post bodies for anki connect
- do post

> select woid from words where wotextlc = 'kinder';
143771

To run this: from root directory:

python -m iss_579_anki.post_demo

"""

from typing import Callable, Iterable

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

from lute.term.model import Repository
import lute.app_factory
from lute.db import db


def evaluate_selector(s, term):
    "Parse the selector, return True or False for the given term."
    # pylint: disable=too-many-locals

    def has_any_matching_tags(tagvals):
        return any(e in term.term_tags for e in tagvals)

    def matches_lang(lang):
        return term.language_name == lang[0]

    def check_has(args):
        "Check has:x"
        has_item = args[0]
        if has_item == "image":
            return term.current_image is not None
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
    # print(f"{result}, {result[0]}")
    # print(bool(result[0]))
    return bool(result[0])


def get_selected_mappings(mappings, term):
    """
    Get all mappings where the selector is True.
    """
    return [
        m for m in mappings if evaluate_selector(m["selector"], term) and m["active"]
    ]


def run_test():
    "Run test."
    app = lute.app_factory.create_app()
    with app.app_context():
        repo = Repository(db.session)
        t = repo.load(143771)
    print(t)

    all_mapping_data = [
        {
            "name": "Gender",
            "selector": 'language:"German" and tags:["der", "die", "das"] and has:image',
            "deck_name": "x",
            "note_type": "y",
            "mapping": "z",
            "active": True,
        },
        {
            "name": "Pluralization",
            "selector": (
                'language:"German" and parents.count = 1 '
                + 'and has:image and tags:["plural", "plural and singular"]'
            ),
            "deck_name": "x",
            "note_type": "y",
            "mapping": "z",
            "active": True,
        },
        {
            "name": "m3",
            "selector": "sel here",
            "deck_name": "x",
            "note_type": "y",
            "mapping": "z",
            "active": False,
        },
    ]

    use_mappings = get_selected_mappings(all_mapping_data, t)
    print(use_mappings)


if __name__ == "__main__":
    run_test()
