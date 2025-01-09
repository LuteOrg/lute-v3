"""
token_group_iterator tests.
"""

from lute.book.model import token_group_generator
from lute.parse.space_delimited_parser import SpaceDelimitedParser


def toks_to_string(tokens):
    ret = "".join([t.token for t in tokens])
    return ret.replace("¶", "\n").strip()


def test_paragraph_scenarios(english):
    """
    Given a string and the max token count,
    generator should return expected groups.
    """

    def scenario(s, threshold, expected_groups):
        parser = SpaceDelimitedParser()
        tokens = parser.get_parsed_tokens(s, english)
        # pylint: disable=unnecessary-comprehension
        groups = [g for g in token_group_generator(tokens, "paragraphs", threshold)]
        print(groups, flush=True)
        gs = [toks_to_string(g) for g in groups]
        expected = "||".join(expected_groups)
        assert "||".join(gs) == expected, f"groups for size {threshold}"

    scenario("", 100, [""])

    scenario("Here is a dog. Here is a cat.", 100, ["Here is a dog. Here is a cat."])
    scenario("Here is a dog. Here is a cat.", 3, ["Here is a dog. Here is a cat."])
    scenario("Here is a dog. Here is a cat", 6, ["Here is a dog. Here is a cat"])
    scenario("Here is a dog Here is a cat", 6, ["Here is a dog Here is a cat"])

    p1 = "Here is a dog."
    p2 = "And a cat."
    src = "\n".join([p1, p2])
    scenario(src, 100, [src])
    scenario(src, 5, [src])
    scenario(src, 3, [p1, p2])
    scenario(src.replace("\n", "\n\n\n"), 3, [p1, p2])

    p1 = "Here is a dog."
    p2 = "Here is a cat. Much more info here, long paragraph."
    p3 = "Last stuff."
    src = "\n".join([p1, p2, p3])
    scenario(src, 100, [src])
    scenario(src, 5, [f"{p1}\n{p2}", p3])
    scenario(src, 3, [p1, p2, p3])

    src = "\n" + "\n\n\n".join([p1, p2, p3]) + "\n"
    scenario(src, 5, [f"{p1}\n\n\n{p2}", p3])


def test_sentence_scenarios(english):
    """
    Given a string and the max token count,
    generator should return expected groups.
    """

    def scenario(s, threshold, expected_groups):
        parser = SpaceDelimitedParser()
        tokens = parser.get_parsed_tokens(s, english)
        # pylint: disable=unnecessary-comprehension
        groups = [g for g in token_group_generator(tokens, "sentences", threshold)]
        gs = [toks_to_string(g) for g in groups]
        expected = "||".join(expected_groups)
        assert "||".join(gs) == expected, f"groups for size {threshold}"

    scenario("", 100, [""])

    text = "Here is a dog. Here is a cat."

    scenario(text, 100, ["Here is a dog. Here is a cat."])

    scenario(text, 3, ["Here is a dog.", "Here is a cat."])

    scenario(text, 6, ["Here is a dog. Here is a cat."])

    # No period at the end.
    scenario("Here is a dog. Here is a cat", 6, ["Here is a dog. Here is a cat"])

    # No period at all.
    scenario("Here is a dog Here is a cat", 6, ["Here is a dog Here is a cat"])

    s1 = "Here is a dog."
    s2 = "Here is a cat."
    s3 = "Here is a thing."
    src = " ".join([s1, s2, s3])
    scenario(src, 10, [src])
    scenario(src, 7, [f"{s1} {s2}", s3])
    scenario(src, 3, [s1, s2, s3])
