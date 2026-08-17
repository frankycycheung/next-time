"""
detector.py — Multi-language pattern detector with LLM fallback.

Scans text for deferred-action patterns across 10+ languages.
Supports regex-level keyword matching + optional LLM edge-case detection.
"""

import json
import re
import os
from pathlib import Path

PATTERNS_PATH = Path(__file__).parent / "patterns.json"


def load_patterns(path: str = None) -> dict:
    path = path or PATTERNS_PATH
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["languages"]


def compile_patterns(languages: dict) -> list[dict]:
    """
    Pre-compile all language patterns into a flat list of
    { "lang", "lang_label", "regex" } objects.
    """
    compiled = []
    for lang_code, config in languages.items():
        for raw_pattern in config["patterns"]:
            # Escape special regex chars, then allow word-boundary matching
            escaped = re.escape(raw_pattern)
            compiled.append({
                "lang": lang_code,
                "lang_label": config["label"],
                "regex": re.compile(escaped, re.IGNORECASE),
                "pattern": raw_pattern,
            })
    return compiled


class Detector:
    """
    Detects deferred-action phrases in text.

    Usage:
        detector = Detector()
        matches = detector.scan("下次一齊去食飯啦！")
        # -> [{"lang": "zh", "matched": "下次", "position": (0,2)}]
    """

    def __init__(self, patterns_path: str = None):
        languages = load_patterns(patterns_path)
        self.patterns = compile_patterns(languages)
        self.supported_languages = list(languages.keys())

    def scan(self, text: str) -> list[dict]:
        """
        Scan text for any deferred-action patterns.
        Returns list of matches, sorted by position.
        """
        if not text or not text.strip():
            return []

        matches = []
        seen_spans = set()

        for entry in self.patterns:
            for match in entry["regex"].finditer(text):
                span = (match.start(), match.end())
                if span not in seen_spans:
                    seen_spans.add(span)
                    matches.append({
                        "lang": entry["lang"],
                        "lang_label": entry["lang_label"],
                        "matched": match.group(),
                        "pattern": entry["pattern"],
                        "position": span,
                    })

        # Sort by start position
        matches.sort(key=lambda m: m["position"][0])
        return matches

    def detect(self, text: str, use_llm_fallback: bool = False, llm_classify_fn=None) -> dict | None:
        """
        High-level detection: returns the best match or None.

        Args:
            text: Input text to scan
            use_llm_fallback: If True and no keyword match, call llm_classify_fn
            llm_classify_fn: Callable(text) -> dict | None, for LLM-based detection

        Returns:
            { "lang", "lang_label", "matched", "pattern", "position" } or None
        """
        matches = self.scan(text)
        if matches:
            return matches[0]

        if use_llm_fallback and llm_classify_fn:
            return llm_classify_fn(text)

        return None

    def extract_action(self, text: str, match: dict) -> str:
        """
        Extract the actionable part of the text.
        e.g. "下次一齊去食飯啦！" -> "一齊去食飯"
        """
        # Simple heuristic: take everything after the trigger
        start = match["position"][1]
        action = text[start:].strip()
        # Remove trailing punctuation/particles
        action = re.sub(r'^[,\s，、。！？!?]+', '', action)
        action = re.sub(r'[,\s，、。！？!?]+$', '', action)
        return action if action else text.strip()

    def describe_detection(self, text: str) -> str:
        """
        Returns a human-readable description of what was detected.
        Useful for agent logging.
        """
        match = self.detect(text)
        if not match:
            return None
        action = self.extract_action(text, match)
        return f"[{match['lang_label']}] \"{match['matched']}\" → {action}"

    @property
    def language_count(self) -> int:
        return len(self.supported_languages)


# Fast standalone test
if __name__ == "__main__":
    detector = Detector()

    test_cases = [
        ("Next time we should try that ramen place", "en"),
        ("下次一齊去食飯啦！", "zh"),
        ("今度行こう", "ja"),
        ("다음에 가자", "ko"),
        ("la próxima vez vamos a ese restaurante", "es"),
        ("quand j'aurai le temps je lirai ce livre", "fr"),
        ("nächstes Mal machen wir das", "de"),
        ("คราวหน้าไปเที่ยวกัน", "th"),
        ("lần sau đi ăn nhé", "vi"),
        ("No trigger here, just a regular sentence", None),
    ]

    for text, expected_lang in test_cases:
        result = detector.detect(text)
        lang = result["lang"] if result else None
        status = "✓" if lang == expected_lang else "✗"
        print(f"{status} {lang or 'None':>6} | {text}")