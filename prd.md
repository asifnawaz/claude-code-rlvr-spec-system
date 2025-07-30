# Product Requirements Document (CLI‑Aligned PRD)

## Product: **Doom‑RLVR Plugin for Claude Code CLI**

### 1 Background

Claude Code already provides sub‑agents (`/agents`), slash commands, hooks, and a rich CLI (`claude`). Our aim is to layer an **RL‑Variable‑Reward (RLVR)** mechanism on top *without introducing a separate coordinator binary*. All orchestration must happen **inside the existing Claude Code CLI** using:

* Slash commands for interactive features (`/leaderboard`, `/score-agent`, `/recalc-tiers`).
* Hooks for deterministic post‑run analysis (`SubagentStop`, `PostToolUse`).
* Standard shell tooling (`bash`, `python3`, `jq`, `yq`).
* **Sub‑agent definitions live in Markdown files (`.md`) that start with YAML front‑matter; our scripts touch only that front‑matter block, never the rest of the Markdown.**

### 2 Goals & Non‑Goals

**Goals**

1. Reward each sub‑agent action and persist scores in `.claude/scoreboard/rlvr.jsonl`.
2. Promote/demote agents nightly by rewriting the YAML front‑matter `tier:` field **inside each agent’s `.md` definition file**.
3. Provide real‑time slash commands to query scores and leaderboards.
4. Require **no additional global installs** beyond Claude Code and common POSIX utilities.

**Non‑Goals**

* Replacing Claude’s internal auto‑delegation logic.
* Inventing a parallel "doom" CLI—**we extend via existing commands**.

### 3 Personas & Use Cases

| Persona         | CLI Touchpoints                                        | Example Flow                                                                                                     |
| --------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| **Developer**   | `/fix-tests`, `claude -p`, `/leaderboard`              | Runs a custom slash command to fix tests; RLVR script scores agent on `SubagentStop`; views updated leaderboard. |
| **Tech Lead**   | `/recalc-tiers --dry-run`                              | Manually recalculates tiers before code‑review freeze.                                                           |
| **CI Pipeline** | `claude -p --output-format json "/leaderboard --json"` | Emits metrics artifact for dashboard.                                                                            |

### 4 Functional Requirements

| ID   | Requirement                                                                                | CLI Mapping                                                                                                                                                                                            |
| ---- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| FR‑1 | **Automatic reward evaluation** after every sub‑agent task.                                | Register `SubagentStop` hook → `python3 .claude/hooks/rlvr-evaluate.py`                                                                                                                                |
| FR‑2 | **Slash command `/leaderboard`** to print ranked agents.                                   | Markdown command in `.claude/commands/leaderboard.md` using `claude -p --output-format json`                                                                                                           |
| FR‑3 | **Nightly tier recalculation** via cron.                                                   | `0 3 * * * claude -p "/recalc-tiers"`                                                                                                                                                                  |
| FR‑4 | **Front‑matter integrity check** for `.md` agent files after tier rewrite.                 | Hook runs `yq eval` and aborts if invalid.                                                                                                                                                             |
| FR‑5 | **Project scaffolding script**.                                                            | `./scripts/setup-doom.sh` creates `.claude/agents/`, `.claude/hooks/`, `.claude/commands/`.                                                                                                            |
| FR‑6 | **Doom prompt template enforcement**.                                                      | Validation hook `validate-prompt-structure.py` ensures each task and sub-agent reply follow Doom structured fields (`GOAL`, `CONTEXT`, `INPUT`, `OUTPUT_EXPECTED`, `DEADLINE`, `ACCEPTANCE_CRITERIA`). |
| FR‑7 | **Sprint management slash commands** (`/start-sprint`, `/end-sprint`, `/burndown`).        | Markdown commands in `.claude/commands/` leverage RLVR metrics to prioritise backlog items.                                                                                                            |
| FR‑8 | **Optional safeguard hook** to block unsafe or non‑compliant tool calls *before* they run. | Register `PreToolUse` hook → `python3 .claude/hooks/pre-check.py`.                                                                                                                                     |

### 4.1 Doom Prompt System Template

```
# Doom Prompt
$GOAL: <single objective sentence>
$CONTEXT: <brief background>
$INPUT: <relevant artefacts / code refs>
$CONSTRAINTS: <edge cases, security limits>
$OUTPUT_EXPECTED: <deliverable definition>
$ACCEPTANCE_CRITERIA: <checklist>
$DEADLINE: <ISO 8601>
```

All sub‑agents must consume **and** respond using this structure. The RLVR evaluator deducts ≥ 2 points for any missing section and adds +1 for each acceptance‑criteria item explicitly ticked.

### 5 Metrics

* Mean reward ≥ +4 within two sprints.
* CLI overhead ≤ 300 ms per hook execution.
* 90 % team adoption of `/leaderboard` by month 1.

### 6 Milestones

| Date            | Deliverable                                 | Key CLI Feature               |
| --------------- | ------------------------------------------- | ----------------------------- |
| **Aug 12 2025** | MVP: `/score-agent` & `.claude/scoreboard/` | Slash command & manual hook   |
| **Sep 02 2025** | Auto RLVR via hooks                         | `SubagentStop` integration    |
| **Sep 30 2025** | Automated tier rewrite & `/promote`         | YQ rewrite script             |
| **Oct 28 2025** | JSON output for CI dashboards               | `--output-format json` prints |

