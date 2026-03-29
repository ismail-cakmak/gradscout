# Master's Program Search Project

## Project Architecture & Rules
- **State Management:** This project uses `.state/pipeline-state.md` as the ultimate source of truth for progress. Never execute a step if it is already checked `[x]`. 
- **Context:** `master-context.md` holds the user's criteria and the required extraction schema.
- **Worker Isolation:** The orchestrator delegates discovery to `program-finder` and extraction to `program-analyzer`. Each subagent gets a unique Crawl4AI session ID and reuses it through `python3 fetch_page.py --session=<session-name>`.
- **Parallel Execution:** Multiple subagents can run in parallel because each uses a separate Crawl4AI `session_id`.
- **Crawl Helper:** `fetch_page.py` is the canonical web access tool. It uses Crawl4AI to return markdown content plus discovered links from official university pages.
- **Data Format:** All extracted data must be saved as strict JSON files in the `.state/extraction/` directory using the filename format: `universityname-programname.json`.
