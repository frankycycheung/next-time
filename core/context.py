"""
context.py — Capture surrounding conversation context for captured events.

When a deferred-action trigger is detected, this module grabs
N messages before and after to preserve why the user said it.
"""

import json
from datetime import datetime, timezone
from typing import Any


class ContextCapture:
    """
    Captures and formats conversation context around a trigger event.

    The context helps the user remember *why* and *with whom* they
    deferred the action when they review it weeks or months later.
    """

    def __init__(self, window_size: int = 5):
        """
        Args:
            window_size: Number of messages to capture before and after trigger.
                         Default 5. Final context will be up to (2*window_size + 1) msgs.
        """
        self.window_size = window_size

    def build_context(
        self,
        trigger_message: dict,
        history: list[dict],
        source: str,
        participants: list[str] | None = None,
    ) -> dict:
        """
        Build a context blob from a trigger message and surrounding history.

        Args:
            trigger_message: The message that triggered detection.
                Expected keys: "id", "text", "timestamp", "sender", "chat"
            history: Full message history (chronological).
                Each item has same shape as trigger_message.
            source: Platform identifier, e.g. "telegram:7635167345"
            participants: Optional list of participant names.
                Auto-derived from history if not provided.

        Returns:
            {
                "participants": [...],
                "before": "...",
                "after": "...",
                "conversation_preview": "...",
                "source": "...",
                "trigger_message_id": "...",
            }
        """
        trigger_idx = self._find_trigger_index(history, trigger_message)
        if trigger_idx is None:
            return self._minimal_context(trigger_message, source, participants)

        before = history[max(0, trigger_idx - self.window_size):trigger_idx]
        after = history[trigger_idx + 1:trigger_idx + 1 + self.window_size]

        # Derive participants if not provided
        if participants is None:
            participants = list(dict.fromkeys(
                m.get("sender", "Unknown") for m in before + [trigger_message] + after
            ))

        context = {
            "participants": participants,
            "before": self._messages_to_text(before),
            "after": self._messages_to_text(after),
            "conversation_preview": self._messages_to_text(before + [trigger_message] + after),
            "source": source,
            "trigger_message_id": trigger_message.get("id", ""),
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }

        return context

    def _find_trigger_index(self, history: list[dict], trigger: dict) -> int | None:
        """Find the trigger message in the history list."""
        trigger_id = trigger.get("id")
        for i, msg in enumerate(history):
            if msg.get("id") and trigger_id and msg["id"] == trigger_id:
                return i
        # Fallback: match by text + sender proximity
        trigger_text = trigger.get("text", "")
        trigger_sender = trigger.get("sender", "")
        for i, msg in enumerate(history):
            if msg.get("text") == trigger_text and msg.get("sender") == trigger_sender:
                return i
        return None

    def _messages_to_text(self, messages: list[dict]) -> str:
        """Format a list of messages into readable text."""
        lines = []
        for msg in messages:
            sender = msg.get("sender", "Unknown")
            text = msg.get("text", "")
            timestamp = msg.get("timestamp", "")
            ts = ""
            if timestamp:
                try:
                    ts = f"[{timestamp}] "
                except Exception:
                    pass
            lines.append(f"{ts}{sender}: {text}")
        return "\n".join(lines)

    def _minimal_context(
        self, trigger_message: dict, source: str, participants: list[str] | None
    ) -> dict:
        """Fallback context when trigger can't be placed in history."""
        return {
            "participants": participants or [trigger_message.get("sender", "Unknown")],
            "before": "",
            "after": "",
            "conversation_preview": trigger_message.get("text", ""),
            "source": source,
            "trigger_message_id": trigger_message.get("id", ""),
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "note": "Minimal context — trigger not found in provided history",
        }

    def to_json(self, context: dict) -> str:
        """Serialize context to JSON for storage."""
        return json.dumps(context, ensure_ascii=False, indent=2)

    @staticmethod
    def format_review_item(context: dict) -> str:
        """
        Format a context blob for human-readable review display.
        Used in weekly digests and list views.
        """
        lines = []
        participants = ", ".join(context.get("participants", []))
        source = context.get("source", "unknown")
        preview = context.get("conversation_preview", "")

        if participants:
            lines.append(f"👥 With: {participants}")
        lines.append(f"📱 Source: {source}")
        if preview:
            lines.append(f"💬 Context:\n{preview}")

        return "\n".join(lines)