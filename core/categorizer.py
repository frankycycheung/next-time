"""
categorizer.py — Auto-categorization of deferred-action items.

Two-tier strategy:
1. Keyword match (fast, zero cost)
2. LLM fallback for ambiguous text

Learns from user corrections over time.
"""

import re
from pathlib import Path

# Category definitions with keyword hints
CATEGORIES = {
    "food": {
        "emoji": "🍜",
        "label": "Food & Drink",
        "keywords": [
            "eat", "restaurant", "food", "dinner", "lunch", "breakfast",
            "cafe", "coffee", "drink", "bar", "pub", "ramen", "sushi",
            "pizza", "steak", "dessert", "bakery", "brunch", "takeout",
            "食", "餐廳", "飯", "美食", "飲茶", "咖啡", "cake",
            "レストラン", "食べる", "食事", "カフェ",
            "맛집", "식당", "먹다", "음식",
            "comer", "restaurante", "comida",
        ],
    },
    "travel": {
        "emoji": "✈️",
        "label": "Travel & Places",
        "keywords": [
            "travel", "trip", "vacation", "go to", "visit", "flight",
            "hotel", "airbnb", "booking", "destination", "tour",
            "去", "旅行", "旅遊", "機票", "酒店", "旅館",
            "여행", "가다", "호텔",
            "viajar", "viaje", "vuelo",
        ],
    },
    "work": {
        "emoji": "💻",
        "label": "Work & Projects",
        "keywords": [
            "project", "work", "meeting", "task", "deadline", "client",
            "deploy", "release", "pr", "merge", "review", "code",
            "工作", "項目", "開會", "deadline", "任務",
            "仕事", "プロジェクト", "会議",
            "업무", "프로젝트", "회의",
        ],
    },
    "hobby": {
        "emoji": "🎮",
        "label": "Hobby & Fun",
        "keywords": [
            "game", "play", "movie", "show", "anime", "netflix",
            "concert", "music", "hiking", "sport", "gym",
            "玩", "遊戲", "睇", "戲", "電影", "動漫",
            "ゲーム", "遊ぶ", "映画",
            "게임", "놀다", "영화",
        ],
    },
    "learn": {
        "emoji": "📚",
        "label": "Learn & Research",
        "keywords": [
            "learn", "study", "read", "read", "course", "tutorial",
            "book", "article", "paper", "research", "skill",
            "學", "學習", "讀", "書", "研究", "course",
            "勉強", "学ぶ", "読む", "本",
            "공부", "배우다", "읽다", "책",
        ],
    },
    "shopping": {
        "emoji": "🛍️",
        "label": "Shopping",
        "keywords": [
            "buy", "shop", "purchase", "order", "amazon", "gadget",
            "買", "購物", "網購", "amazon",
            "買う", "ショッピング",
            "사다", "쇼핑",
        ],
    },
    "home": {
        "emoji": "🏠",
        "label": "Home & Life",
        "keywords": [
            "home", "apartment", "renovation", "furniture", "clean",
            "搬屋", "裝修", "家居", "打掃",
            "家", "引越し", "リノベーション",
            "집", "이사", "인테리어",
        ],
    },
    "relationship": {
        "emoji": "❤️",
        "label": "Relationship & Family",
        "keywords": [
            "girlfriend", "date", "anniversary", "family",
            "parent", "friend", "birthday", "gift", "partner",
            "女朋友", "約會", "紀念日", "家人", "朋友", "帶",
            "彼女", "デート", "家族", "友達",
            "여자친구", "데이트", "가족", "친구",
        ],
    },
    "health": {
        "emoji": "🏥",
        "label": "Health & Wellness",
        "keywords": [
            "doctor", "hospital", "checkup", "exercise", "diet",
            "yoga", "meditation", "sleep",
            "醫生", "醫院", "運動", "健康",
            "医者", "病院", "運動", "健康", "ジム",
            "병원", "운동", "건강",
        ],
    },
    "creative": {
        "emoji": "🎨",
        "label": "Creative & Art",
        "keywords": [
            "draw", "paint", "write", "music", "photo", "design",
            "art", "創作", "畫", "寫作",
            "描く", "書く", "音楽", "デザイン",
            "그리다", "쓰다", "음악", "디자인",
        ],
    },
}


class Categorizer:
    """
    Two-tier auto-categorization with user-correction learning.
    """

    def __init__(self, hints_path: str = None):
        self.categories = CATEGORIES
        # User corrections: { "original text": "corrected_category" }
        self.user_hints: dict[str, str] = {}
        self.hints_path = hints_path

    def categorize(self, text: str) -> str:
        """
        Determine category for a given text.
        Returns category key (e.g. "food", "travel").
        """
        if not text:
            return "other"

        text_lower = text.lower()

        # Check user hints first (highest priority)
        if text in self.user_hints:
            return self.user_hints[text]

        # Keyword matching with scoring
        scores = {}
        for cat_key, cat_config in self.categories.items():
            score = 0
            for kw in cat_config["keywords"]:
                if kw.lower() in text_lower:
                    score += 1
            if score > 0:
                scores[cat_key] = score

        if scores:
            # Return highest-scoring category
            return max(scores, key=scores.get)

        # Fallback: LLM categorization (called externally)
        return None  # Signal that LLM fallback is needed

    def categorize_with_fallback(self, text: str, llm_fn=None) -> str:
        """
        Categorize with LLM fallback if keyword matching fails.
        """
        result = self.categorize(text)
        if result is not None:
            return result

        if llm_fn:
            llm_result = llm_fn(text)
            if llm_result in self.categories:
                return llm_result

        return "other"

    def learn(self, text: str, corrected_category: str):
        """
        Learn from user correction.
        Future categorizations of the same text will use this hint.
        """
        if corrected_category in self.categories:
            self.user_hints[text] = corrected_category
            self._save_hints()

    def _save_hints(self):
        if self.hints_path:
            import json
            with open(self.hints_path, "w", encoding="utf-8") as f:
                json.dump(self.user_hints, f, ensure_ascii=False, indent=2)

    def get_emoji(self, category: str) -> str:
        return self.categories.get(category, {}).get("emoji", "📌")

    def get_label(self, category: str) -> str:
        return self.categories.get(category, {}).get("label", "Other")


# Quick test
if __name__ == "__main__":
    c = Categorizer()
    tests = [
        ("下次去日本旅行", "travel"),
        ("next time try that ramen place", "food"),
        ("someday learn rust", "learn"),
        ("得閒帶朋友去食甜品", "food"),
        ("今度ジムに行く", "health"),
    ]
    for text, expected in tests:
        result = c.categorize_with_fallback(text)
        status = "✓" if result == expected else "✗"
        emoji = c.get_emoji(result)
        print(f"{status} {emoji} {result:>12} | {text}")