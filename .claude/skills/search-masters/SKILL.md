---
name: search-masters
description: Orchestrates the master's program search pipeline using browser automation. Use when the user says "find master programs", "research universities", "run the master search", "update my criteria", "add a keyword", "add a country", "change my search", or "modify my filters".
disable-model-invocation: true
---
# Master's Search Orchestrator

## Performance Notes
* Take your time to do this thoroughly.
* Quality is more important than speed.
* Do not skip validation steps.
* **Autonomy:** Once the pipeline is running (after Step 2 intake is confirmed), do NOT stop to ask the user "should I proceed?" or "would you like me to start?". Just execute the next step immediately. The only time you should pause for user input is during Step 2 (Intake) and Step 1.5 (Criteria Update). Everything else is fully autonomous.

## Workflow: Autonomous Master's Search

Execute these steps strictly in sequence. You must manage state using `.state/pipeline-state.md`.

### Step 0: Global Dependency Validation
*(Execute every time before Step 1)*

1. **Clean Up Stale Sessions:** Kill any leftover browser sessions from a previous run:
   ```bash
   playwright-cli close-all 2>/dev/null || true
   ```

2. **Playwright CLI Check:** Run:
   ```bash
   playwright-cli --version
   ```
   - **If it fails:** Try `npx playwright-cli --version`.
   - **If both fail:** Warn the user: "⚠️ The Playwright CLI is missing. Please install it: `npm install -g @playwright/cli` or use `npx @playwright/cli install --skills`."
   - **Do not proceed** until the CLI is confirmed working.
   
2. **Check Python Environment:** Use the `bash` tool to run: 
   `python3 -c "import os, json, pandas, openpyxl; print('Dependencies OK')"`
   - **If it fails:** Note which library is missing (likely `pandas` or `openpyxl`). 
   - **Action:** Tell the user: "⚠️ Python dependencies missing. Please run: `pip install pandas openpyxl`".
   - **Stop:** Do not proceed to Step 1 until the user confirms installation.

3. **Check Directory Structure:** Ensure `.state/discovery` and `.state/extraction` exist.
   - **Action:** If missing, run `mkdir -p .state/discovery .state/extraction`.

4. **Launch Visual Dashboard:** Open the Playwright CLI visual dashboard so the user can observe all parallel browser sessions in real time:
   ```bash
   playwright-cli show &
   ```
   This runs in the background and displays a live view of every running session. The user can watch the agents work and even step in if needed.

5. **Proceed:** Only if all checks pass, move to Step 1.


### Step 1: State Recovery & Initialization
Check if `.state/pipeline-state.md` exists. 
- If NO: This is a **fresh run**. Create it. Add Phase 1 checkboxes (`[ ] Intake`, `[ ] Context Generation`, `[ ] Baseline Search`). Skip Step 1.5 and go to Step 2.
- If YES: Read the file and also read `master-context.md`.
  - If the user's message is about **updating criteria** (adding/removing keywords, countries, schema fields, etc.), go to **Step 1.5**.
  - Otherwise, scan the `## Universities` section to determine next action:
    1. If any university has `[ ][ ]` (discovery not done), resume from Step 4 (Discovery).
    2. If any university has `[x][ ]` (discovery done, extraction pending), resume from Step 5 (Extraction).
    3. If all universities are `[x][x]`, go to Step 6 (Compilation).
    4. If Phase 1 items are unchecked, resume from the corresponding step.
  - **Important:** The state file only has university-level checkboxes. Per-program status lives in the discovery JSON files (`.state/discovery/*.json`) under the `"status"` field.


### Step 1.5: Criteria Update Flow
*(Execute ONLY when the user wants to change their existing search criteria)*

1. **Show Current Criteria:** Display the current contents of `master-context.md` to the user — Interest Keywords, Negative Keywords, Target Countries, Rank Cutoff, and the Extraction Schema.

2. **Ask What To Change:** Ask the user what they want to modify. Wait for their reply.

3. **Classify the Change:** After the user responds, determine which tier this change falls under:

   **Tier 1 — Additive (append only, keep all existing work):**
   - Adding a new **country** → keep all existing universities; just run Step 3 for the new country, then Steps 4-5-6 for the new additions
   - Adding a new **negative keyword** → filter existing `.state/discovery/*.json` files and remove programs matching the new negative keyword; delete their corresponding `.state/extraction/*.json` files; reset the `"status"` of removed programs in the discovery JSON
   - Removing a **country** → remove universities from that country from pipeline-state.md and delete their discovery/extraction files

   **Tier 2 — Schema Change (nuke extraction, keep discovery):**
   - Adding/removing/modifying a **schema field** → all existing `.state/extraction/*.json` files are invalid. **Delete all files in `.state/extraction/`**. Reset all program statuses to `"pending"` in every `.state/discovery/*.json` file. Set the second checkbox of every university in pipeline-state.md back to `[ ]` (i.e., `[x][ ]`). Discovery results are still valid.

   **Tier 3 — Keyword Change (full re-run):**
   - Adding/removing an **interest keyword** → existing universities may have matching programs that were previously filtered out. **Delete all files in both `.state/discovery/` and `.state/extraction/`**. Reset pipeline-state.md: set all universities to `[ ][ ]`. Phase 1 stays checked. If countries also changed, also re-run Step 3.

4. **Confirm with User:** Tell the user which tier applies, what will be invalidated, and what will be kept. Ask for confirmation before proceeding.

5. **Execute Invalidation:** Once confirmed:
   - Update `master-context.md` with the new criteria.
   - Delete the appropriate files and reset the appropriate checkboxes/statuses according to the tier.
   - Resume the pipeline by going to Step 1 to find the next action.