### 7 Risks & Mitigations

| Risk                                   | Likelihood | Impact | Mitigation                                     |
| -------------------------------------- | ---------- | ------ | ---------------------------------------------- |
| Hooks can leak secrets via shell.      | Medium     | High   | Sandbox paths; peer review hook code.          |
| Agents game reward metrics.            | Medium     | Medium | Add manual override weight; diversify metrics. |
| Large context per task exceeds limits. | Low        | High   | Enforce token budgets in sub‑agent prompts.    |

---

# System Architecture

### 1 Component Diagram

```
┌────────────────────────────────────┐
│       CLI / IDE Plugin            │
└──────────────┬────────────────────┘
               │ task.yml
┌──────────────▼───────────────┐   Job events    ┌───────────────────────┐
│        CLI Dispatcher           │───────────────▶│     Sub‑Agent Pool     │
│ • Parses task metadata       │◀───────────────│  Front‑matter (YAML in .md)  │
│ • Selects best agent         │   PostToolUse  │  Own Claude context    │
└──────────────┬───────────────┘                 └──────────┬────────────┘
               │ Hook exec                          Rewards │
┌──────────────▼───────────────┐                 ┌──────────▼────────────┐
│      RLVR Evaluator          │───────────────▶│   Scoreboard Store     │
│ • Aggregates CI, lint, tests │  JSONL append  │  rlvr.jsonl            │
│ • Emits scalar reward r      │                │  —      │
└──────────────┬───────────────┘                 └───────────────────────┘
               │ Nightly cron
┌──────────────▼───────────────┐
│ Tier Update Service          │ (edits YAML)
└──────────────────────────────┘
```

### 2 Data Flow

1. **Task Submission** – User triggers `claude -p "/assign bug-123"`.
2. **CLI Dispatcher** loads sub‑agent registry, filters by `description` tags & tier, selects highest‑score agent.
3. **Sub‑Agent** runs in isolated Claude context, using Claude Code tools.
   3a. *(Optional)* **PreToolUse** hook `pre-check.py` may abort or modify the run if lint/security checks fail.
4. On `SubagentStop`, hook executes `rlvr‑evaluate.py`, pulling CI status, lint results, review score.
5. **RLVR Evaluator** writes reward to `rlvr.jsonl`; stdout shows summary.
6. Nightly cron recalculates rolling averages, updates `tier:` fields.

### 3 Sequence Diagram (Happy Path)

```
User → CLI Dispatcher: createTask(bug‑123)
CLI Dispatcher → AgentRegistry: selectAgent(tags=bugfix)
CLI Dispatcher → SubAgent: runTask(payload)
SubAgent → Hooks: PostToolUse
Hooks → RLVR: evaluate(outcome)
RLVR → Scoreboard: appendReward(r)
Scoreboard → CLI Dispatcher: ack
CLI Dispatcher → User: taskComplete(PR link)
```

### 4 Technology Choices

| Layer          | Tech                                 |
| -------------- | ------------------------------------ |
| CLI            | Python 3.11 (Typer)                  |
| Persistence    | JSONL files (optional SQLite for v2) |
| Scripting      | Claude Code hooks (Bash/Python)      |
| CI Integration | GitHub Actions REST API              |
| Sandboxing     | `distrobox` + limited capabilities   |

### 5 Deployment Topology

* **Local Dev** – All components run on developer laptop; hooks spawn child processes.
* **CI/CD Runner** – Same scripts run inside GitHub Action; mount `.claude/` to persist scoreboard.

### 6 Scalability & Performance

* Coordination uses in‑memory selection; ≤ 10 ms for 100 agents.
* Evaluator parallelises CI artefact fetch via asyncio; measured 0.5 s for typical project.

### 7 Security Model

*(Event naming note: the Hook Guide sometimes shows a space—"Subagent Stop"—but JSON keys must be `SubagentStop` and likewise `PreToolUse`; this spec adheres to the JSON form.)*

* Least‑privilege PAT for repo status.
* Hooks executed with read‑only FS except project directory.
* Each agent shell command prefixed with `set ‑euo pipefail`.

### 8 Observability

* Stdout/stderr of hooks captured to `logs/<date>.ndjson`.
* CLI `claude -p "/logs --tail"` streams live.

### 9 Future Extensions

1. Replace JSONL with SQLite DB for multi‑device sync.
2. Add web dashboard (Next.js) reading the same data schema.
3. Support non‑Claude agents via OpenAI function call wrapper.

### References

* Claude Code Sub‑agents – [https://docs.anthropic.com/en/docs/claude-code/sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
* Hooks Guide – [https://docs.anthropic.com/en/docs/claude-code/hooks-guide](https://docs.anthropic.com/en/docs/claude-code/hooks-guide)
* Claude Code SDK – [https://docs.anthropic.com/en/docs/claude-code/sdk](https://docs.anthropic.com/en/docs/claude-code/sdk)
* CLI Reference – [https://docs.anthropic.com/en/docs/claude-code/cli-reference](https://docs.anthropic.com/en/docs/claude-code/cli-reference)
* Slash Commands – [https://docs.anthropic.com/en/docs/claude-code/slash-commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands)
