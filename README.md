# 🎓 GradScout

**An AI-powered Claude Code skill that researches master's programs for you.**

Tell it your countries, your interests, your criteria — and it autonomously browses university websites, gathers program details, and delivers a structured Excel spreadsheet.

> **What's a Claude Code skill?** It's a reusable set of instructions that teaches [Claude Code](https://docs.anthropic.com/en/docs/claude-code) how to perform a complex, multi-step task. Install this skill once, and Claude becomes your personal graduate school researcher.

---

## Usage

Open Claude Code in the project directory and run the slash command:

```
You: /search-masters

Claude: I'll help you search for master's programs. Let me ask a few questions:

  → What countries are you interested in?
  → What are your interest keywords? (e.g., "AI", "Computer Science", "Robotics")
  → Any topics to exclude? (e.g., "Biology", "Management")
  → What's your university ranking cutoff? (QS/THE)
  → Any custom data points you want to extract?
```

That's it. You define **what you're looking for**, and the agent handles the rest:

- 🌍 **Countries** — Search in Germany, Netherlands, Sweden, or anywhere
- 🔑 **Interest keywords** — "AI", "Data Engineering", "Robotics" — whatever you're studying
- 🚫 **Negative keywords** — Exclude "Biology", "Healthcare", "MBA" to keep results clean
- 📊 **Custom criteria** — Want to know the language of instruction? Scholarship availability? Just ask — the schema is fully dynamic
- 🏫 **Ranking cutoff** — Only look at universities within your QS/THE threshold

### What You Get

A complete `master_programs_masterlist.xlsx` with every matching program, fully filled with the data points you asked for — deadlines, tuition, housing, and whatever custom fields you added.

### Updating Your Search

Changed your mind? Just tell the agent:

```
You: Add keyword: Robotics
You: Add country: Netherlands
You: Add a field for scholarship availability
```

The agent figures out what needs to be re-processed and what can be kept, then picks up where it left off. No need to start from scratch.

---

## How It Works

```
┌─────────────────────────────┐
│  You tell Claude what you   │
│  want (keywords, countries, │
│  custom fields)             │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  🎯  Orchestrator           │
│  Finds qualifying           │
│  universities, manages      │
│  state, dispatches agents   │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  🔍  Finder Agent           │
│  Browses each university's  │
│  website, finds matching    │
│  program URLs               │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  📋  Analyzer Agent         │
│  Visits each program page,  │
│  extracts your requested    │
│  data points into JSON      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  📊  Excel Compiler         │
│  Merges all JSON results    │
│  into a single spreadsheet  │
└─────────────────────────────┘
```

Every step is checkpointed in `.state/pipeline-state.md`. If anything crashes or you close your terminal, just run the skill again — it resumes exactly where it left off.

---

## Setup

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- Node.js & npx
- Python 3.x

### Installation

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/gradscout.git
cd gradscout
```

**2. Add browser automation**
```bash
claude mcp add playwright -- npx -y @playwright/mcp@latest
```

**3. Install Python dependencies**
```bash
pip install pandas openpyxl
```

**4. Run it**
```bash
claude
```
Then type: `/search-masters`

---

## Project Structure

```
gradscout/
├── .claude/
│   ├── agents/
│   │   ├── program-finder.md      # 🔍 Discovers programs on university sites
│   │   └── program-analyzer.md    # 📋 Extracts detailed data from each program
│   └── skills/
│       └── search-masters/
│           └── SKILL.md           # 🎯 Main orchestrator skill
├── .state/                        # Checkpoint state (auto-managed)
│   ├── discovery/                 # Found program URLs (JSON)
│   └── extraction/                # Extracted program data (JSON)
├── CLAUDE.md                      # Project rules for Claude
├── compile_results.py             # Merges JSONs → Excel
└── README.md
```

---

## Keyword Filtering: How It Keeps Results Clean

The agents use semantic matching, not just text search. This means searching for "AI" could pull in *"Healthcare AI"* or *"AI in Business"*. That's where negative keywords come in.

| Interest Keywords | Negative Keywords | Program | Result |
|---|---|---|---|
| CS, AI, ML | Biology, Healthcare, Management | MSc Computer Science | ✅ Kept |
| CS, AI, ML | Biology, Healthcare, Management | MSc Data Engineering | ✅ Kept |
| CS, AI, ML | Biology, Healthcare, Management | MSc Management & Data Science | ❌ Rejected |
| CS, AI, ML | Biology, Healthcare, Management | MSc Computational Biology | ❌ Rejected |

---

## License

MIT
