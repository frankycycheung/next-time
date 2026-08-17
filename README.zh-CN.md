<p align="center">
  <img src="https://img.shields.io/badge/语言-10+-blue" alt="Languages">
  <img src="https://img.shields.io/badge/代理-Claude%20Code%20%C2%B7%20Cursor%20%C2%B7%20Copilot%20%C2%B7%20Codex-green" alt="Agents">
  <img src="https://img.shields.io/badge/许可-MIT-yellow" alt="License">
</p>

<h1 align="center">⏰ Next-Time</h1>
<h3 align="center">「下次再说」— 世界上最危险的四个字。</h3>

<p align="center">
  <b>Next-Time</b> 是一个由 AI 代理驱动的个人追踪工具，记录你所有说过「下次…」、「有机会…」、「改天…」的事项。
  <br>
  它会保存对话背景、自动分类、定期跟进，让你对自己说过的话负责。
</p>

---

## ✨ 功能特色

- **🌍 支持 10+ 种语言** — 英文、中文、日文、韩文、西班牙文、法文、德文、泰文、越南文、葡萄牙文、俄文等。欢迎社区新增。
- **🧠 通用代理规格** — 把 [`NEXT_TIME.md`](NEXT_TIME.md) 放入任何项目根目录，任何 AI 编程代理（Claude Code、Cursor、Copilot、Codex、Gemini Code Assist）都能自动理解如何使用。
- **💬 对话背景记录** — 不只记下「做什么」，还记得「为什么」。保存触发事件前后的对话内容，几个月后回顾时仍然清楚当时的来龙去脉。
- **🏷️ 自动分类** — AI 自动标记为 🍜 饮食、✈️ 旅行、💻 工作、📚 学习、🎮 兴趣、❤️ 感情等类别。会从你的修正中学习。
- **📦 智能归档** — 90 天无活动的项目会被标记提醒，180 天无活动自动归档。不会有项目永远石沉大海。
- **📊 每周回顾** — 自动生成待办事项摘要，提供具体建议：`done`（完成）、`drop`（放弃）、`schedule`（设定时限）。
- **🎯 命令行优先** — 轻量 Python CLI，无需重型依赖，任何环境都能执行。
- **🔌 Hermes 集成** — 原生支持 [Hermes Agent](https://hermes-agent.nousresearch.com)。

## 🚀 快速开始

### 1. 命令行（无需代理，直接使用）

```bash
# 下载项目
git clone https://github.com/frankycycheung/next-time.git
cd next-time

# 记录一件事
./standalone/next-time add "下次试中环那家拉面店"
# ✓ Saved: 🍜 下次试中环那家拉面店 [nt-001]

# 任何语言都可以
./standalone/next-time add "next time try that ramen place in Causeway Bay"
# ✓ Saved: 🍜 next time try that ramen place in Causeway Bay [nt-002]

./standalone/next-time add "今度ジムに行く"
# ✓ Saved: 🏥 今度ジムに行く [nt-003]

# 查看待办清单
./standalone/next-time list

# 标记完成
./standalone/next-time done nt-001

# 执行智能归档
./standalone/next-time archive

# 查看统计
./standalone/next-time stats
```

### 2. 作为通用代理指令

把 [`NEXT_TIME.md`](NEXT_TIME.md) 放到任何项目根目录，你的 AI 编程代理就会自动懂得如何记录和管理「下次」事项。

### 3. 作为 Hermes Agent 技能

```bash
hermes skill install agents/hermes-skill/SKILL.md
```

之后就可以在对话中自然使用：

> *你：*「下次带朋友去大屿山看日落🌅」
> *Agent：*「✓ Saved: ❤️ 下次带朋友去大屿山看日落 [nt-004]」

## 📋 指令一览

| 指令 | 说明 |
|---|---|
| `list` | 显示待办项目 |
| `list --all` | 显示所有项目（包括已归档） |
| `list --category food` | 按类别筛选 |
| `done <编号>` | 标记为已完成 |
| `drop <编号>` | 永久删除 |
| `schedule <编号> <日期>` | 设定截止日期 |
| `add <文字>` | 手动记录 |
| `archive` | 执行智能归档 |
| `recover <编号>` | 还原已归档项目 |
| `stats` | 完成率统计 |
| `export json\|csv\|md` | 导出数据 |

## 🗂️ 项目结构

```
next-time/
├── NEXT_TIME.md              # 通用代理指令（任何 AI 代理适用）
├── README.md                 # 英文说明
├── README.zh-TW.md           # 繁体中文说明
├── README.zh-CN.md           # 简体中文说明
├── LICENSE
│
├── core/
│   ├── patterns.json         # 多语言触发模式（10+ 种语言）
│   ├── detector.py           # 模式侦测 + LLM 后备
│   ├── tracker.py            # CRUD + 智能归档 + 统计 + 导出
│   ├── categorizer.py        # 自动分类 + 用户修正学习
│   └── context.py            # 对话背景捕捉
│
├── agents/
│   ├── hermes-skill/
│   │   └── SKILL.md          # Hermes Agent 集成
│   └── ...                   # 欢迎新增更多代理！
│
├── standalone/
│   └── next-time             # CLI 入口（无依赖）
│
├── integrations/
│   ├── google_calendar.py    # 项目日程 → 日历
│   ├── todoist_sync.py       # 同步至 Todoist
│   └── notion_export.py      # 导出至 Notion
│
├── web/                      # 简易仪表板（可选）
├── tests/                    # pytest 测试
└── example_data/             # 示例数据
```

## 🧪 运行测试

```bash
python -m pytest tests/ -v
```

## 🤝 如何贡献

- **新增语言：** 编辑 `core/patterns.json`，加入该语言的触发短语即可。
- **新增类别：** 编辑 `core/categorizer.py`，加入关键字和表情符号。
- **新增集成：** 放到 `integrations/` 目录，开一个 Pull Request。
- **代理适配：** 建立 `agents/<名称>/` 文件夹，附上安装说明。

## 📖 为什么要做这个工具？

每个人每个月都会说好几十次「下次」。研究显示，未被记录的延期意图**完成率不足 10%**。这个工具不是要让你难堪，而是想提醒你——有些事值得被认真对待，值得拥有第二次「下次」。

## 🔗 相关链接

- [Hermes Agent](https://hermes-agent.nousresearch.com)
- [NEXT_TIME.md 规格](NEXT_TIME.md) — 通用代理接口
- [语言模式文件](core/patterns.json) — 新增你的语言

---