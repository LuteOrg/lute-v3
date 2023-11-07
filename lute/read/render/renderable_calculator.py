"""
Calculating what items should be rendered in the browser.
"""

import re
import functools
from lute.models.language import Language
from lute.models.term import Term, Status


class RenderableCalculator:
    """
    Calculating what TextTokens and Terms should be rendered.

    Suppose we had the following TextTokens A-I, with spaces between:

     A B C D E F G H I

    Then suppose we had the following Terms:
      "B C"       (term J)
      "E F G H I" (K)
      "F G"       (L)
      "C D E"     (M)

    Stacking these:

     A B C D E F G H I

      "B C"              (term J)
            "E F G H I"  (term K)
              "F G"      (term L)
        "C D E"          (term M)

    We can say:

    - term J "contains" TextTokens B and C, so B and C should not be rendered.
    - K contains tokens E-I, and also L, so none of those should be rendered.
    - M is _not_ contained by anything else, so it should be rendered.
    """

    def _assert_texttokens_are_contiguous(self, texttokens):
        prevtok = None
        for tok in texttokens:
            if prevtok is not None and prevtok.order != (tok.order - 1):
                mparts = [prevtok.token, prevtok.order, tok.token, tok.order]
                msg = "; ".join(map(str, mparts))
                raise RuntimeError(f"bad token ordering: {msg}")
            prevtok = tok

    def _get_renderable(self, tokenlocator, terms, texttokens):
        """
        Return RenderableCandidates that will **actually be rendered**.

        Method to determine what should be rendered:

        1. Create a "rendered array".  On completion of this algorithm,
        each position in the array will be filled with the ID of the
        RenderableCandidate that should actually appear there (and
        which might hide other candidates).

        2. Start by saying that all the original texttokens will be
        rendered by writing each candidate ID in the rendered array.

        3. Create candidates for all the terms.

        4. Starting with the shortest terms first (fewest text tokens),
        and starting _at the end_ of the string, "write" the candidate
        ID to the output "rendered array", for each token in the candidate.

        At the end of this process, each position in the "rendered array"
        should be filled with the ID of the corresponding candidate
        that will actually appear in that position.  By getting the
        unique IDs and returning just their candidates, we should have
        the list of candidates that would be "visible" on render.

        Applying the above algorithm to the example given in the class
        header:

        We have the following TextTokens A-I, with spaces between:

         a b c d e f g h i

        And the following terms, arranged from shortest to longest:
          "B C"
          "F G"
          "C D E"
          "E F G H I"

        First, terms are created for each individual token in the
        original string:

        A B C D E F G H I

        Then the positions for each of the terms are calculated:

        [A B C D E F G H I]

          "B C"
                  "F G"
            "C D E"
                "E F G H I"

        Then, "writing" terms order by their length, and then by their
        distance from the *end* of the string:

        - "F G" is written first, because it's short, and is nearest
          the end:
          => "A B C D E [F-G] H I"
        - "B C" is next:
          => "A [B-C] D E [F-G] H I"
        - then "C D E":
          => "A [B-C][C-D-E] [F-G] H I"
        then "E F G H I":
          => "A [B-C][C-D-E][E-F-G-H-I]"
        """

        # All the candidates to be considered for rendering.
        candidates = {}

        # Step 1.  Map of the token position to the id of the
        # candidate that should be rendered there.
        rendered = {}

        # Step 2 - fill with the original texttokens.
        for tok in texttokens:
            rc = RenderableCandidate()
            rc.display_text = tok.token
            rc.text = tok.token
            rc.pos = tok.order
            rc.is_word = tok.is_word
            candidates[rc.id] = rc
            rendered[rc.pos] = rc.id

        # 3.  Create candidates for all the terms.
        termcandidates = []

        for term in terms:
            for loc in tokenlocator.locate_string(term.text_lc):
                rc = RenderableCandidate()
                rc.term = term
                rc.display_text = loc["text"]
                rc.text = loc["text"]
                rc.pos = texttokens[0].order + loc["index"]
                rc.length = term.token_count
                rc.is_word = 1

                termcandidates.append(rc)
                candidates[rc.id] = rc

        # 4a.  Sort the term candidates: first by length, then by position.
        def compare(a, b):
            # Longest sorts first.
            if a.length != b.length:
                return -1 if (a.length > b.length) else 1
            # Lowest position (closest to front of string) sorts first.
            return -1 if (a.pos < b.pos) else 1

        termcandidates.sort(key=functools.cmp_to_key(compare))

        # The termcandidates should now be sorted such that longest
        # are first, with items of equal length being sorted by
        # position.  By traversing this in reverse and "writing"
        # their IDs to the "rendered" array, we should end up with
        # the final IDs in each position.
        termcandidates.reverse()
        for tc in termcandidates:
            for i in range(tc.length):
                rendered[tc.pos + i] = tc.id

        rcids = list(set(rendered.values()))
        return [candidates[rcid] for rcid in rcids]

    def _sort_by_order_and_tokencount(self, items):
        items.sort(key=lambda x: (x.pos, -x.length))
        return items

    def _calc_overlaps(self, items):
        for i in range(1, len(items)):
            prev = items[i - 1]
            curr = items[i]

            prevterm_last_token_pos = prev.pos + prev.length - 1
            overlap = prevterm_last_token_pos - curr.pos + 1

            if overlap > 0:
                zws = chr(0x200B)
                curr_tokens = curr.text.split(zws)
                show = curr_tokens[overlap:]
                curr.display_text = zws.join(show)

        return items

    def main(self, language, words, texttokens):
        """
        Main entrypoint.

        Given a language and some terms and texttokens,
        return the RenderableCandidates to be rendered.
        """
        texttokens.sort(key=lambda x: x.order)
        self._assert_texttokens_are_contiguous(texttokens)

        subject = TokenLocator.make_string([t.token for t in texttokens])
        tocloc = TokenLocator(language, subject)

        renderable = self._get_renderable(tocloc, words, texttokens)
        items = self._sort_by_order_and_tokencount(renderable)
        items = self._calc_overlaps(items)
        return items

    @staticmethod
    def get_renderable(lang, words, texttokens):
        "Convenience method, calls main."
        rc = RenderableCalculator()
        return rc.main(lang, words, texttokens)


