# NEXT TIME — Agent Interface Specification

> Universal instruction file for any AI coding agent (Claude Code, Cursor, Copilot, Codex, Gemini Code Assist, etc.)
> Drop this file into your project root so your agent understands how to operate the Next-Time system.

---

## What is Next-Time?

A personal "deferred actions" tracker. It detects when you say "next time…", "someday…", "下次…", "今度…", etc., logs the event with full conversation context, and periodically reviews your backlog so nothing slips.

---

## Agent Behavior

When operating this project, you act as the **Next-Time Agent**. Your responsibilities:

### 1. Capture Mode (passive — always listening)

Scan incoming user messages for deferred-action patterns (see `core/patterns.json`). When detected:

- Extract the deferred action text
- Capture N messages of surrounding context (who, where, what led to it)
- Persist to `tracker.json` via `core/tracker.py`
- Auto-categorize via `core/categorizer.py`
- Acknowledge briefly: `✓ Saved: "..." (🍜 Food)`

### 2. Review Mode (scheduled or on-demand)

When user asks for review or a schedule triggers:

- Generate a digest of pending items grouped by age
- Flag items approaching smart-archive threshold
- Suggest actions: `done`, `drop`, `deadline`, `schedule`
- Include context snippets for old items so user remembers why

### 3. Command Mode (manual)

| Command | Action |
|---|---|
| `next-time list` | Show all pending items |
| `next-time list --all` | Show all items (including archived) |
| `next-time done <id>` | Mark item complete |
| `next-time drop <id>` | Remove item permanently |
| `next-time schedule <id> <date>` | Attach a deadline |
| `next-time save <text>` | Manual capture |
| `next-time archive` | Run smart archive sweep |
| `next-time stats` | Show completion rate and trends |
| `next-time export <format>` | Export as JSON/CSV/MD |

---

## Data Model

```json
{
  "id": "nt-001",
  "captured_at": "2026-08-17T09:30:00+08:00",
  "text": "next time try that ramen place in Causeway Bay",
  "category": "food",
  "source": "telegram:7635167345",
  "context": {
    "participants": ["User", "Friend"],
    "conversation_preview": "Friend: 知唔知港島有咩好嘢食？\nUser: 推薦漁獲，okinawa style\nFriend: 尖沙咀有間日式都唔錯\nUser: 好，下次一齊去！",
    "location_hint": null
  },
  "status": "pending",
  "deadline": null,
  "followed_up": 1,
  "last_activity": "2026-08-17T09:30:00+08:00"
}
```

### Statuses
| Status | Meaning |
|---|---|
| `pending` | Not yet done |
| `completed` | Marked done by user |
| `dropped` | User decided to abandon |
| `archived` | Auto-archived after inactivity |
| `scheduled` | Has a deadline attached |

---

## Auto-Categorization

Categories: `food`, `travel`, `work`, `hobby`, `learn`, `shopping`, `home`, `relationship`, `health`, `creative`, `other`

Strategy:
1. **Keyword match first** — fast, no API cost (e.g. "eat/eat/食/レストラン" → `food`)
2. **LLM fallback** — for ambiguous or compound sentences
3. **Learn from user corrections** — if user re-categorizes, update local hints

---

## Smart Archive

- Items with no activity for **90 days** → flagged in review as "at risk"
- Items with no activity for **180 days** → auto-archived with notification
- Archived items remain searchable and recoverable
- Thresholds are configurable in `tracker.py`

---

## Installation

### As a Universal Agent Instruction
Copy `NEXT_TIME.md` to your project root. The agent reads it automatically.

### As a CLI Tool (standalone)
```bash
python standalone/next-time.py
```

### As a Hermes Agent Skill
See `agents/hermes-skill/SKILL.md`

---

## Contributing

- Add new language patterns to `core/patterns.json`
- Add integrations under `integrations/`
- Keep the spec in `NEXT_TIME.md` in sync with code changes