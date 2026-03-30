---
name: program-analyzer
description: Extracts one or more program records into strict JSON files using Crawl4AI-backed fetches.
allowed-tools:
  - Bash
---
Extract the provided data into the provided schema. Accuracy matters more than speed.

## Input Shape
You may receive either:
- one program: `Program Name`, `University Name`, `Direct URL`, `SESSION_NAME`, `Descriptive JSON Schema`
- a batch: `Programs`, where each item includes `program_name`, `url`, `session_name`, and optionally `output_file`, plus `University Name` and the shared `Descriptive JSON Schema`

## Rules
1. Process every assigned program. For batches, work sequentially in the same task.
2. Use Bash only. Do not use `WebSearch`, `WebFetch`, `Read`, `Fetch`, `playwright-cli`, or any other browser/search skill. All page access must go through `python3 fetch_page.py`.
3. Start with:
   ```bash
   python3 fetch_page.py "<Direct URL>"
   ```
4. If fields are missing, inspect official internal links with:
   ```bash
   python3 fetch_page.py "<Direct URL>" --json --session="$SESSION_NAME"
   ```
   In batch mode, use the current program item's `url` and `session_name`.
5. Follow only official university pages that help fill unresolved schema fields.
6. Limit follow-up fetches to 3 targeted pages per missing field. If still unresolved, use `"Not Listed"`.
7. Output all JSON values in English.
8. Replace schema instructions with actual values and save each result to the provided `output_file` when present. Otherwise save to `.state/extraction/universityname-programname.json` using lowercase and hyphens.
9. Do not print the full JSON to the conversation. Return only a short status summary for each processed program.

## Failure Handling
- If a fetch fails repeatedly, save the program with `"Not Listed"` for unresolved fields rather than looping.
- Do not exceed the assigned batch. Finish your programs, save the files, and stop.
