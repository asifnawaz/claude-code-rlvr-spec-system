# Product Requirements Document (PRD)

## "Kiro‑RLVR" Context Engineering Platform for Claude Code

### 1 Background & Problem Statement

Large‑language‑model agents often diverge from intended scope, producing buggy features or unsafe work‑arounds. Claude Code recently introduced **sub‑agents, hooks, and commands**, letting us isolate agent contexts—but we still lack a structured, reward‑driven process that mimics real‑world development accountability.
We need a platform that:

* Routes tasks to specialised sub‑agents with minimal context bleed‑over.
* Scores outcomes with Reinforcement Learning & Variable Rewards (RLVR).
* Promotes or demotes agents automatically, raising overall quality.

### 2 Goals & Objectives

| Priority | Goal                                             | Measure of Success                                          |
| -------- | ------------------------------------------------ | ----------------------------------------------------------- |
| P0       | Deterministic execution of multi‑agent pipelines | 95 % of tasks assigned to correct tiered agent on first try |
| P0       | Automated reward computation & leaderboard       | Rewards logged ≤ 5 s after hook finish                      |
| P1       | Self‑healing via agent promotion/demotion        | Mean reward per task increases ≥ 10 % month‑over‑month      |
| P2       | Cross‑project reputation registry                | 80 % re‑use rate of Principal agents across projects        |

### 3 Personas & Use Cases

* **Tech Lead** – defines sub‑agent prompts & reward rules; audits security.
* **Contributor/Developer** – submits tasks, reviews agent output.
* **Product Manager** – tracks leaderboard trends & delivery KPIs.

Key use cases:

1. Assign bug‑fix ticket → junior agent returns patch → evaluator penalises failing tests → agent demoted.
2. New integration feature → senior agent delivers clean PR → evaluator rewards → agent promoted to Principal.

### 4 Scope

**In‑scope**

* Agent coordination & reward loop
* Hook scripts for CI, lint, security scan
* JSONL scoreboard & nightly tier recalculation

**Out‑of‑scope (v1)**

* Web UI dashboard (CLI/JSON only)
* Non‑Claude LLM back‑ends
* Fine‑tuning of language models

### 5 Functional Requirements

| ID   | Requirement                                                                                               |
| ---- | --------------------------------------------------------------------------------------------------------- |
| FR‑1 | Coordinator must route each task to the highest‑tier matching sub‑agent within <200 ms.                   |
| FR‑2 | Hooks MUST run `rlvr‑evaluate.py` on `SubagentStop` and write scalar reward `r` to scoreboard file.       |
| FR‑3 | Nightly cron MUST recalculate rolling averages over last 10 tasks and edit `tier:` in agent front‑matter. |
| FR‑4 | Suspended agents MUST NOT be selectable for new tasks, but history is preserved.                          |
| FR‑5 | System MUST expose CLI `kiro status` returning leaderboard JSON.                                          |

### 6 Non‑Functional Requirements

* **Security** – Hooks run in sandbox; no outbound network except whitelisted CI APIs.
* **Observability** – Logs streamed to stdout and archived; 30‑day retention.
* **Scalability** – Support ≥ 50 concurrent sub‑agents on commodity laptop.
* **Portability** – Works on macOS/Linux; no proprietary binaries.

### 7 Success Metrics (KPIs)

* Task failure rate ‹ 8 % after 4 weeks.
* Mean reward ≥ +4 by sprint 3.
* Average lead time from ticket creation to agent PR ≤ 30 min.

### 8 Milestones & Timeline

| Date        | Milestone                                |
| ----------- | ---------------------------------------- |
| Aug 12 2025 | MVP: coordinator + manual reward entry   |
| Sep 02 2025 | RLVR evaluator hook + auto leaderboard   |
| Sep 30 2025 | Tier promotion/demotion automation       |
| Oct 28 2025 | Cross‑project reputation registry (beta) |

### 9 Risks & Mitigations

| Risk                                      | Likelihood | Impact | Mitigation                              |
| ----------------------------------------- | ---------- | ------ | --------------------------------------- |
| Hooks abused for malicious shell commands | M          | H      | Sandbox + code review                   |
| Reward shaping causes gaming behaviour    | M          | M      | Add manual override & diversity metrics |
| Context windows exceed Claude limits      | L          | H      | Coordinator enforces token budgets      |

---

# System Architecture

### 1 Component Diagram

```
┌────────────────────────────────────┐
│       CLI / IDE Plugin            │
└──────────────┬────────────────────┘
               │ task.yml
┌──────────────▼───────────────┐   Job events    ┌───────────────────────┐
│        Coordinator           │───────────────▶│     Sub‑Agent Pool     │
│ • Parses task metadata       │◀───────────────│  YAML front‑matter     │
│ • Selects best agent         │   PostToolUse  │  Own Claude context    │
└──────────────┬───────────────┘                 └──────────┬────────────┘
               │ Hook exec                          Rewards │
┌──────────────▼───────────────┐                 ┌──────────▼────────────┐
│      RLVR Evaluator          │───────────────▶│   Scoreboard Store     │
│ • Aggregates CI, lint, tests │  JSONL append  │  rlvr.jsonl            │
│ • Emits scalar reward r      │                │  agent_tiers.json      │
└──────────────┬───────────────┘                 └───────────────────────┘
               │ Nightly cron
┌──────────────▼───────────────┐
│ Tier Update Service          │ (edits YAML)
└──────────────────────────────┘
```

### 2 Data Flow

1. **Task Submission** – User triggers `kiro assign --task bug‑123`.
2. **Coordinator** loads sub‑agent registry, filters by `description` tags & tier, selects highest‑score agent.
3. **Sub‑Agent** runs in isolated Claude context, using Claude Code tools.
4. On `SubagentStop`, hook executes `rlvr‑evaluate.py`, pulling CI status, lint results, review score.
5. **RLVR Evaluator** writes reward to `rlvr.jsonl`; stdout shows summary.
6. Nightly cron recalculates rolling averages, updates `tier:` fields.

### 3 Sequence Diagram (Happy Path)

```
User → Coordinator: createTask(bug‑123)
Coordinator → AgentRegistry: selectAgent(tags=bugfix)
Coordinator → SubAgent: runTask(payload)
SubAgent → Hooks: PostToolUse
Hooks → RLVR: evaluate(outcome)
RLVR → Scoreboard: appendReward(r)
Scoreboard → Coordinator: ack
Coordinator → User: taskComplete(PR link)
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

* Least‑privilege PAT for repo status.
* Hooks executed with read‑only FS except project directory.
* Each agent shell command prefixed with `set ‑euo pipefail`.

### 8 Observability

* Stdout/stderr of hooks captured to `logs/<date>.ndjson`.
* CLI `kiro logs --tail` streams live.

### 9 Future Extensions

1. Replace JSONL with Postgres for multi‑device sync.
2. Add web dashboard (Next.js) reading the same data schema.
3. Support non‑Claude agents via OpenAI function call wrapper.
