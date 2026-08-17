---
name: next-time
description: "Track 'next time' deferred actions across 10+ languages. Captures context, auto-categorizes, smart-archives, and reviews backlog."
---

# Next-Time

A personal deferred-actions tracker. Detects when you say "next time…", "someday…", "下次…", "今度…", etc., logs it with full conversation context, and periodically reviews your backlog.

## How It Works

1. **Capture** — Agent detects trigger phrases in your messages (10+ languages supported)
2. **Context** — Surrounding conversation is saved so you remember *why* later
3. **Categorize** — Auto-tags as 🍜 Food, ✈️ Travel, 💻 Work, 📚 Learn, etc.
4 **Archive** — Items untouched for 90d are flagged, 180d auto-archived
5. **Review** — Weekly digest of pending items with suggested actions

## Installation

```bash
hermes tools install
hermes skill install next-time
```

## Commands

| Command | Action |
|---|---|
| `next-time list` | Show pending items |
| `next-time list --all` | Show all items |
| `next-time done <id>` | Mark item complete |
| `next-time drop <id>` | Remove item |
| `next-time save <text>` | Manual capture |
| `next-time archive` | Run smart archive |
| `next-time stats` | Completion stats |
| `next-time export <format>` | Export (json/csv/md) |

## Cron Jobs

```yaml
# Weekly review — every Sunday 10:00 HKT
- schedule: "0 10 * * 0"
  prompt: "Run next-time weekly review and summarize pending items"
  deliver: "origin"

# Monthly stats — 1st of each month
- schedule: "0 9 1 * *"
  prompt: "Run next-time stats and share monthly report"
  deliver: "origin"
```

## Files

| Path | Purpose |
|---|---|
| `~/.next-time/tracker.json` | All captured items |
| `~/.next-time/user_hints.json` | Learned category corrections |

## Requirements

- Hermes Agent (any provider)
- Core: `core/detector.py`, `core/tracker.py`, `core/categorizer.py`, `core/context.py`

## See Also

- `NEXT_TIME.md` — Universal agent instruction file (for any AI agent, not just Hermes)
- `core/patterns.json` — Add new language patterns