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
        (["a", "b", "c", "d"],
         "b",
         [["b", 1]]),

        # Case doesn't matter
        (["A", "B", "C", "D"],
         "b",
         [["B", 1]]),  # The original case is returned

        (["a", "b", "c", "d"],
         "B",
         [["b", 1]]),  # Original case returned

        (["a", "bb", "c", "d"],
         "B",
         []),  # No match

        (["b", "b", "c", "d"],
         "b",
         [["b", 0], ["b", 1]]),  # Found in multiple places

        (["b", "B", "b", "d"],
         f"b{zws}b",
         [[f"b{zws}B", 0], [f"B{zws}b", 1]]),  # Multiword, found in multiple

        (["b", "B", "c", "b", "b", "x", "b"],
         f"b{zws}b",
         [[f"b{zws}B", 0], [f"b{zws}b", 3]]),  # Multiword, found in multiple

        (["a", " ", "cat", " ", "here"],
         "cat",
         [["cat", 2]]),

        (["a", " ", "CAT", " ", "here"],
         "cat",
         [["CAT", 2]]),

        (["a", " ", "CAT", " ", "here"],
         "ca",
         []),  # No match

        (["b", "b", "c", "d"],
         "x",
         []),  # No match
    ]

    casenum = 0
    for tokens, word, expected in cases:
        casenum += 1
        sentence = TokenLocator.make_string(tokens)
        tocloc = TokenLocator(english, sentence)
        actual = tocloc.locate_string(word)
        msg = f"case {casenum} - tokens: {', '.join(tokens)}; word: {word}"
        assert actual == expected, msg