class RenderableCandidate:  # pylint: disable=too-many-instance-attributes
    """
    An item that may or may not be rendered on the browser.

    Given some Terms contained in a text, the RenderableCalculator
    creates RenderableCandidates for each Term in the text, as well as
    the original text tokens.

    When the final set of actually rendered RenderableCandidates is
    found (with self.render is True), these are convered into TextItems
    for the final render.
    """

    # ID incremented for each instance.
    class_id = 0

    def __init__(self):
        RenderableCandidate.class_id += 1

        self.id: int = RenderableCandidate.class_id
        self.term: Term = None
        self.display_text: str  # Text to show, if there is any overlap
        self.text: str  # Actual text of the term
        self.pos: int
        self.length: int = 1
        self.is_word: int
        self.render: bool = True

    def __repr__(self):
        parts = [f"pos {self.pos}", f"render {self.render}" f"(id {self.id})"]
        parts = " ".join(parts)
        return f'<RenderableCandidate "{self.text}", {parts}>'

    @property
    def term_id(self) -> int:
        return self.term.id if self.term else None

    @property
    def order_end(self) -> int:
        return self.pos + self.length - 1

    def make_text_item(self, p_num: int, se_id: int, text_id: int, lang: Language):
        """
        Create a TextItem for final rendering.
        """
        t = TextItem()
        t.order = self.pos
        t.text_id = text_id
        t.lang_id = lang.id
        t.display_text = self.display_text
        t.text = self.text
        t.token_count = self.length
        t.text_lc = lang.get_lowercase(self.text)
        t.para_id = p_num
        t.se_id = se_id
        t.is_word = self.is_word
        t.text_length = len(self.text)

        t.load_term_data(self.term)

        return t


