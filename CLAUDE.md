# Master's Program Search Project

## Project Architecture & Rules
- **State Management:** This project uses `.state/pipeline-state.md` as the ultimate source of truth for progress. Never execute a step if it is already checked `[x]`. 
- **Context:** `master-context.md` holds the user's criteria and the required extraction schema.
- **Worker Isolation:** The orchestrator delegates discovery to `program-finder` and extraction to `program-analyzer`. Each subagent runs its own isolated browser session using `playwright-cli -s=<session-name>`. The orchestrator assigns unique session names to each subagent.
- **Parallel Execution:** Multiple subagents can run in parallel because each uses a separate named session (`-s=` flag) with fully isolated cookies, tabs, and storage.
- **Visual Dashboard:** Run `playwright-cli show` to open a live dashboard that displays all running browser sessions.
- **Data Format:** All extracted data must be saved as strict JSON files in the `.state/extraction/` directory using the filename format: `universityname-programname.json`.