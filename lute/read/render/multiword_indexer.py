"""
Find terms in contest string using ahocorapy.
"""

from ahocorapy.keywordtree import KeywordTree


class MultiwordTermIndexer:
    """
    Find terms in strings using ahocorapy.
    """

    zws = "\u200B"  # zero-width space

    def __init__(self):
        self.kwtree = KeywordTree(case_insensitive=True)
        self.finalized = False

    def add(self, t):
        "Add zws-enclosed term to tree."
        add_t = f"{self.zws}{t}{self.zws}"
        self.kwtree.add(add_t)

    def search_all(self, lc_tokens):
        "Find all terms and starting token index."
        if not self.finalized:
            self.kwtree.finalize()
            self.finalized = True

        zws = self.zws
        content = zws + zws.join(lc_tokens) + zws
        zwsindexes = [i for i, char in enumerate(content) if char == zws]
        results = self.kwtree.search_all(content)

        for result in results:
            # print(f"{result}\n", flush=True)
            t = result[0].strip(zws)
            charpos = result[1]
            index = zwsindexes.index(charpos)
            yield (t, index)
