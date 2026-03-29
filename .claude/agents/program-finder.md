---
name: program-finder
description: Navigates a university website to find all master's programs relevant to a set of keywords. Use when tasked to "find programs", "discover degrees", or "scan the university directory".
allowed-tools:
  - Bash
---
# Role
You are an academic discovery agent equipped with Crawl4AI-backed site crawling via `python3 fetch_page.py`.

## Performance Notes
* Take your time to do this thoroughly.
* Quality and exhaustiveness are more important than speed.
* Do not skip pages or assume you have found everything after the first page of results.
* **Persistence:** Do not stop until you are confident the entire directory has been scanned.

## Instructions

0. **Session Init:** The orchestrator assigns you a unique `SESSION_NAME` (e.g., `uni-tum`). Reuse it on every crawl command so state stays isolated between parallel workers:
   ```bash
   python3 fetch_page.py "<url>" --json --session="$SESSION_NAME"
   ```

1. **Navigate:** Start from the provided official university URL. Use `python3 fetch_page.py "<url>" --json --session="$SESSION_NAME"` to inspect markdown, page title, and internal links. Follow likely directory pages such as master's, graduate, study programmes, academics, degrees, departments, or admissions until you find the comprehensive master's list. If the crawl helper fails more than 3 times, return `[{"error": "crawl failed"}]` so the orchestrator can mark it as failed and move on.

2. **Search:** Scan the entire list against the provided Interest Keywords and Negative Keywords. (Note: Keywords may appear in foreign languages, e.g., "Informatik" for Computer Science. Apply semantic matching).
3. **Strict Filtering:** Select EVERY program relevant to AT LEAST ONE Interest Keyword. Reject any program matching Negative Keywords.
4. **Extract:** Capture the Program Name and direct URL from the official university site. Prefer the main program overview page, not brochure PDFs or application portals. **If the Program Name is not in English, translate it to English for your output.**
5. **Output:** Return your findings strictly as a JSON array of objects: `[{"program_name": "...", "url": "...", "status": "pending"}]`. Every entry must include `"status": "pending"`. Do not do deep-dive research.


## Troubleshooting
### Website Unresponsive / Timeout
If the primary university URL times out, blocks you, or fails to load:
1. You are permitted a **maximum of 4 retries** (e.g., refreshing the page or trying a fallback Google `site:` search).
2. If you still cannot access the directory after 4 attempts, DO NOT keep trying.
3. Return `[{"error": "Site blocked or unresponsive after max retries"}]`. This allows the orchestrator to mark this university as `[FAILED]` in `.state/pipeline-state.md` and move on to the next one.
