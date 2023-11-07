"""
TokenLocator tests.
"""

from lute.read.render.renderable_calculator import TokenLocator


def test_token_locator_scenario(english):
    """
    Run test scenarios.
    """

    zws = "\u200B"
    cases = [
        # Cases are of the following form:
        # ( tokens,
        #   word sought
        #   matches [ [ as_found_in_text, position ], ... ])
        # Finds b
        (["a", "b", "c", "d"], "b", [{"text": "b", "index": 1}]),
        # Case doesn't matter
        # The original case is returned
        (["A", "B", "C", "D"], "b", [{"text": "B", "index": 1}]),
        # Original case returned
        (["a", "b", "c", "d"], "B", [{"text": "b", "index": 1}]),
        # No match
        (["a", "bb", "c", "d"], "B", []),
        # Found in multiple places
        (
            ["b", "b", "c", "d"],
            "b",
            [{"text": "b", "index": 0}, {"text": "b", "index": 1}],
        ),
        # Multiword, found in multiple
        (
            ["b", "B", "b", "d"],
            f"b{zws}b",
            [{"text": f"b{zws}B", "index": 0}, {"text": f"B{zws}b", "index": 1}],
        ),
        # Multiword, found in multiple
        (
            ["b", "B", "c", "b", "b", "x", "b"],
            f"b{zws}b",
            [{"text": f"b{zws}B", "index": 0}, {"text": f"b{zws}b", "index": 3}],
        ),
        (["a", " ", "cat", " ", "here"], "cat", [{"text": "cat", "index": 2}]),
        (["a", " ", "CAT", " ", "here"], "cat", [{"text": "CAT", "index": 2}]),
        # No match
        (["a", " ", "CAT", " ", "here"], "ca", []),
        # No match
        (["b", "b", "c", "d"], "x", []),
    ]

    casenum = 0
    for tokens, word, expected in cases:
        casenum += 1
        sentence = TokenLocator.make_string(tokens)
        tocloc = TokenLocator(english, sentence)
        actual = tocloc.locate_string(word)
        msg = f"case {casenum} - tokens: {', '.join(tokens)}; word: {word}"
        assert actual == expected, msg
