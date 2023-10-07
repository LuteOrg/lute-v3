"""
Common classes use for all parsing.
"""

from abc import ABC, abstractmethod
from typing import List

from lute.models.language import Language


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


class AbstractParser(ABC):
    """
    Abstract parser, inherited from by all parsers.
    """

    @abstractmethod
    def get_parsed_tokens(self, text: str, language: Language) -> List:
        """
        Get an array of ParsedTokens from the input text for the given language.
        """
        pass


    def get_reading(self, text: str):
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