### Step 2: The Intake & Context Generation
*(Execute only if unchecked in pipeline-state.md)*
1. Ask the user for: Interest Keywords, Negative Keywords (topics to explicitly ignore), Target Countries, and Rank Cutoff.
2. Present this default extraction schema, noting that the values contain instructions and examples for the subagent:
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

3. Ask the user: "Would you like to add any custom data points? If so, please provide the field name and a short description of what you are looking for."

4. CRITICAL: Stop and wait for the user to reply.

5. Intent Verification: If the user adds a new criteria, you MUST repeat back your understanding of their intent and provide a mock example of the expected output. Ask the user to confirm this interpretation before proceeding.

6. Once approved, save the criteria and this Descriptive JSON Schema into master-context.md. You must explicitly write a rule in master-context.md that the Rank Cutoff applies strictly to QS World University Rankings or Times Higher Education (THE). Check off Phase 1 setup boxes [x].

### Step 3: Baseline Search & State Update

(Execute only if unchecked)

1. Use your built-in web search or `playwright-cli` to find a baseline list of universities matching the user's target countries.

2. Strict Ranking Filter: You must evaluate the Rank Cutoff for these universities using ONLY the QS World University Rankings or Times Higher Education (THE). Ignore national rankings, ARWU, US News, etc. If a university falls outside the cutoff on both QS and THE, discard it.

3. Update `.state/pipeline-state.md` to create a `## Universities` section. List every qualifying university with two empty checkboxes: `- [ ][ ] University Name (Country)`.

### Step 4: Discovery Delegation (The Finders) — PARALLEL

Look at the `## Universities` section in `.state/pipeline-state.md` for universities with `[ ][ ]` (first checkbox unchecked).

1. **Parallel Execution:** You may dispatch **multiple `program-finder` subagents in parallel**. Each subagent gets a unique session name to ensure full browser isolation.

2. **Session Naming:** For each university, generate a session name: `uni-<sanitized-name>` (e.g., `uni-tum`, `uni-eth-zurich`, `uni-oxford`). Sanitize by lowercasing and replacing spaces/special chars with hyphens.

3. **Dispatch:** For each unchecked university, invoke the `Agent` tool with the `program-finder` subagent. In the task description, include:
   - The University Name and its website URL
   - The Interest Keywords and Negative Keywords
   - **The session name**, e.g.: "Your SESSION_NAME is `uni-tum`. Use `-s=uni-tum` for every playwright-cli command."

4. **Batching:** Dispatch universities in batches (e.g., 3–5 at a time) to avoid overwhelming system resources. Wait for the batch to complete before dispatching the next batch.

5. **Collect Results:** Once each agent returns, save the results to `.state/discovery/universityname.json`. Each program entry must include `"status": "pending"`. Update the first checkbox to `[x]` in the state file (i.e., `[ ][ ]` → `[x][ ]`).

6. **Cleanup:** After each batch completes, run:
   ```bash
   playwright-cli close-all
   ```
   This ensures no stale browser sessions linger between batches.

### Step 5: Extraction Delegation (The Analyzers) — PARALLEL

Look at the `## Universities` section for universities with `[x][ ]` (discovery done, extraction pending).

**For each university with `[x][ ]`:**

1. **Load Programs:** Read ONLY that university's `.state/discovery/universityname.json`. Filter for programs with `"status": "pending"`.

2. **Skip if none:** If no programs are `"pending"`, mark the university as `[x][x]` and move to the next.

3. **Session Naming:** For each program, generate a session name: `prog-<sanitized-uni>-<sanitized-program>` (e.g., `prog-tum-cs`, `prog-eth-ml`). Keep it short but unique.

4. **Dispatch:** For each pending program, invoke the `Agent` tool with the `program-analyzer` subagent. Include:
   - The URL, Program Name, University Name, and the Descriptive JSON Schema from `master-context.md`
   - **The session name**, e.g.: "Your SESSION_NAME is `prog-tum-cs`. Use `-s=prog-tum-cs` for every playwright-cli command."

5. **Batching:** Dispatch programs in batches (e.g., 3–5 at a time). Wait for the batch to complete before the next batch.

6. **Update Status:** After each analyzer returns:
   - Update the program's `"status"` in the discovery JSON to `"done"` or `"failed"`.
   - Once ALL programs for this university are non-pending (`"done"` or `"failed"`), mark the university as `[x][x]` in `pipeline-state.md`.

7. **Move to next university:** Proceed to the next `[x][ ]` university.


### Step 6: Compilation

Once all Phase 3 boxes are checked, run the terminal command python compile_results.py to generate the final Excel file.


## Troubleshooting

### Playwright CLI Not Found

If `playwright-cli` is not found:
1. Try `npx playwright-cli --version` to use the npx fallback.
2. If that also fails, ask the user to install: `npm install -g @playwright/cli`.

### Stale / Zombie Browser Sessions

If browsers become unresponsive or sessions are left open from a previous run:
```bash
playwright-cli list        # see what's running
playwright-cli close-all   # graceful shutdown
playwright-cli kill-all    # force kill if close-all fails
```

### Subagent Timeout or Crash

If a program-analyzer or program-finder subagent fails to return data or throws a critical error:

1. Note the failure in .state/pipeline-state.md (e.g., mark as [FAILED]).
2. Run `playwright-cli close-all` to clean up any orphaned sessions.
3. Do not get stuck in an infinite retry loop. Move on to the next empty [ ] checkbox in the queue.