---
name: search-masters
description: Orchestrates the master's program search pipeline using Crawl4AI-backed web crawling. Use when the user says "find master programs", "research universities", "run the master search", "update my criteria", "add a keyword", "add a country", "change my search", or "modify my filters".
disable-model-invocation: true
---
# Master's Search Orchestrator

## Operating Rules
- Quality is more important than speed.
- Once intake or criteria-update confirmation is complete, continue autonomously.
- Use `.state/pipeline-state.md` as the source of truth.
- Claude subagents have fixed startup cost. Prefer short task payloads and batch work where possible.
- `program-finder` and `program-analyzer` are crawl-only workers. They must use Bash plus `python3 fetch_page.py` only, not built-in web search/fetch tools or `playwright-cli`.

## Workflow

### Step 0: Dependency Validation
Run these before anything else:
1. `python3 -c "import crawl4ai; print(getattr(crawl4ai, '__version__', 'installed'))"`
2. `python3 -c "import os, json, pandas, openpyxl; print('Dependencies OK')"`
3. `python3 fetch_page.py "https://example.com" --max-chars=200`
4. Ensure `.state/discovery` and `.state/extraction` exist.

If Crawl4AI is missing, tell the user to run `pip install crawl4ai` and `crawl4ai-setup`.
If `pandas` or `openpyxl` is missing, tell the user to install them.
Do not proceed until all checks pass.

### Step 1: Recovery
If `.state/pipeline-state.md` does not exist, create it with:
- `[ ] Intake`
- `[ ] Context Generation`
- `[ ] Baseline Search`

If it exists, read it and `master-context.md`.
- If the user is changing criteria, go to Step 1.5.
- Otherwise resume from the first incomplete stage:
  - `[ ][ ]` university -> Step 4
  - `[x][ ]` university -> Step 5
  - all `[x][x]` -> Step 6
  - unchecked Phase 1 item -> resume that step

Per-program status lives in `.state/discovery/*.json` under `"status"`.

### Step 1.5: Criteria Update
Show the current contents of `master-context.md`, ask what changed, classify it, explain what will be invalidated, and ask for confirmation.

Tiers:
- Tier 1, additive:
  - add country -> keep existing work; extend Step 3 onward
  - add negative keyword -> remove matching programs from discovery and delete matching extraction files
  - remove country -> remove those universities and delete related files
- Tier 2, schema change:
  - delete all `.state/extraction/*.json`
  - reset every discovery program to `"pending"`
  - change every university from `[x][x]` or `[x][ ]` to `[x][ ]`
- Tier 3, interest-keyword change:
  - delete all `.state/discovery/*.json` and `.state/extraction/*.json`
  - reset universities to `[ ][ ]`
  - keep Phase 1 checked

After confirmation, update `master-context.md`, perform the invalidation, then return to Step 1.

### Step 2: Intake
Ask for:
- interest keywords
- negative keywords
- target countries
- rank cutoff

Present this default schema:
```json
{
  "program_url": "Instruction: The direct URL to the main program overview page. Example: 'https://www.tum.de/msc-computer-science'",
  "program_name": "Instruction: The official name of the degree. Example: 'MSc Computer Science'",
  "application_deadline": "Instruction: The exact date applications close for international students. Example: '2025-05-31'",
  "tuition_fee": "Instruction: The total cost of the entire program. Example: '1500 EUR/semester' or 'Free'",
  "housing_info": "Instruction: Indicate if housing is guaranteed and average rent. Example: 'No guarantee, ~600 EUR/month'",
  "scholarship_info": "Instruction: Available scholarships, eligibility, AND their website links. Example: 'Merit scholarship: 50% tuition waiver (https://tum.de/scholarships). Also: diversity scholarship.'"
}
```

Ask whether the user wants custom fields. Wait.
If they add or modify criteria, restate your understanding with a mock output example and get confirmation.
Then write `master-context.md`, including the rule that rankings must use only QS or THE, and mark Phase 1 complete.

### Step 3: Baseline Search
Use web search to find universities in the target countries.
Keep only universities inside the user's cutoff using QS or THE only.
Write them to `.state/pipeline-state.md` under `## Universities` as:
- `- [ ][ ] University Name (Country)`

### Step 4: Discovery Delegation
For universities with `[ ][ ]`:
1. Dispatch multiple `program-finder` subagents in parallel for universities with `[ ][ ]`.
2. Use the named `program-finder` subagent from `.claude/agents/program-finder.md`, not a generic `Agent`.
3. Batch universities into groups of 3 to 5 active subagents at a time.
4. Use session names like `uni-<sanitized-name>`.
5. Keep each task payload short: university name, country, official URL, keywords, negative keywords, session name, an `OUTPUT_PATH` in `.state/discovery/`, and a hard reminder to use `python3 fetch_page.py` only.
6. Require the finder to write its JSON result directly to `OUTPUT_PATH`.
7. After each discovery wave, run `python3 sync_pipeline_state.py` so `[ ][ ]` becomes `[x][ ]` automatically for completed discovery files.

### Step 5: Extraction Delegation
For universities with `[x][ ]`:
1. Ask the filesystem for the next chunk with:
   ```bash
   python3 get_pending_extraction_batch.py --limit=5
   ```
2. If the script returns `"done": true`, move to Step 6.
3. Use the named `program-analyzer` subagent from `.claude/agents/program-analyzer.md`, not a generic `Agent`.
4. Pass only:
   - `University Name`
   - shared `Descriptive JSON Schema`
   - `Programs: [{program_name, url, session_name, output_file}, ...]`
   - a hard reminder to use `python3 fetch_page.py` only
5. Dispatch one analyzer subagent for the returned chunk.
6. After each analyzer wave, run:
   ```bash
   python3 sync_state.py
   ```
7. Repeat Step 5 until `get_pending_extraction_batch.py` returns `"done": true`.

### Step 6: Compilation
When all universities are `[x][x]`, run:
```bash
python compile_results.py
```

## Failure Handling
- If a finder or analyzer fails critically, mark the relevant item failed and continue.
- Do not loop forever on a broken site or program.
