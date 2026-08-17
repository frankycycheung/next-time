"""Tests for next-time core modules."""

import json
import os
import sys
import tempfile
import unittest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.detector import Detector
from core.categorizer import Categorizer
from core.tracker import Tracker
from core.context import ContextCapture


class TestDetector(unittest.TestCase):

    def setUp(self):
        self.detector = Detector()

    def test_english(self):
        result = self.detector.detect("Next time we should try that ramen place")
        self.assertIsNotNone(result)
        self.assertEqual(result["lang"], "en")

    def test_chinese(self):
        result = self.detector.detect("下次一齊去食飯啦！")
        self.assertIsNotNone(result)
        self.assertEqual(result["lang"], "zh")

    def test_japanese(self):
        result = self.detector.detect("今度行こう")
        self.assertIsNotNone(result)
        self.assertEqual(result["lang"], "ja")

    def test_korean(self):
        result = self.detector.detect("다음에 가자")
        self.assertIsNotNone(result)
        self.assertEqual(result["lang"], "ko")

    def test_spanish(self):
        result = self.detector.detect("la próxima vez vamos a ese restaurante")
        self.assertIsNotNone(result)
        self.assertEqual(result["lang"], "es")

    def test_no_trigger(self):
        result = self.detector.detect("This is a normal sentence with no trigger")
        self.assertIsNone(result)

    def test_empty_text(self):
        result = self.detector.detect("")
        self.assertIsNone(result)

    def test_extract_action(self):
        match = self.detector.detect("下次一齊去食飯啦！")
        action = self.detector.extract_action("下次一齊去食飯啦！", match)
        self.assertTrue("食飯" in action or "去" in action)

    def test_language_count(self):
        count = self.detector.language_count
        self.assertGreaterEqual(count, 10)

    def test_multiple_matches(self):
        matches = self.detector.scan("下次 try that place 下次再去")
        self.assertGreaterEqual(len(matches), 2)


class TestCategorizer(unittest.TestCase):

    def setUp(self):
        self.categorizer = Categorizer()

    def test_food(self):
        cat = self.categorizer.categorize_with_fallback("next time try that ramen place")
        self.assertEqual(cat, "food")

    def test_travel(self):
        cat = self.categorizer.categorize_with_fallback("下次去日本")
        self.assertEqual(cat, "travel")

    def test_learn(self):
        cat = self.categorizer.categorize_with_fallback("someday learn rust")
        self.assertEqual(cat, "learn")

    def test_relationship(self):
        cat = self.categorizer.categorize_with_fallback("帶朋友去大嶼山睇日落")
        self.assertEqual(cat, "relationship")

    def test_health(self):
        cat = self.categorizer.categorize_with_fallback("今度ジムに行く")
        self.assertEqual(cat, "health")

    def test_unknown_fallback(self):
        cat = self.categorizer.categorize_with_fallback("some random text no keywords here")
        self.assertEqual(cat, "other")

    def test_learn_from_correction(self):
        # Initially might not catch this
        text = "下次去圖書館借書"
        initial = self.categorizer.categorize(text)
        # Learn correction
        self.categorizer.learn(text, "learn")
        corrected = self.categorizer.categorize(text)
        self.assertEqual(corrected, "learn")

    def test_get_emoji(self):
        self.assertEqual(self.categorizer.get_emoji("food"), "🍜")
        self.assertEqual(self.categorizer.get_emoji("unknown"), "📌")


