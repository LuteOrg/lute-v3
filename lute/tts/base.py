from abc import ABC, abstractmethod


class AbstractTextToSpeechEngine(ABC):
    """
    Abstract engine, inherited from by all Lute TTS engines.
    """

    @classmethod
    @abstractmethod
    def name(cls):
        """
        TTS engine name, for displaying in UI.
        """

    @abstractmethod
    def tts(self, text: str, filepath: str, format: str):
        """
        converts text to speech and writes to filepath
        """

class TTSEngineManager:
    pass