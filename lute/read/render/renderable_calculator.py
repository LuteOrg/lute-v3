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

    def _tokens_to_string(self, texttokens):
        "Convert array of tokens to string for debugging."
        arr = [f"{tok.order}: '{tok.token}'" for tok in texttokens]
        return "\n".join(arr)

    def _assert_texttokens_are_contiguous(self, texttokens):
        "Check ordering."
        prevtok = None
        for tok in texttokens:
            if prevtok is not None and prevtok.order != (tok.order - 1):
                toks = self._tokens_to_string(texttokens)
                msg = f"Order error at pos {prevtok.order}:\n{toks}"
                raise RuntimeError(msg)
            prevtok = tok

    def _get_renderable(
        self, tokenlocator, terms, texttokens
    ):  # pylint: disable=too-many-locals
        """Return RenderableCandidates that will **actually be rendered**.

        Method to determine what should be rendered:

        1. Create candidates for all the terms found in the subject string.

        2. Sort the term candidates: first by length, then by position.

        3. Add candidates for all of the original text tokens at the end of the
        list of candidates.

        4. Now, in *reverse order*, write the candidate IDs to a
        "rendered array". Note we start at the _end_ because
        overlapping multiword terms closer to the front of the string
        should be written _last_, so that they "hide" the start of the
        other multiword terms.

        On completion of this, each position in the array will be
        filled with the ID of the RenderableCandidate that should
        actually appear there (and which might hide other candidates).
        By getting the unique IDs and returning just their candidates,
        we will have the list of candidates that would be "visible" on
        render.

        Applying the above algorithm to the example given in the class
        header:

        We have the following TextTokens A-I, with spaces between:

         a b c d e f g h i

        Step 1:

        Given the following terms:
          "B C"
          "C D E"
          "E F G H I"
          "F G"

        The positions for each of the terms are calculated:

        [A B C D E F G H I]
                "E F G H I"
            "C D E"
          "B C"
                  "F G"

        Step 2: Sorting by length, and then position:

          "E F G H I"
          "C D E"
          "F G"
          "B C"   <<< now at end of list

        Step 3: Add candidates for all other original text tokens:
          "E F G H I"
          "C D E"
          "F G"
          "B C"
          "A"
          "B"
          "C" ... etc through to "H", "I"

        Step 4: "writing" these in reverse order:

          "I": "A B C D E F G H [I]"
          "H": "A B C D E F G [H] [I]"
          ... etc through to "A":
          "A": "[A] [B] [C] [D] [E] [F] [G] [H] [I]"
          "F G": "[A] [B] [C] [D] [E] [F G] [H] [I]"
          "B C": "[A] [B C] [D] [E] [F G] [H] [I]"
          "C D E": "[A] [B C][C D E] [F G] [H] [I]"
          "E F G H I": "[A] [B C][C D E][E F G H I]"

        """

        # 1. Create candidates for all the terms found in the subject
        # string.
        def _candidate_from_term_loc(term, loc):
            rc = RenderableCandidate()
            rc.term = term
            rc.display_text = loc["text"]
            rc.text = loc["text"]
            rc.pos = texttokens[0].order + loc["index"]
            rc.length = term.token_count
            rc.is_word = 1
            return rc

        candidates = [
            _candidate_from_term_loc(term, loc)
            for term in terms
            if term.text_lc in tokenlocator.subjLC
            for loc in tokenlocator.locate_string(term.text_lc)
        ]

        # 2. Sort the term candidates: first by length, then by position.
        def compare(a, b):
            # Longest sorts first.
            if a.length != b.length:
                return -1 if (a.length > b.length) else 1
            # Lowest position (closest to front of string) sorts first.
            return -1 if (a.pos < b.pos) else 1

        candidates.sort(key=functools.cmp_to_key(compare))

        # 3. Add the original tokens at the end of the array.
        def _candidate_from_texttoken(tok):
            rc = RenderableCandidate()
            rc.display_text = tok.token
            rc.text = tok.token
            rc.pos = tok.order
            rc.is_word = tok.is_word
            rc.length = 1
            return rc

        candidates += map(_candidate_from_texttoken, texttokens)

        # 4. Write the ids of the candidates to the rendered array.
        # Later elements in the array are written _first_,
        # because they are lower priority and will be overwritten
        # by earlier ones.
        render_position_to_candidate = {}
        for rc in reversed(candidates):
            for i in range(rc.length):
                render_position_to_candidate[rc.pos + i] = rc.id

        # 5. Get final list of candidates, these will actually be rendered.
        rcids = list(set(render_position_to_candidate.values()))
        id_to_candidate = {}
        for rc in candidates:
            id_to_candidate[rc.id] = rc
        rendered = [id_to_candidate[rcid] for rcid in rcids]

        rendered.sort(key=lambda x: x.pos)
        return rendered

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
        return self._calc_overlaps(renderable)

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
    """

    # ID incremented for each instance.
    class_id = 0

    def __init__(self):
        RenderableCandidate.class_id += 1

        self.id: int = RenderableCandidate.class_id
        self.term: Term = None
        self.display_text: str = None  # Text to show, if there is any overlap
        self.text: str = None  # Actual text of the term
        self.text_lc: str = None
        self.pos: int = None
        self.length: int = 1
        self.is_word: int = None

    def __repr__(self):
        parts = [f"pos {self.pos}", f"(id {self.id})"]
        parts = " ".join(parts)
        return f'<RenderableCandidate "{self.text}", {parts}>'

    @property
    def term_id(self) -> int:
        return self.term.id if self.term else None

    @property
    def order_end(self) -> int:
        return self.pos + self.length - 1

    def make_text_item(self, p_num: int, se_id: int, lang: Language):
        """
        Create a TextItem for final rendering.
        """
        t = TextItem(self.term)
        t.order = self.pos
        t.lang_id = lang.id
        t.display_text = self.display_text
        t.text = self.text
        t.text_lc = lang.get_lowercase(self.text)
        t.token_count = self.length
        t.para_id = p_num
        t.se_id = se_id
        t.is_word = self.is_word
        t.text_length = len(self.text)
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
        self.subjLC = self.language.get_lowercase(self.subject)

    def locate_string(self, s):
        """
        Find the string s in the subject self.subject.
        """
        find_lc = self.language.get_lowercase(s)
        find_lc = TokenLocator.make_string(find_lc)

        matches = self.preg_match_capture(find_lc, self.subjLC)

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
        return f"{zws}{t}{zws}"


class TextItem:  # pylint: disable=too-many-instance-attributes
    """
    Unit to be rendered.

    Data structure for template read/textitem.html

    Some elements are lazy loaded, because they're only needed in
    certain situations.
    """

    def __init__(self, term=None):
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

        # Calls setter
        self.term = term

        # The tooltip should be shown for well-known/ignored TextItems
        # that merit a tooltip. e.g., if there isn't any actual Term
        # entity associated with this TextItem, nothing more is needed.
        # Also, if there is a Term entity but it's mostly empty, a
        # tooltip isn't useful.
        self._show_tooltip: bool = None

        # The flash message can be None, so we need an extra flag
        # to determine if it has been loaded or not.
        self._flash_message_loaded: bool = False
        self._flash_message: str = None

    def __repr__(self):
        return f'<TextItem "{self.text}" (wo_id={self.wo_id})>'

    @property
    def term(self):
        return self._term

    @term.setter
    def term(self, t):
        self.wo_id = None
        self.wo_status = None
        self._term = t
        if t is None:
            return

        self.wo_id = t.id
        self.wo_status = t.status
        if t.status >= 1 and t.status <= 5:
            self._show_tooltip = True

    @property
    def show_tooltip(self):
        """
        Show the tooltip if there is anything to show.
        Lazy loaded as needed.
        """
        if self._show_tooltip is not None:
            return self._show_tooltip
        if self.term is None:
            return False

        def blank_string(s):
            return s is None or s.strip() == ""

        def has_extra(cterm):
            if cterm is None:
                return False
            no_extra = (
                blank_string(cterm.translation)
                and blank_string(cterm.romanization)
                and cterm.get_current_image() is None
            )
            return not no_extra

        self._show_tooltip = has_extra(self.term)
        for p in self.term.parents:
            self._show_tooltip = self._show_tooltip or has_extra(p)
        return self._show_tooltip

    @property
    def flash_message(self):
        """
        Return flash message if anything present.
        Lazy loaded as needed.
        """
        if self._flash_message_loaded:
            return self._flash_message
        if self.term is None:
            return None

        self._flash_message = self.term.get_flash_message()
        self._flash_message_loaded = True
        return self._flash_message

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
    def status_class(self):
        "Status class to apply."
        if self.wo_id is None:
            return "status0"
        return f"status{self.wo_status}"

    @property
    def html_class_string(self):
        """
        Create class string for TextItem.
        """
        if self.is_word == 0:
            return "textitem"

        if self.wo_id is None:
            classes = ["textitem", "click", "word"]
            return " ".join(classes)

        st = self.wo_status
        classes = [
            "textitem",
            "click",
            "word",
            "word" + str(self.wo_id),
        ]

        tooltip = (
            st not in (Status.WELLKNOWN, Status.IGNORED, Status.UNKNOWN)
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
