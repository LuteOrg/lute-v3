"""
Parsing for space-delimited languages.

The parser uses some Language settings (e.g., word characters) to
perform the actual parsing.

Includes classes:

- SpaceDelimitedParser
- TurkishParser
"""

import functools
import re
import sys
import unicodedata

from typing import List

from lute.parse.base import ParsedToken, AbstractParser


class SpaceDelimitedParser(AbstractParser):
    """
    A general parser for space-delimited languages,
    such as English, French, Spanish ... etc.
    """

    @classmethod
    def name(cls):
        return "Space Delimited"

    @staticmethod
    @functools.lru_cache
    def compile_re_pattern(pattern: str, *args, **kwargs) -> re.Pattern:
        """Compile regular expression pattern, cache result for fast re-use."""
        return re.compile(pattern, *args, **kwargs)

    @staticmethod
    @functools.lru_cache
    def get_default_word_characters() -> str:
        """Return default value for lang.word_characters."""

        # Unicode categories reference: https://www.compart.com/en/unicode/category
        categories = set(["Cf", "Ll", "Lm", "Lo", "Lt", "Lu", "Mc", "Mn", "Sk"])

        # There are more than 130,000 characters across all these categories.
        # Expressing this a single character at a time, mostly using unicode
        # escape sequences like \u1234 or \U12345678, would require 1 megabyte.
        # Converting to ranges like \u1234-\u1256 requires only 10K.
        ranges = []
        current = None

        def add_current_to_ranges():
            def ucode(n):
                "Unicode point for integer."
                fstring = r"\u{:04x}" if n < 0x10000 else r"\U{:08x}"
                return (fstring).format(n)

            start_code = ucode(current[0])
            if current[0] == current[1]:
                range_string = start_code
            else:
                endcode = ucode(current[1])
                range_string = f"{start_code}-{endcode}"
            ranges.append(range_string)

        for i in range(1, sys.maxunicode):
            if unicodedata.category(chr(i)) not in categories:
                if current is not None:
                    add_current_to_ranges()
                    current = None
            elif current is None:
                # Starting a new range.
                current = [i, i]
            else:
                # Extending existing range.
                current[1] = i

        if current is not None:
            add_current_to_ranges()

        return "".join(ranges)

    @staticmethod
    @functools.lru_cache
    def get_default_regexp_split_sentences() -> str:
        """Return default value for lang.regexp_split_sentences."""

        # Construct pattern from Unicode ATerm and STerm categories.
        # See: https://www.unicode.org/Public/UNIDATA/auxiliary/SentenceBreakProperty.txt
        # and: https://unicode.org/reports/tr29/

        # Also include colon, since that is used to separate speakers
        # and their dialog, and is a reasonable dividing point for
        # sentence translations.

        return "".join(
            [
                re.escape(".!?:"),
                # ATerm entries (other than ".", covered above):
                r"\u2024\uFE52\uFF0E",
                # STerm entries (other than "!" and "?", covered above):
                r"\u0589",
                r"\u061D-\u061F\u06D4",
                r"\u0700-\u0702",
                r"\u07F9",
                r"\u0837\u0839\u083D\u083E",
                r"\u0964\u0965",
                r"\u104A\u104B",
                r"\u1362\u1367\u1368",
                r"\u166E",
                r"\u1735\u1736",
                r"\u17D4\u17D5",
                r"\u1803\u1809",
                r"\u1944\u1945",
                r"\u1AA8-\u1AAB",
                r"\u1B5A\u1B5B\u1B5E\u1B5F\u1B7D\u1B7E",
                r"\u1C3B\u1C3C",
                r"\u1C7E\u1C7F",
                r"\u203C\u203D\u2047-\u2049\u2E2E\u2E3C\u2E53\u2E54\u3002",
                r"\uA4FF",
                r"\uA60E\uA60F",
                r"\uA6F3\uA6F7",
                r"\uA876\uA877",
                r"\uA8CE\uA8CF",
                r"\uA92F",
                r"\uA9C8\uA9C9",
                r"\uAA5D\uAA5F",
                r"\uAAF0\uAAF1\uABEB",
                r"\uFE56\uFE57\uFF01\uFF1F\uFF61",
                r"\U00010A56\U00010A57",
                r"\U00010F55-\U00010F59",
                r"\U00010F86-\U00010F89",
                r"\U00011047\U00011048",
                r"\U000110BE-\U000110C1",
                r"\U00011141-\U00011143",
                r"\U000111C5\U000111C6\U000111CD\U000111DE\U000111DF",
                r"\U00011238\U00011239\U0001123B\U0001123C",
                r"\U000112A9",
                r"\U0001144B\U0001144C",
                r"\U000115C2\U000115C3\U000115C9-\U000115D7",
                r"\U00011641\U00011642",
                r"\U0001173C-\U0001173E",
                r"\U00011944\u00011946",
                r"\U00011A42\U00011A43",
                r"\U00011A9B\U00011A9C",
                r"\U00011C41\U00011C42",
                r"\U00011EF7\U00011EF8",
                r"\U00011F43\U00011F44",
                r"\U00016A6E\U00016A6F",
                r"\U00016AF5",
                r"\U00016B37\U00016B38\U00016B44",
                r"\U00016E98",
                r"\U0001BC9F",
                r"\U0001DA88",
            ]
        )

    def get_parsed_tokens(self, text: str, language) -> List[ParsedToken]:
        "Return parsed tokens."

        # Remove extra spaces.
        clean_text = re.sub(r" +", " ", text)

        # Remove zero-width spaces.
        clean_text = clean_text.replace(chr(0x200B), "")

        return self._parse_to_tokens(clean_text, language)

    def preg_match_capture(self, pattern, subject):
        """
        Return the matched text and their start positions in the subject.

        E.g. search for r'cat' in "there is a CAT and a Cat" returns:
        [['CAT', 11], ['Cat', 21]]
        """
        compiled = SpaceDelimitedParser.compile_re_pattern(pattern, flags=re.IGNORECASE)
        matches = compiled.finditer(subject)
        result = [[match.group(), match.start()] for match in matches]
        return result

    def _parse_to_tokens(self, text: str, lang):
        """
        Returns ParsedToken array for given language.
        """
        replacements = lang.character_substitutions.split("|")
        for replacement in replacements:
            fromto = replacement.strip().split("=")
            if len(fromto) >= 2:
                rfrom = fromto[0].strip()
                rto = fromto[1].strip()
                text = text.replace(rfrom, rto)

        text = text.replace("\r\n", "\n")
        text = text.replace("{", "[")
        text = text.replace("}", "]")

        tokens = []
        paras = text.split("\n")
        pcount = len(paras)
        for i, para in enumerate(paras):
            self.parse_para(para, lang, tokens)
            if i != (pcount - 1):
                tokens.append(ParsedToken("¶", False, True))

        return tokens

    def parse_para(self, text: str, lang, tokens: List[ParsedToken]):
        """
        Parse a string, appending the tokens to the list of tokens.
        """
        termchar = lang.word_characters.strip()
        if not termchar:
            termchar = SpaceDelimitedParser.get_default_word_characters()

        splitex = lang.exceptions_split_sentences.replace(".", "\\.")
        pattern = rf"({splitex}|[{termchar}]*)"
        if splitex.strip() == "":
            pattern = rf"([{termchar}]*)"

        m = self.preg_match_capture(pattern, text)
        wordtoks = list(filter(lambda t: t[0] != "", m))

        def add_non_words(s):
            """
            Add non-word token s to the list of tokens.  If s
            matches any of the split_sentence values, mark it as an
            end-of-sentence.
            """
            if not s:
                return
            splitchar = lang.regexp_split_sentences.strip()
            if not splitchar:
                splitchar = SpaceDelimitedParser.get_default_regexp_split_sentences()
            pattern = f"[{re.escape(splitchar)}]"
            has_eos = False
            if pattern != "[]":  # Should never happen, but ...
                allmatches = self.preg_match_capture(pattern, s)
                has_eos = len(allmatches) > 0
            tokens.append(ParsedToken(s, False, has_eos))

        # For each wordtok, add all non-words before the wordtok, and
        # then add the wordtok.
        pos = 0
        for wt in wordtoks:
            w = wt[0]
            wp = wt[1]
            s = text[pos:wp]
            add_non_words(s)
            tokens.append(ParsedToken(w, True, False))
            pos = wp + len(w)

        # Add anything left over.
        s = text[pos:]
        add_non_words(s)


class TurkishParser(SpaceDelimitedParser):
    "Parser to handle Turkish parsing fun."

    @classmethod
    def name(cls):
        return "Turkish"

    def get_lowercase(self, text):
        "Handle the funny turkish i variants."
        for caps, lower in {"İ": "i", "I": "ı"}.items():
            text = text.replace(caps, lower)
        return text.lower()
