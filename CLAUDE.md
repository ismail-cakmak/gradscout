# Master's Program Search Project

## Project Architecture & Rules
- **State Management:** This project uses `.state/pipeline-state.md` as the ultimate source of truth for progress. Never execute a step if it is already checked `[x]`. 
- **Context:** `master-context.md` holds the user's criteria and the required extraction schema.
- **Worker Isolation:** The orchestrator delegates discovery to `program-finder` and extraction to `program-analyzer`. Each subagent gets a unique Crawl4AI session ID and reuses it through `python3 fetch_page.py --session=<session-name>`.
- **Worker Tool Policy:** `program-finder` and `program-analyzer` are crawl-only workers. They should use Bash plus `python3 fetch_page.py` only, not built-in WebSearch/WebFetch tools or `playwright-cli`.
- **Parallel Execution:** Multiple subagents can run in parallel because each uses a separate Crawl4AI `session_id`.
- **Spawn Cost:** Claude subagents have a fixed prompt/context cost before tool use. Prefer fewer, larger worker batches over one-worker-per-item. Keep task payloads short and have workers write results directly to disk.
- **Crawl Helper:** `fetch_page.py` is the canonical web access tool. It uses Crawl4AI to return markdown content plus discovered links from official university pages.
- **State Scripts:** Prefer `python3 get_pending_extraction_batch.py`, `python3 sync_state.py`, and `python3 sync_pipeline_state.py` over manual state bookkeeping in the orchestrator prompt.
- **Browser Runtime:** Activate `venv` before running crawl tooling. Use `PLAYWRIGHT_BROWSERS_PATH=.playwright` so Playwright and Patchright share the local browser install in this repo.
- **Data Format:** All extracted data must be saved as strict JSON files in the `.state/extraction/` directory using the filename format: `universityname-programname.json`.
