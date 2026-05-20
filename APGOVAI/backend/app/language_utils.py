from langdetect import detect

from deep_translator import GoogleTranslator


def detect_language(text: str):

    try:
        return detect(text)
    except:
        return "en"


def translate_to_english(text: str):

    return GoogleTranslator(
        source="auto",
        target="en",
    ).translate(text)


def translate_to_telugu(text: str):

    return GoogleTranslator(
        source="auto",
        target="te",
    ).translate(text)