"""
SentenceGroupIterator tests.
"""

from lute.parse.base import SentenceGroupIterator
from lute.parse.space_delimited_parser import SpaceDelimitedParser


def toks_to_string(tokens):
    return "".join([t.token for t in tokens])


def test_sgi_scenarios(english):
    """
    Given a string and the max token count,
    SentenceGroupIterator should return expected groups.
    """

    def scenario(s, maxcount, expected_groups):
        parser = SpaceDelimitedParser()
        tokens = parser.get_parsed_tokens(s, english)

        it = SentenceGroupIterator(tokens, maxcount)
        groups = []
        while g := it.next():
            groups.append(g)
        gs = [toks_to_string(g) for g in groups]
        assert "||".join(gs) == "||".join(
            expected_groups
        ), f"groups for size {maxcount}"

    scenario("", 100, [""])

    text = "Here is a dog. Here is a cat."

    scenario(text, 100, ["Here is a dog. Here is a cat."])

    scenario(text, 3, ["Here is a dog. ", "Here is a cat."])

    scenario(text, 6, ["Here is a dog. ", "Here is a cat."])

    # No period at the end.
    scenario("Here is a dog. Here is a cat", 6, ["Here is a dog. ", "Here is a cat"])

    # No period at all.
    scenario("Here is a dog Here is a cat", 6, ["Here is a dog Here is a cat"])

    scenario(
        "Here is a dog. Here is a cat. Here is a thing.",
        10,
        ["Here is a dog. Here is a cat. ", "Here is a thing."],
    )
