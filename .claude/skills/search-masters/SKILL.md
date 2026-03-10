---
name: search-masters
description: Orchestrates the parallel master's program search pipeline using browser automation. Use when the user says "find master programs", "research universities", or "run the master search".
disable-model-invocation: true
---
# Master's Search Orchestrator

## Performance Notes
* Take your time to do this thoroughly.
* Quality is more important than speed.
* Do not skip validation steps.

## Workflow: Autonomous Master's Search

Execute these steps strictly in sequence. You must manage state using `.state/pipeline-state.md`.

### Step 0: Global Dependency Validation
*(Execute every time before Step 1)*

1. **Strict MCP Tool Check:** You MUST run `list_tools` and verify that tools provided by the `puppeteer` MCP server (e.g., `puppeteer_navigate`) are active.
   - **CRITICAL:** If you see `chrome-devtools`, `computer`, or `Google Search` but NOT `puppeteer_navigate`, you must STOP.
   - **Action:** Warn the user: "⚠️ The Puppeteer MCP is missing. The subagents will be slow and expensive. Please install Puppeteer: `claude mcp add puppeteer -- npx -y @modelcontextprotocol/server-puppeteer` and restart."
   - **Do not proceed** until you see the `puppeteer_` prefix in your tool list.
   
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
- If NO: Create it. Add Phase 1 checkboxes (`[ ] Intake`, `[ ] Context Generation`, `[ ] Baseline Search`).
- If YES: Read the file. Find the very first empty `[ ]` checkbox. This is your exact starting position. Ignore all steps above it.



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

1. Use your built-in web search or puppeteer MCP tools to find a baseline list of universities matching the user's target countries.

2. Strict Ranking Filter: You must evaluate the Rank Cutoff for these universities using ONLY the QS World University Rankings or Times Higher Education (THE). Ignore national rankings, ARWU, US News, etc. If a university falls outside the cutoff on both QS and THE, discard it.

3. Update .state/pipeline-state.md to create a "Phase 2: Discovery" section. List every single qualifying university with an empty [ ] checkbox.

### Step 4: Phase 2 Delegation (The Finders)

Look at the Phase 2 checklist in `.state/pipeline-state.md`.
1. **Parallel Batch Execution:** You MUST invoke the `Agent` tool for up to **5 unchecked universities simultaneously in a single turn**. 
2. Do NOT wait for one university to finish before starting the others in the batch. Delegate each to the `program-finder` subagent. 
3. **Single-Turn Dispatch:** Send one message containing multiple `Agent` tool use blocks (one for each university in the batch).
4. Pass the University Name, Interest Keywords, and Negative Keywords. Instruct the agent to be thorough in its extraction. 
3. Once a batch returns, compile the JSON links into `.state/discovery/universityname.json`, check off `[x]` (or [FAILED] if it fails) in the state file, and immediately dispatch the next batch of 5.

### Step 5: Phase 3 Setup & Delegation (The Analyzers)
1. Read the Descriptive JSON Schema and the list of discovered program URLs.
3. Update .state/pipeline-state.md to create a "Phase 3: Extraction" section, listing every program URL with an empty [ ] box next to it. This is your queue for the analyzers.
2. **Parallel Batch Execution:** You MUST invoke the `Agent` tool for up to **5 unchecked programs simultaneously in a single turn**.
3. Do NOT wait for one program to finish before starting the others in the batch.
4. Delegate each to the `program-analyzer` subagent. Pass the URL, Program Name, and the Descriptive JSON Schema. Instruct the agent to be thorough in its extraction.
5. As each batch finishes, check them off `[x]` (or [FAILED] if it fails) in the state file and proceed to the next batch of 5 until all extractions are complete.


### Step 6: Compilation

Once all Phase 3 boxes are checked, run the terminal command python compile_results.py to generate the final Excel file.


## Troubleshooting

### MCP Connection Failed

If you see "Connection refused" or cannot access browser tools:

1. Verify the Puppeteer MCP server is running by checking your extension settings.
2. Confirm the Node.js environment is active.
3. Do not fail the entire pipeline; pause and ask the user to restart the MCP server.

### Subagent Timeout or Crash

If a program-analyzer or program-finder subagent fails to return data or throws a critical error:

1. Note the failure in .state/pipeline-state.md (e.g., mark as [FAILED]).
2. Do not get stuck in an infinite retry loop. Move on to the next empty [ ] checkbox in the queue.