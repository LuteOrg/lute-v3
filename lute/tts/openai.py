from lute.tts.base import AbstractTextToSpeechEngine
from flask import current_app

from openai import OpenAI
import os


class TTSEngineOpenAiApi(AbstractTextToSpeechEngine):
    """
    TTS Engine for Opne API
    """

    def __init__(self):
        model = 'tts-1'
        voice = 'echo'
        api_key = None
        openai_config = current_app.env_config.tts_configs.get('OPENAI')
        if openai_config is not None:
            model = openai_config.get('MODEL', 'tts-1')
            voice = openai_config.get('VOICE', 'echo')
            api_key = openai_config.get('APIKEY')
        if api_key is None:
            self.client = OpenAI()
        else:
            self.client = OpenAI(api_key=api_key)
        self._model = model
        self._voice = voice

    def name(self):
        return "OpenAI_TTS"

    def tts(self, text: str, speech_file_path: str, format='mp3'):
        response = self.client.audio.speech.create(
            model= self._model,
            voice = self._voice,
            input= text,
            response_format = format
        )
        response.stream_to_file(speech_file_path)
