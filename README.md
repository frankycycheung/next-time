<p align="center">
  <img src="https://img.shields.io/badge/languages-10+-blue" alt="Languages">
  <img src="https://img.shields.io/badge/agents-Claude%20Code%20%7C%20Cursor%20%7C%20Copilot%20%7C%20Codex-green" alt="Agents">
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
</p>

<h1 align="center">⏰ Next-Time</h1>
<h3 align="center">"I'll do it next time" — the most dangerous phrase in the world.</h3>

<p align="center">
  <b>Next-Time</b> is an agent-powered personal tracker for <i>every</i> "next time…", "someday…", "下次…", "今度…", "다음에…" you've ever said.
  <br>
  It captures the context, auto-categorizes, follows up, and holds you accountable.
</p>

---

## ✨ Features

- **🌍 10+ Languages** — English, Chinese, Japanese, Korean, Spanish, French, German, Thai, Vietnamese, Portuguese, Russian, and more. Community PRs welcome.
- **🧠 Universal Agent Spec** — Drop [`NEXT_TIME.md`](NEXT_TIME.md) into any project. Works with Claude Code, Cursor, Copilot, Codex, Gemini Code Assist — any AI coding agent.
- **💬 Context Capture** — Not just "what" but "why". Saves the surrounding conversation so you remember the *reason* months later.
- **🏷️ Auto-Categorization** — AI tags items as 🍜 Food, ✈️ Travel, 💻 Work, 📚 Learn, 🎮 Hobby, ❤️ Relationship, and more. Learns from your corrections.
- **📦 Smart Archive** — Items untouched for 90 days get flagged. Items untouched for 180 days auto-archive. Nothing gets buried forever.
- **📊 Weekly Reviews** — Automated digests of your backlog with suggested actions: `done`, `drop`, `schedule`.
- **🎯 CLI-first** — Lightweight Python CLI. No heavy dependencies. Runs anywhere.
- **🔌 Hermes Skill** — Native integration with [Hermes Agent](https://hermes-agent.nousresearch.com).

## 🚀 Quick Start

### 1. CLI (standalone — no agent required)

```bash
# Clone the repo
git clone https://github.com/frankycycheung/next-time.git
cd next-time

# Capture a deferred action
./standalone/next-time add "next time try that ramen place in Causeway Bay"
# ✓ Saved: 🍜 next time try that ramen place in Causeway Bay [nt-001]

# Add in any language
./standalone/next-time add "下次帶朋友去大嶼山睇日落"
# ✓ Saved: ❤️ 下次帶朋友去大嶼山睇日落 [nt-002]

./standalone/next-time add "今度ジムに行く"
# ✓ Saved: 🏥 今度ジムに行く [nt-003]

# List pending items
./standalone/next-time list

# Mark as done
./standalone/next-time done nt-001

# Run smart archive
./standalone/next-time archive

# See your statistics
./standalone/next-time stats
```

### 2. As a Universal Agent Instruction

Drop [`NEXT_TIME.md`](NEXT_TIME.md) into any project root. Your AI coding agent will automatically understand how to capture and manage "next time" items.

### 3. As a Hermes Agent Skill

```bash
hermes skill install agents/hermes-skill/SKILL.md
```

Then use the commands naturally in chat:

> *You:* "下次試中環間拉麵店"
> *Agent:* "✓ Saved: 🍜 下次試中環間拉麵店 [nt-004]"

## 📋 Commands

| Command | Description |
|---|---|
| `list` | Show pending items |
| `list --all` | Show all items (including archived) |
| `list --category food` | Filter by category |
| `done <id>` | Mark item complete |
| `drop <id>` | Remove permanently |
| `schedule <id> <date>` | Attach a deadline |
| `add <text>` | Manual capture |
| `archive` | Run smart archive sweep |
| `recover <id>` | Recover archived item |
| `stats` | Completion analytics |
| `export json\|csv\|md` | Export your data |

## 🗂️ Project Structure

```
next-time/
├── NEXT_TIME.md              # Universal agent instruction (any AI agent)
├── README.md                 # English
├── README.zh-TW.md           # Traditional Chinese
├── README.zh-CN.md           # Simplified Chinese
├── LICENSE
│
├── core/
│   ├── patterns.json         # Multi-lang trigger patterns (10+ languages)
│   ├── detector.py           # Pattern detection + LLM fallback
│   ├── tracker.py            # CRUD + smart archive + stats + export
│   ├── categorizer.py        # Auto-tagging with user-correction learning
│   └── context.py            # Conversation context capture
│
├── agents/
│   ├── hermes-skill/
│   │   └── SKILL.md          # Hermes Agent integration
│   └── ...                   # More agent adapters welcome!
│
├── standalone/
│   └── next-time             # CLI entry point (no deps)
│
├── integrations/
│   ├── google_calendar.py    # Schedule items → calendar
│   ├── todoist_sync.py       # Sync with Todoist
│   └── notion_export.py      # Export to Notion
│
├── web/                      # Simple dashboard (optional)
├── tests/                    # pytest suite
└── example_data/             # Sample data to explore
```

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

## 🤝 Contributing

- **Add a language:** Edit `core/patterns.json` with trigger phrases for your language. That's it.
- **Add a category:** Edit `core/categorizer.py` with keywords + emoji.
- **Add an integration:** Drop it in `integrations/` and open a PR.
- **Agent adapter:** Create a `agents/<name>/` folder with setup instructions.

## 📖 Why?

We all say "next time" dozens of times a month. Studies show that deferred intentions have a **< 10% follow-through rate** when unrecorded. This tool doesn't shame you — it *reminds* you. Some things deserve a second "next time".

## 🔗 Links

- [Hermes Agent](https://hermes-agent.nousresearch.com)
- [NEXT_TIME.md spec](NEXT_TIME.md) — Universal agent interface
- [Pattern file](core/patterns.json) — Add your language

---