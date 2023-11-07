"""
Parsing for space-delimited languages.

The parser uses some Language settings (e.g., word characters) to
perform the actual parsing.

Includes classes:

- SpaceDelimitedParser
- Turkish
"""

import re
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

    def get_parsed_tokens(self, text: str, language) -> List[ParsedToken]:
        "Return parsed tokens."
        clean_text = re.sub(r" +", " ", text)
        zws = chr(0x200B)  # zero-width space
        clean_text = clean_text.replace(zws, "")
        return self._parse_to_tokens(clean_text, language)

    def preg_match_capture(self, pattern, subject):
        """
        Return the matched text and their start positions in the subject.

        E.g. search for r'cat' in "there is a CAT and a Cat" returns:
        [['CAT', 11], ['Cat', 21]]
        """
        matches = re.finditer(pattern, subject, flags=re.IGNORECASE)
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
        termchar = lang.word_characters
        if termchar.strip() == "":
            raise RuntimeError(
                f"Language {lang.name} has invalid Word Characters specification."
            )

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
            pattern = f"[{re.escape(lang.regexp_split_sentences)}]"
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
