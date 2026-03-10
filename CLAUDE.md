# Master's Program Search Project

## Project Architecture & Rules
- **State Management:** This project uses `.state/pipeline-state.md` as the ultimate source of truth for progress. Never execute a step if it is already checked `[x]`. 
- **Context:** `master-context.md` holds the user's criteria and the required extraction schema.
- **Worker Isolation:** The main orchestrator must never browse university websites directly. It must delegate discovery to `program-finder` and extraction to `program-analyzer`.
- **Data Format:** All extracted data must be saved as strict JSON files in the `.state/extraction/` directory using the filename format: `universityname-programname.json`.