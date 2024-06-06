from importlib.metadata import entry_points
from flask import current_app
from sys import version_info

from lute.tts.base import AbstractTextToSpeechEngine
from lute.tts.openai import TTSEngineOpenAiApi

__TTS_ENGINES__ = { "OpenAI_TTS": TTSEngineOpenAiApi,}


def init_tts_engines():
    """
    Initialize all TTS engines from plugins
    """
    vmaj = version_info.major
    vmin = version_info.minor
    if vmaj == 3 and vmin in (8, 9, 10, 11):
        custom_tts_eps = entry_points().get("lute.plugin.tts")
    elif (vmaj == 3 and vmin >= 12) or (vmaj >= 4):
        # Can't be sure this will always work, API may change again,
        # but can't plan for the unforseeable everywhere.
        custom_tts_eps = entry_points().select(group="lute.plugin.tts")
    else:
        # earlier version of python than 3.8?  What madness is this?
        # Not going to throw, just print and hope the user sees it.
        msg = f"Unable to load plugins for python {vmaj}.{vmin}, please upgrade to 3.8+"
        print(msg, flush=True)
        return

    if custom_tts_eps is None:
        return

    for custom_tts_ep in custom_tts_eps:
        name = custom_tts_ep.name
        klass = custom_tts_ep.load()
        if issubclass(klass, AbstractTextToSpeechEngine):
            __TTS_ENGINES__[name] = klass
        else:
            raise ValueError(f"{name} is not a subclass of AbstractParser")

def get_tts_engine_for_language(language_id):
    if not tts_enabled(language_id):
        return None
    default_engine = current_app.env_config.tts_configs.get("DEFAULT", list(__TTS_ENGINES__.keys())[0])
    language_engine = current_app.env_config.tts_configs.get("LANGSPEC", {}).get(language_id, {}).get("ENGINE")
    if language_engine is None:
        return __TTS_ENGINES__[default_engine]()
    else:
        return __TTS_ENGINES__[language_engine]()


def tts_enabled(language_id):
    if current_app.env_config.tts_configs.get("LANGSPEC", {}).get(language_id, {}).get("DISABLE") is not None:
        return False
    return len(__TTS_ENGINES__.items()) > 0