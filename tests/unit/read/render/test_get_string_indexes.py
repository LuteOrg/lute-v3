"""
get_string_indexes tests.
"""

from lute.read.render.calculate_textitems import get_string_indexes


def test_get_string_indexes_scenario(english):
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
        (["a", "b", "c", "d"], "b", [("b", 1)]),
        # Case doesn't matter
        # The original case is returned
        (["A", "B", "C", "D"], "b", [("b", 1)]),
        # Original case returned
        (["a", "b", "c", "d"], "B", [("b", 1)]),
        # No match
        (["a", "bb", "c", "d"], "B", []),
        # Found in multiple places
        (
            ["b", "b", "c", "d"],
            "b",
            [("b", 0), ("b", 1)],
        ),
        # Multiword, found in multiple
        (
            ["b", "B", "b", "d"],
            f"b{zws}b",
            [(f"b{zws}b", 0), (f"b{zws}b", 1)],
        ),
        # Multiword, found in multiple
        (
            ["b", "B", "c", "b", "b", "x", "b"],
            f"b{zws}b",
            [(f"b{zws}b", 0), (f"b{zws}b", 3)],
        ),
        (["a", " ", "cat", " ", "here"], "cat", [("cat", 2)]),
        (["a", " ", "CAT", " ", "here"], "cat", [("cat", 2)]),
        # No match
        (["a", " ", "CAT", " ", "here"], "ca", []),
        # No match
        (["b", "b", "c", "d"], "x", []),
    ]

    casenum = 0
    for tokens, word, expected in cases:
        casenum += 1
        p = english.parser
        sentence = p.get_lowercase(zws.join(tokens))
        actual = get_string_indexes([p.get_lowercase(word)], sentence)
        msg = f"case {casenum} - tokens: {', '.join(tokens)}; word: {word}"
        assert actual == expected, msg