class TestTracker(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tracker = Tracker(path=os.path.join(self.temp_dir.name, "test.json"))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_item(self):
        item = self.tracker.add("下次試中環間拉麵店", source="test")
        self.assertEqual(item["text"], "下次試中環間拉麵店")
        self.assertEqual(item["status"], "pending")
        self.assertEqual(item["source"], "test")
        self.assertTrue(item["id"].startswith("nt-"))

    def test_add_auto_categorize(self):
        item = self.tracker.add("next time try that ramen place")
        self.assertEqual(item["category"], "food")

    def test_add_with_category_override(self):
        item = self.tracker.add("下次試中環間拉麵店", category="travel")
        self.assertEqual(item["category"], "travel")

    def test_get_item(self):
        added = self.tracker.add("test item")
        retrieved = self.tracker.get(added["id"])
        self.assertEqual(retrieved["id"], added["id"])

    def test_get_nonexistent(self):
        result = self.tracker.get("nt-999")
        self.assertIsNone(result)

    def test_list_empty(self):
        items = self.tracker.list()
        self.assertEqual(len(items), 0)

    def test_list_with_items(self):
        self.tracker.add("item 1")
        self.tracker.add("item 2")
        items = self.tracker.list()
        self.assertEqual(len(items), 2)

    def test_list_filter_by_status(self):
        self.tracker.add("item 1")
        item2 = self.tracker.add("item 2")
        self.tracker.update_status(item2["id"], "completed")

        pending = self.tracker.list(status="pending")
        completed = self.tracker.list(status="completed")

        self.assertEqual(len(pending), 1)
        self.assertEqual(len(completed), 1)

    def test_update_status(self):
        item = self.tracker.add("test")
        self.tracker.update_status(item["id"], "completed")
        updated = self.tracker.get(item["id"])
        self.assertEqual(updated["status"], "completed")
        self.assertIn("completed_at", updated)

    def test_update_status_invalid(self):
        with self.assertRaises(ValueError):
            self.tracker.update_status("nt-001", "invalid_status")

    def test_remove_item(self):
        item = self.tracker.add("to remove")
        self.assertTrue(self.tracker.remove(item["id"]))
        self.assertIsNone(self.tracker.get(item["id"]))

    def test_smart_archive(self):
        # Add an item, then archive with zero-day thresholds
        self.tracker.add("old item")
        result = self.tracker.smart_archive(flag_days=0, auto_archive_days=0)
        self.assertEqual(len(result["archived"]), 1)
        self.assertEqual(result["archived"][0]["old_status"], "pending")

    def test_recover(self):
        self.tracker.add("item")
        self.tracker.smart_archive(flag_days=0, auto_archive_days=0)
        self.tracker.recover("nt-001")
        item = self.tracker.get("nt-001")
        self.assertEqual(item["status"], "pending")

    def test_stats(self):
        self.tracker.add("item 1")
        item2 = self.tracker.add("item 2")
        self.tracker.update_status(item2["id"], "completed")

        stats = self.tracker.stats()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["completion_rate_pct"], 50.0)

    def test_export_json(self):
        self.tracker.add("test")
        output = self.tracker.export("json")
        data = json.loads(output)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_export_markdown(self):
        self.tracker.add("test")
        output = self.tracker.export("md")
        self.assertIn("Next-Time Export", output)
        self.assertIn("test", output)

    def test_export_csv(self):
        self.tracker.add("test")
        output = self.tracker.export("csv")
        self.assertIn("id,", output)
        self.assertIn("nt-001", output)

    def test_set_deadline(self):
        item = self.tracker.add("test")
        self.tracker.set_deadline(item["id"], "2026-12-31T00:00:00")
        updated = self.tracker.get(item["id"])
        self.assertEqual(updated["deadline"], "2026-12-31T00:00:00")
        self.assertEqual(updated["status"], "scheduled")


class TestContextCapture(unittest.TestCase):

    def setUp(self):
        self.capture = ContextCapture(window_size=2)

    def test_build_context(self):
        history = [
            {"id": "msg-1", "sender": "User", "text": "知唔知港島有咩好嘢食？", "timestamp": "10:00"},
            {"id": "msg-2", "sender": "Friend", "text": "推介漁獲", "timestamp": "10:01"},
            {"id": "msg-3", "sender": "User", "text": "下次一齊去！", "timestamp": "10:02"},
        ]
        trigger = history[2]
        context = self.capture.build_context(trigger, history, source="test")
        self.assertIn("User", context["participants"])
        self.assertIn("Friend", context["participants"])
        self.assertIn("下次一齊去", context["conversation_preview"])

    def test_minimal_context(self):
        trigger = {"id": "msg-1", "sender": "User", "text": "test"}
        context = self.capture.build_context(trigger, [], source="test")
        self.assertEqual(context["source"], "test")


if __name__ == "__main__":
    unittest.main(verbosity=2)