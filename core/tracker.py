"""
tracker.py — Persistent JSON store for captured items.

CRUD + smart archive + stats + export.
"""

import json
import os
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .categorizer import Categorizer
from .context import ContextCapture


class Tracker:
    """
    Core data store for Next-Time items.

    Stores items in a JSON array at the configured path.
    Handles auto-increment IDs, status transitions, smart archive, and export.
    """

    def __init__(self, path: str = None):
        self.path = Path(path or os.path.expanduser("~/.next-time/tracker.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.categorizer = Categorizer()
        self.context_capture = ContextCapture()
        self._items: list[dict] = []
        self._load()

    # ─────────────────────────── CRUD ───────────────────────────

    def add(
        self,
        text: str,
        source: str = "manual",
        context: dict = None,
        category: str = None,
        sender: str = None,
    ) -> dict:
        """
        Add a new captured item.

        Args:
            text: The deferred action text
            source: Platform/source identifier
            context: Optional conversation context dict
            category: Optional category override. Auto-detected if omitted.
            sender: Who said it

        Returns: The created item dict
        """
        if not category:
            category = self.categorizer.categorize_with_fallback(text) or "other"

        item_id = self._next_id()

        item = {
            "id": item_id,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "text": text,
            "category": category,
            "source": source,
            "sender": sender or "unknown",
            "context": context or {},
            "status": "pending",
            "deadline": None,
            "followed_up": 0,
            "last_activity": datetime.now(timezone.utc).isoformat(),
        }

        self._items.append(item)
        self._save()
        return item

    def get(self, item_id: str) -> dict | None:
        """Get a single item by ID."""
        for item in self._items:
            if item["id"] == item_id:
                return item
        return None

    def list(
        self,
        status: str = None,
        category: str = None,
        include_archived: bool = False,
        sort_by: str = "captured_at",
        sort_desc: bool = True,
    ) -> list[dict]:
        """
        List items with optional filters.

        Args:
            status: Filter by status (pending/completed/dropped/archived)
            category: Filter by category
            include_archived: Include archived items
            sort_by: Field to sort by (captured_at, last_activity, etc.)
            sort_desc: Sort descending (newest first) if True

        Returns: Filtered and sorted list
        """
        items = self._items

        # Filter
        if status:
            items = [i for i in items if i.get("status") == status]
        if not include_archived:
            items = [i for i in items if i.get("status") != "archived"]
        if category:
            items = [i for i in items if i.get("category") == category]

        # Sort
        reverse = sort_desc
        items = sorted(items, key=lambda i: i.get(sort_by, ""), reverse=reverse)
        return items

    def update_status(self, item_id: str, new_status: str) -> dict | None:
        """Update item status. Valid: pending, completed, dropped, archived."""
        valid_statuses = {"pending", "completed", "dropped", "archived"}
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}. Must be one of {valid_statuses}")

        item = self.get(item_id)
        if not item:
            return None

        item["status"] = new_status
        item["last_activity"] = datetime.now(timezone.utc).isoformat()
        if new_status == "completed":
            item["completed_at"] = datetime.now(timezone.utc).isoformat()

        self._save()
        return item

    def set_deadline(self, item_id: str, deadline: str | datetime) -> dict | None:
        """Attach a deadline to an item."""
        item = self.get(item_id)
        if not item:
            return None

        if isinstance(deadline, datetime):
            deadline = deadline.isoformat()

        item["deadline"] = deadline
        item["last_activity"] = datetime.now(timezone.utc).isoformat()
        if item["status"] == "pending":
            item["status"] = "scheduled"

        self._save()
        return item

    def recategorize(self, item_id: str, new_category: str) -> dict | None:
        """Recategorize an item (also learns the correction)."""
        item = self.get(item_id)
        if not item:
            return None

        self.categorizer.learn(item["text"], new_category)
        item["category"] = new_category
        item["last_activity"] = datetime.now(timezone.utc).isoformat()
        self._save()
        return item

    def remove(self, item_id: str) -> bool:
        """Permanently delete an item."""
        initial_len = len(self._items)
        self._items = [i for i in self._items if i["id"] != item_id]
        if len(self._items) < initial_len:
            self._save()
            return True
        return False

    # ─────────────────────── Smart Archive ───────────────────────

    def smart_archive(
        self,
        flag_days: int = 90,
        auto_archive_days: int = 180,
    ) -> dict:
        """
        Run smart archive sweep.

        1. Flag items with no activity for `flag_days` days
        2. Auto-archive items with no activity for `auto_archive_days` days

        Returns summary of what happened.
        """
        now = datetime.now(timezone.utc)
        flagged = []
        archived = []

        for item in self._items:
            if item["status"] not in ("pending", "scheduled"):
                continue

            last_activity = self._parse_iso(item.get("last_activity", ""))
            if last_activity is None:
                continue

            days_inactive = (now - last_activity).days

            if days_inactive >= auto_archive_days:
                old_status = item["status"]
                item["status"] = "archived"
                item["last_activity"] = now.isoformat()
                item["archive_reason"] = f"auto-archived after {days_inactive} days inactive"
                archived.append({
                    "id": item["id"],
                    "text": item["text"],
                    "days_inactive": days_inactive,
                    "old_status": old_status,
                })

            elif days_inactive >= flag_days:
                flagged.append({
                    "id": item["id"],
                    "text": item["text"],
                    "days_inactive": days_inactive,
                })

        self._save()

        return {
            "flagged": flagged,
            "archived": archived,
            "flag_threshold_days": flag_days,
            "archive_threshold_days": auto_archive_days,
            "run_at": now.isoformat(),
        }

    def recover(self, item_id: str) -> dict | None:
        """Recover an archived item back to pending."""
        item = self.get(item_id)
        if not item or item["status"] != "archived":
            return None
        item["status"] = "pending"
        item["last_activity"] = datetime.now(timezone.utc).isoformat()
        item.pop("archive_reason", None)
        self._save()
        return item

    # ─────────────────────── Stats ───────────────────────

    def stats(self) -> dict:
        """Get summary statistics."""
        total = len(self._items)
        by_status = {}
        by_category = {}
        completion_rate = 0.0

        for item in self._items:
            s = item.get("status", "unknown")
            by_status[s] = by_status.get(s, 0) + 1

            c = item.get("category", "other")
            by_category[c] = by_category.get(c, 0) + 1

        completed = by_status.get("completed", 0)
        non_archived = total - by_status.get("archived", 0) - by_status.get("dropped", 0)
        if total > 0:
            completion_rate = round(completed / total * 100, 1)

        return {
            "total": total,
            "by_status": by_status,
            "by_category": by_category,
            "completed": completed,
            "pending": by_status.get("pending", 0) + by_status.get("scheduled", 0),
            "archived": by_status.get("archived", 0),
            "dropped": by_status.get("dropped", 0),
            "completion_rate_pct": completion_rate,
        }

    # ─────────────────────── Export ───────────────────────

    def export(self, fmt: str = "json") -> str:
        """
        Export data in various formats.

        Args:
            fmt: "json", "csv", "markdown", or "md"

        Returns: Formatted string
        """
        if fmt == "json":
            return json.dumps(self._items, ensure_ascii=False, indent=2)

        if fmt in ("csv",):
            import csv
            import io
            output = io.StringIO()
            if not self._items:
                return ""
            writer = csv.DictWriter(output, fieldnames=self._items[0].keys())
            writer.writeheader()
            writer.writerows(self._items)
            return output.getvalue()

        if fmt in ("markdown", "md"):
            lines = ["# Next-Time Export\n", f"*Exported: {datetime.now().isoformat()}*\n"]
            lines.append(f"**Total items: {len(self._items)}**\n")
            for item in self._items:
                emoji = self.categorizer.get_emoji(item.get("category", "other"))
                status_icon = {
                    "pending": "⏳",
                    "completed": "✅",
                    "dropped": "🗑️",
                    "archived": "📦",
                    "scheduled": "📅",
                }.get(item.get("status", ""), "❓")
                lines.append(f"\n---\n### {status_icon} {emoji} {item.get('text', '')}")
                lines.append(f"- **ID:** `{item['id']}`")
                lines.append(f"- **Status:** {item.get('status', '?')}")
                lines.append(f"- **Category:** {item.get('category', '?')}")
                lines.append(f"- **Captured:** {item.get('captured_at', '?')}")
                lines.append(f"- **Source:** {item.get('source', '?')}")
                if item.get("context", {}).get("participants"):
                    p = ", ".join(item["context"]["participants"])
                    lines.append(f"- **With:** {p}")
            return "\n".join(lines)

        raise ValueError(f"Unsupported format: {fmt}")

    # ─────────────────────── Internal ───────────────────────

    def _next_id(self) -> str:
        existing = {item["id"] for item in self._items}
        n = 1
        while True:
            item_id = f"nt-{n:03d}"
            if item_id not in existing:
                return item_id
            n += 1

    def _load(self):
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                self._items = json.load(f)
        else:
            self._items = []

    def _save(self):
        # Atomic write: write to temp, then rename
        temp_path = self.path.with_suffix(".json.tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self._items, f, ensure_ascii=False, indent=2)
        shutil.move(str(temp_path), str(self.path))

    def _parse_iso(self, iso_str: str) -> datetime | None:
        try:
            return datetime.fromisoformat(iso_str)
        except (ValueError, TypeError):
            return None


# Quick test
if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        t = Tracker(path=os.path.join(tmp, "test.json"))

        t.add("下次試中環間新拉麵店", source="telegram:test", category="food")
        t.add("someday go to japan", source="telegram:test")
        t.add("다음에 그 영화 봐야지", source="telegram:test")

        print("=== All items ===")
        for item in t.list():
            emoji = t.categorizer.get_emoji(item["category"])
            print(f"  {emoji} [{item['status']}] {item['id']}: {item['text']}")

        print("\n=== Stats ===")
        print(json.dumps(t.stats(), indent=2))

        print("\n=== Smart Archive ===")
        result = t.smart_archive(flag_days=0, auto_archive_days=0)
        print(json.dumps(result, indent=2))