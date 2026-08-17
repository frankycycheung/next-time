<p align="center">
  <img src="https://img.shields.io/badge/語言-10+-blue" alt="Languages">
  <img src="https://img.shields.io/badge/代理-Claude%20Code%20%C2%B7%20Cursor%20%C2%B7%20Copilot%20%C2%B7%20Codex-green" alt="Agents">
  <img src="https://img.shields.io/badge/許可-MIT-yellow" alt="License">
</p>

<h1 align="center">⏰ Next-Time</h1>
<h3 align="center">「下次先講」— 世界上最危險的四個字。</h3>

<p align="center">
  <b>Next-Time</b> 是一個由 AI 代理驅動的個人追蹤工具，記錄你所有說過「下次…」、「有機會…」、「得閒…」的事項。
  <br>
  它會保存對話背景、自動分類、定期跟進，讓你對自己說過的話負責。
</p>

---

## ✨ 功能特色

- **🌍 支援 10+ 種語言** — 英文、中文、日文、韓文、西班牙文、法文、德文、泰文、越南文、葡萄牙文、俄文等。歡迎社群新增。
- **🧠 通用代理規格** — 把 [`NEXT_TIME.md`](NEXT_TIME.md) 放入任何專案根目錄，任何 AI 編程代理（Claude Code、Cursor、Copilot、Codex、Gemini Code Assist）都能自動理解如何使用。
- **💬 對話背景記錄** — 不只記下「做什麼」，還記得「為什麼」。保存觸發事件前後的對話內容，幾個月後回顧時仍然清楚當時的來龍去脈。
- **🏷️ 自動分類** — AI 自動標記為 🍜 飲食、✈️ 旅行、💻 工作、📚 學習、🎮 興趣、❤️ 感情等類別。會從你的修正中學習。
- **📦 智能歸檔** — 90 天無活動的項目會被標記提醒，180 天無活動自動歸檔。不會有項目永遠石沉大海。
- **📊 每週回顧** — 自動生成待辦事項摘要，提供具體建議：`done`（完成）、`drop`（放棄）、`schedule`（設定時限）。
- **🎯 命令列優先** — 輕量 Python CLI，無需重型依賴，任何環境都能執行。
- **🔌 Hermes 整合** — 原生支援 [Hermes Agent](https://hermes-agent.nousresearch.com)。

## 🚀 快速開始

### 1. 命令列（無需代理，直接使用）

```bash
# 下載專案
git clone https://github.com/frankycycheung/next-time.git
cd next-time

# 記錄一件事
./standalone/next-time add "下次試中環間拉麵店"
# ✓ Saved: 🍜 下次試中環間拉麵店 [nt-001]

# 任何語言都可以
./standalone/next-time add "next time try that ramen place in Causeway Bay"
# ✓ Saved: 🍜 next time try that ramen place in Causeway Bay [nt-002]

./standalone/next-time add "今度ジムに行く"
# ✓ Saved: 🏥 今度ジムに行く [nt-003]

# 查看待辦清單
./standalone/next-time list

# 標記完成
./standalone/next-time done nt-001

# 執行智能歸檔
./standalone/next-time archive

# 查看統計
./standalone/next-time stats
```

### 2. 作為通用代理指令

把 [`NEXT_TIME.md`](NEXT_TIME.md) 放到任何專案根目錄，你的 AI 編程代理就會自動懂得如何記錄和管理「下次」事項。

### 3. 作為 Hermes Agent 技能

```bash
hermes skill install agents/hermes-skill/SKILL.md
```

之後就可以在對話中自然使用：

> *你：*「下次帶朋友去大嶼山睇日落🌅」
> *Agent：*「✓ Saved: ❤️ 下次帶朋友去大嶼山睇日落 [nt-004]」

## 📋 指令一覽

| 指令 | 說明 |
|---|---|
| `list` | 顯示待辦項目 |
| `list --all` | 顯示所有項目（包括已歸檔） |
| `list --category food` | 按類別篩選 |
| `done <編號>` | 標記為已完成 |
| `drop <編號>` | 永久刪除 |
| `schedule <編號> <日期>` | 設定截止日期 |
| `add <文字>` | 手動記錄 |
| `archive` | 執行智能歸檔 |
| `recover <編號>` | 還原已歸檔項目 |
| `stats` | 完成率統計 |
| `export json\|csv\|md` | 匯出資料 |

## 🗂️ 專案結構

```
next-time/
├── NEXT_TIME.md              # 通用代理指令（任何 AI 代理適用）
├── README.md                 # 英文說明
├── README.zh-TW.md           # 繁體中文說明
├── LICENSE
│
├── core/
│   ├── patterns.json         # 多語言觸發模式（10+ 種語言）
│   ├── detector.py           # 模式偵測 + LLM 備援
│   ├── tracker.py            # CRUD + 智能歸檔 + 統計 + 匯出
│   ├── categorizer.py        # 自動分類 + 使用者修正學習
│   └── context.py            # 對話背景捕捉
│
├── agents/
│   ├── hermes-skill/
│   │   └── SKILL.md          # Hermes Agent 整合
│   └── ...                   # 歡迎新增更多代理！
│
├── standalone/
│   └── next-time             # CLI 進入點（無依賴）
│
├── integrations/
│   ├── google_calendar.py    # 項目排程 → 日曆
│   ├── todoist_sync.py       # 同步至 Todoist
│   └── notion_export.py      # 匯出至 Notion
│
├── web/                      # 簡易儀表板（可選）
├── tests/                    # pytest 測試
└── example_data/             # 範例資料
```

## 🧪 執行測試

```bash
python -m pytest tests/ -v
```

## 🤝 如何貢獻

- **新增語言：** 編輯 `core/patterns.json`，加入該語言的觸發短語即可。
- **新增類別：** 編輯 `core/categorizer.py`，加入關鍵字和表情符號。
- **新增整合：** 放到 `integrations/` 目錄，開一個 Pull Request。
- **代理適配：** 建立 `agents/<名稱>/` 資料夾，附上安裝說明。

## 📖 為什麼要做這個工具？

每個人每個月都會說好幾十次「下次」。研究顯示，未被記錄的延期意圖**完成率不足 10%**。這個工具不是要讓你難堪，而是想提醒你——有些事值得被認真對待，值得擁有第二次「下次」。

## 🔗 相關連結

- [Hermes Agent](https://hermes-agent.nousresearch.com)
- [NEXT_TIME.md 規格](NEXT_TIME.md) — 通用代理介面
- [語言模式檔案](core/patterns.json) — 新增你的語言

---