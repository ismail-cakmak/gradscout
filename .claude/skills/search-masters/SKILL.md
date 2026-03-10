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

1. **Strict MCP Tool Check:** You MUST run `list_tools` and verify that tools provided by the `playwright` MCP server (e.g., `browser_navigate`) are active.
   - **CRITICAL:** If you see `chrome-devtools`, `computer`, or `Google Search` but NOT `browser_navigate`, you must STOP.
   - **Action:** Warn the user: "⚠️ The Playwright MCP is missing. The subagents will be slow and expensive. Please install Playwright MCP: `claude mcp add playwright -- npx -y @playwright/mcp` and restart."
   - **Do not proceed** until you see the `browser_` prefix in your tool list.
   
2. **Check Python Environment:** Use the `bash` tool to run: 
   `python3 -c "import os, json, pandas, openpyxl; print('Dependencies OK')"`
   - **If it fails:** Note which library is missing (likely `pandas` or `openpyxl`). 
   - **Action:** Tell the user: "⚠️ Python dependencies missing. Please run: `pip install pandas openpyxl`".
   - **Stop:** Do not proceed to Step 1 until the user confirms installation.

3. **Check Directory Structure:** Ensure `.state/discovery` and `.state/extraction` exist.
   - **Action:** If missing, run `mkdir -p .state/discovery .state/extraction`.

4. **Proceed:** Only if all three checks pass, move to Step 1.


### Step 1: State Recovery & Initialization
Check if `.state/pipeline-state.md` exists. 
- If NO: This is a **fresh run**. Create it. Add Phase 1 checkboxes (`[ ] Intake`, `[ ] Context Generation`, `[ ] Baseline Search`). Skip Step 1.5 and go to Step 2.
- If YES: Read the file and also read `master-context.md`.
  - If the user's message is about **updating criteria** (adding/removing keywords, countries, schema fields, etc.), go to **Step 1.5**.
  - Otherwise, determine which phase to resume:
    1. If there are ANY unchecked `[ ]` items in **Phase 2**, resume from Step 4 (Discovery). **Do NOT skip ahead to Phase 3 even if Phase 3 items exist.**
    2. If all Phase 2 items are checked and there are unchecked `[ ]` items in **Phase 3**, resume from Step 5 (Extraction).
    3. If all Phase 2 and Phase 3 items are checked, go to Step 6 (Compilation).
    4. If Phase 1 items are unchecked, resume from the corresponding step.


### Step 1.5: Criteria Update Flow
*(Execute ONLY when the user wants to change their existing search criteria)*

1. **Show Current Criteria:** Display the current contents of `master-context.md` to the user — Interest Keywords, Negative Keywords, Target Countries, Rank Cutoff, and the Extraction Schema.

2. **Ask What To Change:** Ask the user what they want to modify. Wait for their reply.

3. **Classify the Change:** After the user responds, determine which tier this change falls under:

   **Tier 1 — Additive (append only, keep all existing work):**
   - Adding a new **country** → keep all existing universities; just run Step 3 for the new country, then Steps 4-5-6 for the new additions
   - Adding a new **negative keyword** → filter existing `.state/discovery/*.json` files and remove programs matching the new negative keyword; delete their corresponding `.state/extraction/*.json` files; uncheck removed programs in pipeline-state.md
   - Removing a **country** → remove universities from that country from pipeline-state.md and delete their discovery/extraction files

   **Tier 2 — Schema Change (nuke extraction, keep discovery):**
   - Adding/removing/modifying a **schema field** (e.g., adding `language_of_instruction`) → all existing `.state/extraction/*.json` files are invalid because they are missing the new field. **Delete all files in `.state/extraction/`**. Uncheck all Phase 3 items in pipeline-state.md (set back to `[ ]`). Discovery results are still valid.

   **Tier 3 — Keyword Change (full re-run):**
   - Adding/removing an **interest keyword** → existing universities may have matching programs that were previously filtered out. **Delete all files in both `.state/discovery/` and `.state/extraction/`**. Reset pipeline-state.md: uncheck all Phase 2 and Phase 3 items (set back to `[ ]`). Phase 1 stays checked. If countries also changed, also re-run Step 3.

4. **Confirm with User:** Tell the user which tier applies, what will be invalidated, and what will be kept. Ask for confirmation before proceeding.

5. **Execute Invalidation:** Once confirmed:
   - Update `master-context.md` with the new criteria.
   - Delete the appropriate files and uncheck the appropriate items in `pipeline-state.md` according to the tier.
   - Resume the pipeline from the first unchecked `[ ]` in `pipeline-state.md` (i.e., go to Step 1 and let it find the resume point).


