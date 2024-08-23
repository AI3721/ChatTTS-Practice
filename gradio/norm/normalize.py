import re
from typing import Literal
from .norm_zh import ZHNormalizer
from .norm_en import ENNormalizer

normalize_zh = ZHNormalizer().normalize_sentence
normalize_en = ENNormalizer().normalize_sentence

def detect_language(sentence: str) -> Literal["zh", "en"]:
    chinese_chars = re.compile(r"[\u4e00-\u9fff]").findall(sentence)
    english_words = re.compile(r"\b[A-Za-z]+\b").findall(sentence)
    if len(chinese_chars) > len(english_words):
        return "zh"
    else:
        return "en"

def normalize(text):
    if detect_language(text) == "zh":
        return normalize_zh(text)
    else:
        return normalize_en(text)
