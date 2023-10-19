"""
Common classes use for all parsing.
"""

from abc import ABC, abstractmethod
from typing import List

class ParsedToken:
    """
    A single parsed token from an input text.
    """
    def __init__(
            self,
            token: str,
            is_word: bool,
            is_end_of_sentence: bool = False
    ):
        self.token = token
        self.is_word = is_word
        self.is_end_of_sentence = is_end_of_sentence

    def __repr__(self):
        return f"<\"{self.token}\" (word: {self.is_word}, eos: {self.is_end_of_sentence})>"


class SentenceGroupIterator:
    """
    An iterator of ParsedTokens that groups them by sentence, up
    to a maximum number of tokens.
    """

    def __init__(self, tokens, maxcount=500):
        self.tokens = tokens
        self.maxcount = maxcount
        self.currpos = 0

    def count(self):
        """
        Get count of groups that will be returned.
        """
        old_currpos = self.currpos
        c = 0
        while self.next():
            c += 1
        self.currpos = old_currpos
        return c

    def next(self):
        """
        Get next sentence group.
        """
        if self.currpos >= len(self.tokens):
            return False

        curr_tok_count = 0
        last_eos = -1
        i = self.currpos

        while (curr_tok_count <= self.maxcount or last_eos == -1) and i < len(self.tokens):
            tok = self.tokens[i]
            if tok.is_end_of_sentence == 1:
                last_eos = i
            if tok.is_word == 1:
                curr_tok_count += 1
            i += 1

        if curr_tok_count <= self.maxcount or last_eos == -1:
            ret = self.tokens[self.currpos:i]
            self.currpos = i + 1
        else:
            ret = self.tokens[self.currpos:last_eos + 1]
            self.currpos = last_eos + 1

        return ret


class AbstractParser(ABC):
    """
    Abstract parser, inherited from by all parsers.
    """

    @property
    @abstractmethod
    def name(self):
        """
        Parser name, for displaying in UI.
        """

    @abstractmethod
    def get_parsed_tokens(self, text: str, language) -> List:
        """
        Get an array of ParsedTokens from the input text for the given language.
        """


    def get_reading(self, text: str): # pylint: disable=unused-argument
        """
        Get the pronunciation for the given text.  For most
        languages, this can't be automated.
        """
        return None


    def get_lowercase(self, text: str):
        """
        Return the lowcase text.

        Most languages can use the built-in lowercase operation,
        but some (like Turkish) need special handling.
        """
        return text.lower()