### Step 2: The Intake & Context Generation
*(Execute only if unchecked in pipeline-state.md)*
1. Ask the user for: Interest Keywords, Negative Keywords (topics to explicitly ignore), Target Countries, and Rank Cutoff.
2. Present this default extraction schema, noting that the values contain instructions and examples for the subagent:
   ```json
   {
     "program_name": "Instruction: The official name of the degree. Example: 'MSc Computer Science'",
     "application_deadline": "Instruction: The exact date applications close for international students. Example: '2025-05-31'",
     "tuition_fee": "Instruction: The total cost of the entire program. Example: '1500 EUR/semester' or 'Free'",
     "housing_info": "Instruction: Indicate if housing is guaranteed and average rent. Example: 'No guarantee, ~600 EUR/month'"
   }
    ```

3. Ask the user: "Would you like to add any custom data points? If so, please provide the field name and a short description of what you are looking for."

4. CRITICAL: Stop and wait for the user to reply.

5. Intent Verification: If the user adds a new criteria, you MUST repeat back your understanding of their intent and provide a mock example of the expected output. Ask the user to confirm this interpretation before proceeding.

6. Once approved, save the criteria and this Descriptive JSON Schema into master-context.md. You must explicitly write a rule in master-context.md that the Rank Cutoff applies strictly to QS World University Rankings or Times Higher Education (THE). Check off Phase 1 setup boxes [x].

### Step 3: Baseline Search & State Update

(Execute only if unchecked)

1. Use your built-in web search or playwright MCP tools to find a baseline list of universities matching the user's target countries.

2. Strict Ranking Filter: You must evaluate the Rank Cutoff for these universities using ONLY the QS World University Rankings or Times Higher Education (THE). Ignore national rankings, ARWU, US News, etc. If a university falls outside the cutoff on both QS and THE, discard it.

3. Update .state/pipeline-state.md to create a "Phase 2: Discovery" section. List every single qualifying university with an empty [ ] checkbox.

### Step 4: Phase 2 Delegation (The Finders)

Look at the Phase 2 checklist in `.state/pipeline-state.md`.
1. **Sequential Execution:** You MUST invoke the `Agent` tool for **one unchecked university at a time**. All subagents share the same browser instance via the MCP server, so parallel execution causes tab conflicts and race conditions.
2. Delegate the university to the `program-finder` subagent. **Wait for it to fully complete** before starting the next one.
3. Pass the University Name, Interest Keywords, and Negative Keywords. Instruct the agent to be thorough in its extraction.
4. Once the agent returns, compile the JSON links into `.state/discovery/universityname.json`, check off `[x]` (or [FAILED] if it fails) in the state file, and then dispatch the next university.
5. **CRITICAL: Do NOT create Phase 3 entries or start any extraction work during this step. You must complete ALL Phase 2 universities before moving to Step 5. Keep looping through unchecked Phase 2 universities until every single one is `[x]` or `[FAILED]`.**

### Step 5: Phase 3 Setup & Delegation (The Analyzers)

**Prerequisite:** Verify that ALL Phase 2 items are `[x]` or `[FAILED]`. If any Phase 2 item is still `[ ]`, go back to Step 4. Do NOT start Phase 3 until Phase 2 is fully complete.

1. Read the Descriptive JSON Schema and the list of discovered program URLs from ALL `.state/discovery/*.json` files.
2. Update .state/pipeline-state.md to create a "Phase 3: Extraction" section, listing every program URL with an empty [ ] box next to it. This is your queue for the analyzers.
3. **Sequential Execution:** You MUST invoke the `Agent` tool for **one unchecked program at a time**. All subagents share the same browser instance, so parallel execution causes tab conflicts.
4. Delegate the program to the `program-analyzer` subagent. Pass the URL, Program Name, and the Descriptive JSON Schema. Instruct the agent to be thorough in its extraction.
5. **Wait for the agent to fully complete** before dispatching the next one. Check off `[x]` (or [FAILED] if it fails) in the state file and proceed to the next program until all extractions are complete.


### Step 6: Compilation

Once all Phase 3 boxes are checked, run the terminal command python compile_results.py to generate the final Excel file.


## Troubleshooting

### MCP Connection Failed

If you see "Connection refused" or cannot access browser tools:

1. Verify the Playwright MCP server is running by checking your extension settings.
2. Confirm the Node.js environment is active.
3. Do not fail the entire pipeline; pause and ask the user to restart the MCP server.

### Subagent Timeout or Crash

If a program-analyzer or program-finder subagent fails to return data or throws a critical error:

1. Note the failure in .state/pipeline-state.md (e.g., mark as [FAILED]).
2. Do not get stuck in an infinite retry loop. Move on to the next empty [ ] checkbox in the queue.