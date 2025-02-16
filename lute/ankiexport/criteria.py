"""
Criteria.  Given a string with selection criteria, evaluates it
with a term, returning True or False.
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
from pyparsing.exceptions import ParseException
from lute.models.term import Term
from lute.models.language import Language
from lute.ankiexport.exceptions import AnkiExportConfigurationError


def evaluate_criteria(s, term):
    "Parse the criteria, return True or False for the given term."
    # pylint: disable=too-many-locals

    if (s or "").strip() == "":
        return True

    def has_any_matching_tags(tagvals):
        term_tags = [t.text for t in term.term_tags]
        return any(e in term_tags for e in tagvals)

    def has_any_matching_parent_tags(tagvals):
        ptags = []
        for p in term.parents:
            ptags.extend([t.text for t in p.term_tags])
        return any(e in ptags for e in tagvals)

    def has_any_matching_all_tags(tagvals):
        alltags = [t.text for t in term.term_tags]
        for p in term.parents:
            alltags.extend([t.text for t in p.term_tags])
        return any(e in alltags for e in tagvals)

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

    def get_binary_operator(opstring):
        "Return lambda matching op."
        opMap = {
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
            "!=": lambda a, b: a != b,
            "=": lambda a, b: a == b,
            "==": lambda a, b: a == b,
        }
        return opMap[opstring]

    def check_parent_count(args):
        "Check parents."
        opstring, val = args
        oplambda = get_binary_operator(opstring)
        pcount = len(term.parents)
        return oplambda(pcount, val)

    def check_status_val(args):
        "Check status."
        opstring, val = args
        oplambda = get_binary_operator(opstring)
        return oplambda(term.status, val)

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

    tag_matcher = Suppress(Literal("tags") + Literal(":")) + tagcrit
    parents_tag_matcher = Suppress(Literal("parents.tags") + Literal(":")) + tagcrit
    all_tag_matcher = Suppress(Literal("all.tags") + Literal(":")) + tagcrit

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

    status_matcher = Suppress("status") + comparison_op + integer

    and_keyword = Keyword("and")
    or_keyword = Keyword("or")

    multi_check = infixNotation(
        tag_matcher.set_parse_action(has_any_matching_tags)
        | parents_tag_matcher.set_parse_action(has_any_matching_parent_tags)
        | all_tag_matcher.set_parse_action(has_any_matching_all_tags)
        | lang_matcher.set_parse_action(matches_lang)
        | has_matcher.set_parse_action(check_has)
        | parent_count_matcher.set_parse_action(check_parent_count)
        | status_matcher.set_parse_action(check_status_val),
        [
            (and_keyword, 2, opAssoc.LEFT, BoolAnd),
            (or_keyword, 2, opAssoc.LEFT, BoolOr),
        ],
    )

    try:
        result = multi_check.parseString(s, parseAll=True)
        return bool(result[0])
    except pp.ParseException as ex:
        msg = f"Criteria syntax error at position {ex.loc} or later: {ex.line}"
        raise AnkiExportConfigurationError(msg) from ex


def validate_criteria(criteria):
    "Check criteria with a dummy Term."
    term = Term(Language(), "")
    try:
        evaluate_criteria(criteria, term)
    except ParseException as ex:
        msg = f'Invalid criteria "{ex.line}"'
        raise AnkiExportConfigurationError(msg) from ex