class TokenLocator:
    """
    Helper class for finding tokens and positions in a subject string.

    Finds a given token (word) in a sentence, ignoring case, returning
    the actual word in the sentence (its original case), and its index
    or indices.

    For example, given:

      - $subject "/this/ /CAT/ /is/ /big/"
      - $find_patt = "/cat/"

    (where "/" is the zero-width space to indicate word boundaries)

    this method would return [ { 'term': "CAT", 'index': 2 } ]
      - the token "cat" is actually "CAT" (uppercase) in the sentence
      - it's at index = 2

    Note that the language of the string must also be provided, because
    some languages (Turkish!) have unusual case requirements.

    See the test cases for more examples.
    """

    def __init__(self, language, subject):
        self.language = language
        self.subject = subject

    def locate_string(self, s):
        """
        Find the string s in the subject self.subject.
        """
        find_lc = self.language.get_lowercase(s)
        find_lc = TokenLocator.make_string(find_lc)

        subjLC = self.language.get_lowercase(self.subject)

        matches = self.preg_match_capture(find_lc, subjLC)

        # The matches were performed with the lowercased subject,
        # because some languages (Turkish!) have funny cases.
        # We need to convert the matched text back to the _original_
        # subject string cases.
        subj = self.subject

        def make_text_index_pair(match):
            matchtext = match[0]  # includes zws at start and end.
            matchlen = len(matchtext)
            matchpos = match[1]

            # print(f"found match \"{matchtext}\" len={matchlen} pos={matchpos}")
            original_subject_text = subj[matchpos : matchpos + matchlen]
            zws = "\u200B"
            t = original_subject_text.lstrip(zws).rstrip(zws)
            index = self.get_count_before(subj, matchpos)
            return {"text": t, "index": index}

        termmatches = list(map(make_text_index_pair, matches))

        return termmatches

    def get_count_before(self, string, pos):
        """
        Count of tokens found in string before position pos.
        """
        zws = "\u200B"
        beforesubstr = string[:pos]
        n = beforesubstr.count(zws)
        return n

    def preg_match_capture(self, find_lc, subject):
        """
        Return the matched text and their start positions in the subject.

        E.g. search for r'cat' in "there is a CAT and a Cat" returns:
        [['CAT', 11], ['Cat', 21]]
        """

        # "(?=())" is required because sometimes the search pattern can
        # overlap -- e.g. _b_b_ has _b_ *twice*.
        # https://stackoverflow.com/questions/5616822/
        #   how-to-use-regex-to-find-all-overlapping-matches
        pattern = rf"(?=({re.escape(find_lc)}))"

        matches = re.finditer(pattern, subject, flags=re.IGNORECASE)

        # Use group(1) to get the match text, because group(0) is a
        # zero-length string.
        result = [[match.group(1), match.start()] for match in matches]
        return result

    @staticmethod
    def make_string(t):
        """
        Append zero-width string to string to simplify/standardize searches.
        """
        zws = "\u200B"
        if isinstance(t, list):
            t = zws.join(t)
        return zws + t + zws


class TextItem:  # pylint: disable=too-many-instance-attributes
    """
    Unit to be rendered.

    Data structure for template read/textitem.html
    """

    def __init__(self):
        self.text_id: int
        self.lang_id: int
        self.order: int
        self.text: str  # The original, un-overlapped text.
        self.display_text: str  # The actual text to display on screen.
        # If part of the text has been overlapped by a
        # prior token, this will be different from Text.
        self.token_count: int
        self.text_lc: str
        self.para_id: int
        self.se_id: int
        self.is_word: int
        self.text_length: int
        # The tooltip should be shown for well-known/ignored TextItems
        # that merit a tooltip. e.g., if there isn't any actual Term
        # entity associated with this TextItem, nothing more is needed.
        # Also, if there is a Term entity but it's mostly empty, a
        # tooltip isn't useful.
        self.show_tooltip: bool = False
        self.wo_id: int = None
        self.wo_status: int = None
        self.flash_message: str = None

    def load_term_data(self, term):
        """
        Load extra term data, if any.
        """
        if term is None:
            return

        self.wo_id = term.id
        self.wo_status = term.status
        self.flash_message = term.get_flash_message()

        def has_extra(cterm):
            if cterm is None:
                return False
            no_extra = (
                cterm.translation is None
                and cterm.romanization is None
                and cterm.get_current_image() is None
            )
            return not no_extra

        show_tooltip = has_extra(term)
        for p in term.parents:
            show_tooltip = show_tooltip or has_extra(p)
        self.show_tooltip = show_tooltip

    @property
    def html_display_text(self):
        """
        Content to be rendered to browser.
        """
        zws = chr(0x200B)
        return self.display_text.replace(zws, "").replace(" ", "&nbsp;")

    @property
    def span_id(self):
        """
        Each span gets a unique id.
        Arbitrary format: ID-{order}-{tokencount}.

        This *might* not be necessary ... I don't think IDs are used anywhere.
        """
        parts = ["ID", str(self.order), str(max(1, self.token_count))]
        return "-".join(parts)

    @property
    def html_class_string(self):
        """
        Create class string for TextItem.
        """
        if self.is_word == 0:
            return "textitem"

        if self.wo_id is None:
            classes = ["textitem", "click", "word", "status0"]
            return " ".join(classes)

        st = self.wo_status
        classes = [
            "textitem",
            "click",
            "word",
            "word" + str(self.wo_id),
            "status" + str(st),
        ]

        tooltip = (
            st not in (Status.WELLKNOWN, Status.IGNORED)
            or self.show_tooltip
            or self.flash_message is not None
        )
        if tooltip:
            classes.append("showtooltip")

        if self.flash_message is not None:
            classes.append("hasflash")

        if self.display_text != self.text:
            classes.append("overlapped")

        return " ".join(classes)
