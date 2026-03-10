
# Autonomous Master's Program Search Pipeline

A robust, fault-tolerant, parallel-processing AI agent swarm built with Claude Code. This pipeline autonomously discovers, analyzes, and extracts master's degree program requirements from dynamic university websites and compiles them into a structured Excel spreadsheet.

## Architecture Overview

This project uses a **Master-Worker (Orchestrator-Subagent) architecture** combined with a **Stateful ETL (Extract, Transform, Load) Pipeline**.

1. **The Orchestrator (`/search-masters`):** The manager agent. It interviews the user to establish criteria, manages the state checkpointing, and delegates tasks to the worker swarm.
2. **The Finder Subagent (`program-finder`):** The scout. It uses headless browser automation and strict semantic filtering to navigate university directories and find exactly the right program URLs.
3. **The Analyzer Subagent (`program-analyzer`):** The data extractor. It receives a specific program URL and an empty JSON template, scrapes the page (and falls back to Google if needed), and perfectly fills out the requested data points.
4. **State Management (`.state/pipeline-state.md`):** A strict Write-Ahead Log (WAL). The orchestrator updates a markdown checklist as it works. If the pipeline is interrupted, the swarm instantly resumes exactly where it left off.

## How Keyword Filtering Works (Positive vs. Negative)

Because LLMs understand semantic relationships, searching for "AI" might accidentally pull in "Master's in Healthcare AI" or "Business Analytics with AI". To prevent your final spreadsheet from filling up with irrelevant programs, the pipeline uses a strict Bouncer System.

During the intake interview, you will provide two sets of keywords:
* **Interest Keywords (Positive):** The core topics you want (e.g., "Computer Science", "AI", "Machine Learning", "Data Engineering").
* **Negative Keywords (Exclusion):** The topics that immediately disqualify a program, even if it contains an Interest Keyword.

**Real-World Example:**
If your Interest Keywords are `CS, AI, ML` and your Negative Keywords are `Biology, Healthcare, Management, Education`:
* *MSc Computer Science* -> **Kept** * *MSc Data Engineering* -> **Kept** * *MSc Management and Data Science* -> **Rejected** (Triggers the "Management" negative keyword)
* *MSc Computational Biology* -> **Rejected** (Triggers the "Biology" negative keyword)

## Prerequisites

To run this pipeline, you need the following installed on your system:

- **Claude Code:** The official CLI tool from Anthropic.
- **Node.js & npx:** Required to run the Model Context Protocol (MCP) server.
- **Python 3.x:** For the final data compilation script (`pandas` and `openpyxl`).

## Setup & Installation

**1. Initialize the Project Environment**
Create your project directory and navigate into it:
```bash
mkdir Masters_Search && cd Masters_Search

```

**2. Enable Browser Automation (MCP)**
Give Claude Code the ability to browse the web using the official Playwright MCP server:

```bash
claude mcp add playwright -- npx -y @playwright/mcp

```

**3. Install Python Dependencies**

```bash
pip install pandas openpyxl

```

**4. Build the Directory Structure**
Ensure your project matches this exact structure:

```text
Masters_Search/
├── .claude/
│   ├── agents/
│   │   ├── program-finder.md
│   │   └── program-analyzer.md
│   └── skills/
│       └── search-masters/
│           └── SKILL.md
├── .state/
│   ├── discovery/
│   └── extraction/
├── CLAUDE.md
├── compile_results.py
└── README.md

```

## How to Run

1. Open your terminal in the `Masters_Search` directory.
2. Launch Claude Code:
```bash
claude

```


3. Trigger the main orchestrator skill:
```bash
/search-masters

```


4. **The Intake Interview:** Claude will pause and ask for your Target Countries, Rank Cutoffs, Interest Keywords, **Negative Keywords**, and the specific Data Points you want to extract.
5. **Watch it Work:** Open `.state/pipeline-state.md` in your code editor to watch the checkboxes tick off as the parallel agents scrape the web.
6. **The Result:** Once all checkboxes are complete, the pipeline will automatically output `master_programs_masterlist.xlsx` in your root directory.
