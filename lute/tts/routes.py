"""
Edge-TTS voice synthesis and Google auto-translation routes.

Provides:
  * GET /tts/<lang>/<path:text>  -- generate (and cache) an mp3 using edge-tts.
  * GET /api/translate/<sl>/<tl>/<path:text>  -- translate text via Google's
    free translate API, cached in memory.
"""

import os
import asyncio
import hashlib
import urllib.parse

import requests
from flask import Blueprint, current_app, send_file, jsonify

try:
    import edge_tts
    _EDGE_TTS_AVAILABLE = True
except ImportError:
    _EDGE_TTS_AVAILABLE = False

bp = Blueprint("tts", __name__)


# Voice mapping: language code -> edge-tts voice name.
VOICE_MAP = {
    "ja": "ja-JP-NanamiNeural",
    "en": "en-US-AvaNeural",
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "hi": "hi-IN-MadhurNeural",
    "ru": "ru-RU-SvetlanaNeural",
    "ko": "ko-KR-SunHiNeural",
    "ar": "ar-EG-SalmaNeural",
    "it": "it-IT-ElsaNeural",
    "pt": "pt-BR-FranciscaNeural",
    "tr": "tr-TR-EmelNeural",
    "nl": "nl-NL-ColetteNeural",
    "pl": "pl-PL-AgnieszkaNeural",
    "cs": "cs-CZ-VlastaNeural",
    "th": "th-TH-PremwadeeNeural",
    "id": "id-ID-GadisNeural",
    "vi": "vi-VN-HoaiMyNeural",
    "el": "el-GR-AthinaNeural",
    "he": "he-IL-HilaNeural",
    "sv": "sv-SE-SofieNeural",
    "uk": "uk-UA-PolinaNeural",
    "no": "nb-NO-PernilleNeural",
    "fi": "fi-FI-NooraNeural",
    "da": "da-DK-JeppeNeural",
    "ro": "ro-RO-AlinaNeural",
    "hu": "hu-HU-NoemiNeural",
    "ca": "ca-ES-JoanaNeural",
    "bg": "bg-BG-BorislavNeural",
    "hr": "hr-HR-GabrijelaNeural",
}
DEFAULT_VOICE = "en-US-AvaNeural"

# Mapping from the Lute Language "name" to an ISO 639-1 code used by the
# TTS and translate routes.  Used by read/routes.py to pass the source
# language code to the reading template.
LANG_NAME_TO_CODE = {
    "japanese": "ja",
    "english": "en",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "chinese": "zh",
    "classical chinese": "zh",
    "simplified chinese": "zh",
    "traditional chinese": "zh",
    "mandarin": "zh",
    "cantonese": "zh",
    "italian": "it",
    "portuguese": "pt",
    "russian": "ru",
    "korean": "ko",
    "arabic": "ar",
    "hindi": "hi",
    "dutch": "nl",
    "polish": "pl",
    "turkish": "tr",
    "vietnamese": "vi",
    "thai": "th",
    "indonesian": "id",
    "czech": "cs",
    "greek": "el",
    "hebrew": "he",
    "swedish": "sv",
    "ukrainian": "uk",
    "latin": "la",
    "norwegian": "no",
    "finnish": "fi",
    "danish": "da",
    "romanian": "ro",
    "hungarian": "hu",
    "catalan": "ca",
    "bulgarian": "bg",
    "croatian": "hr",
    "persian": "fa",
    "malay": "ms",
    "tagalog": "tl",
}


def get_lang_code(lang_name):
    """
    Get the ISO 639-1 language code for a Lute language name.
    Falls back to 'en' if the language is unknown.
    """
    if not lang_name:
        return "en"
    return LANG_NAME_TO_CODE.get(lang_name.lower(), "en")


# In-memory translation cache:  "{sl}_{tl}_{text}" -> translation string.
trans_cache = {}


@bp.route("/tts/<lang>/<path:text>", methods=["GET"])
def tts_speak(lang, text):
    """
    Generate speech for *text* using edge-tts, returning an mp3.

    Audio files are cached on disk in DATAPATH/tts_cache, keyed by the
    MD5 of ``f"{lang}_{text}"`` so repeated requests are served
    instantly.
    """
    voice = VOICE_MAP.get(lang, DEFAULT_VOICE)

    datapath = current_app.config["DATAPATH"]
    cache_dir = os.path.join(datapath, "tts_cache")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    key = f"{lang}_{text}"
    filename = hashlib.md5(key.encode("utf-8")).hexdigest() + ".mp3"
    filepath = os.path.join(cache_dir, filename)

    if not os.path.exists(filepath):
        _generate_audio(text, voice, filepath)

    return send_file(filepath, mimetype="audio/mpeg")


def _generate_audio(text, voice, filepath):
    """
    Use edge-tts to synthesize *text* with *voice*, saving to *filepath*.

    edge-tts is async, so it is run via asyncio.run() within this sync
    Flask route.

    Returns None on success, or an error tuple on failure.
    """
    if not _EDGE_TTS_AVAILABLE:
        return jsonify({"error": "edge-tts not installed"}), 500

    async def _run():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filepath)

    asyncio.run(_run())
    return None


@bp.route("/api/translate/<sl>/<tl>/<path:text>", methods=["GET"])
def translate(sl, tl, text):
    """
    Translate *text* from source language *sl* to target language *tl*.

    Tries Google's free translate API first, then falls back to
    MyMemory API if Google fails.

    Results are cached in the in-memory ``trans_cache`` dict.

    Returns JSON ``{"translation": "..."}``.
    """
    cache_key = f"{sl}_{tl}_{text}"
    if cache_key in trans_cache:
        return jsonify({"translation": trans_cache[cache_key]})

    translation = _translate_via_google(sl, tl, text)
    if not translation:
        translation = _translate_via_mymemory(sl, tl, text)

    trans_cache[cache_key] = translation
    return jsonify({"translation": translation})


def _translate_via_google(sl, tl, text):
    """Try Google's free translate API.  Returns '' on failure."""
    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl={sl}&tl={tl}&dt=t&q={urllib.parse.quote(text)}"
    )
    try:
        resp = requests.get(url, timeout=8)
        data = resp.json()
        if data and data[0] and data[0][0]:
            result = data[0][0][0] or ""
            if result and result.lower() == text.lower():
                return ""
            return result
    except Exception as e:  # pylint: disable=broad-exception-caught
        current_app.logger.warning("Google translate failed: %s", e)
    return ""


def _translate_via_mymemory(sl, tl, text):
    """Try MyMemory free translate API.  Returns '' on failure."""
    langpair = f"{sl}|{tl}"
    url = (
        "https://api.mymemory.translated.net/get"
        f"?q={urllib.parse.quote(text)}"
        f"&langpair={urllib.parse.quote(langpair)}"
    )
    try:
        resp = requests.get(url, timeout=8)
        data = resp.json()
        if data and data.get("responseData") and data["responseData"].get("translatedText"):
            result = data["responseData"]["translatedText"]
            # If result is identical to input, treat as failed translation
            if result and result.lower() == text.lower():
                return ""
            return result
    except Exception as e:  # pylint: disable=broad-exception-caught
        current_app.logger.warning("MyMemory translate failed: %s", e)
    return ""
