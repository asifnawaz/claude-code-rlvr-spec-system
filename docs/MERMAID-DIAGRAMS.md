# Doom-RLVR Mermaid Diagrams

This document contains all Mermaid diagrams for the Doom-RLVR system. You can copy these into any Mermaid-compatible viewer or documentation system.

## 1. High-Level System Flow

```mermaid
graph LR
    A[User Input] --> B[Task Detection]
    B --> C[Agent Selection]
    C --> D[Prompt Optimization]
    D --> E[Task Execution]
    E --> F[RLVR Evaluation]
    F --> G[Feedback Loop]
    G --> C
```

## 2. Complete System Architecture

```mermaid
flowchart TB
    subgraph "User Layer"
        U[User Input<br/>Natural Language]
    end

    subgraph "Hook Layer"
        H1[UserPromptSubmit Hook]
        H2[PreToolUse Hook]
        H3[PostToolUse Hook]
        H4[Stop Hook]
    end

    subgraph "Processing Layer"
        TD[Task Detector]
        PO[Prompt Optimizer]
        AS[Agent Selector]
        TC[Tool Validator]
    end

    subgraph "Agent Pool"
        A1[agent-bugfix-junior]
        A2[agent-bugfix-senior]
        A3[agent-feature-junior]
        A4[agent-feature-senior]
        A5[agent-refactor-principal]
        A6[agent-security-senior]
    end

    subgraph "Evaluation Layer"
        EV[RLVR Evaluator]
        FB[Feedback Generator]
        PM[Performance Monitor]
    end

    subgraph "Storage Layer"
        TS[(Tasks<br/>Metadata)]
        SB[(Scoreboard<br/>Metrics)]
        FD[(Feedback<br/>History)]
    end

    subgraph "Claude Code Core"
        CC[Claude Code<br/>Execution Engine]
    end

    U --> H1
    H1 --> TD
    TD --> PO
    PO --> AS
    AS --> A1
    AS --> A2
    AS --> A3
    AS --> A4
    AS --> A5
    AS --> A6

    A1 --> CC
    A2 --> CC
    A3 --> CC
    A4 --> CC
    A5 --> CC
    A6 --> CC

    CC --> H2
    H2 --> TC
    TC --> CC
    CC --> H3
    H3 --> SB

    CC --> H4
    H4 --> EV
    EV --> FB
    EV --> PM
    PM --> SB
    FB --> FD

    SB --> AS
    FD --> PO

    H1 --> TS
    EV --> TS
```

## 3. Hook Execution Sequence

```mermaid
sequenceDiagram
    participant User
    participant Claude Code
    participant UserPromptSubmit
    participant PreToolUse
    participant PostToolUse
    participant Stop

    User->>Claude Code: Natural language prompt
    Claude Code->>UserPromptSubmit: Intercept prompt
    UserPromptSubmit->>UserPromptSubmit: Detect task type
    UserPromptSubmit->>UserPromptSubmit: Optimize prompt
    UserPromptSubmit->>UserPromptSubmit: Select agent
    UserPromptSubmit->>Claude Code: Enhanced prompt
    
    Claude Code->>Claude Code: Process with agent context
    
    Claude Code->>PreToolUse: Before tool use
    PreToolUse->>PreToolUse: Validate permissions
    PreToolUse->>Claude Code: Allow/Deny
    
    Claude Code->>PostToolUse: After tool use
    PostToolUse->>PostToolUse: Track usage
    
    Claude Code->>Stop: Task complete
    Stop->>Stop: Evaluate performance
    Stop->>Stop: Generate feedback
    Stop->>User: Show results
```

## 4. Task Detection Flow

```mermaid
graph TD
    subgraph "Task Detection"
        I[Input Text] --> K[Keyword Analysis]
        K --> T1{Contains<br/>'fix', 'bug'?}
        K --> T2{Contains<br/>'add', 'create'?}
        K --> T3{Contains<br/>'refactor'?}
        K --> T4{Contains<br/>'security'?}
        
        T1 -->|Yes| BF[Bugfix Task]
        T2 -->|Yes| FT[Feature Task]
        T3 -->|Yes| RF[Refactor Task]
        T4 -->|Yes| ST[Security Task]
    end

    subgraph "Agent Selection"
        BF --> S1[Score Agents]
        FT --> S1
        RF --> S1
        ST --> S1
        
        S1 --> S2{Check<br/>Specialization}
        S2 --> S3{Check<br/>Tier Level}
        S3 --> S4{Check<br/>Performance}
        S4 --> SA[Select Best Agent]
    end
```

## 5. RLVR Evaluation Process

```mermaid
graph LR
    subgraph "Evaluation Components"
        TC[Test Coverage<br/>30%]
        CQ[Code Quality<br/>20%]
        SS[Security Scan<br/>20%]
        CC[Code Complexity<br/>10%]
        CI[CI/CD Status<br/>10%]
        RR[Review Readiness<br/>10%]
    end

    subgraph "Reward Calculation"
        TC --> RC[Reward<br/>Calculator]
        CQ --> RC
        SS --> RC
        CC --> RC
        CI --> RC
        RR --> RC
        RC --> FR[Final Reward<br/>0.0 - 1.0]
    end

    subgraph "Agent Update"
        FR --> AP[Agent Performance<br/>Update]
        AP --> AT{Tier<br/>Threshold?}
        AT -->|Promote| PR[Promotion]
        AT -->|Demote| DM[Demotion]
        AT -->|Maintain| MT[No Change]
    end
```

## 6. Data Model Relationships

```mermaid
erDiagram
    TASK ||--o{ SUBTASK : contains
    TASK ||--|| AGENT : assigned-to
    TASK ||--|| EVALUATION : has
    AGENT ||--o{ PERFORMANCE : tracks
    EVALUATION ||--o{ FEEDBACK : generates
    
    TASK {
        string task_id PK
        string type
        string priority
        string description
        datetime created_at
        string status
    }
    
    AGENT {
        string name PK
        string tier
        string specializations
        float avg_reward
    }
    
    EVALUATION {
        string eval_id PK
        string task_id FK
        float reward
        json components
        datetime timestamp
    }
    
    PERFORMANCE {
        string perf_id PK
        string agent_name FK
        float reward
        datetime timestamp
    }
    
    FEEDBACK {
        string feedback_id PK
        string eval_id FK
        string area
        string suggestion
    }
```

## 7. State Machine

```mermaid
stateDiagram-v2
    [*] --> UserInput
    UserInput --> TaskDetection
    
    state TaskDetection {
        [*] --> AnalyzeKeywords
        AnalyzeKeywords --> DetermineType
        DetermineType --> SetPriority
        SetPriority --> [*]
    }
    
    TaskDetection --> PromptOptimization
    
    state PromptOptimization {
        [*] --> LoadTemplate
        LoadTemplate --> InjectContext
        InjectContext --> AddGuidelines
        AddGuidelines --> [*]
    }
    
    PromptOptimization --> AgentSelection
    
    state AgentSelection {
        [*] --> ScoreAgents
        ScoreAgents --> CheckSpecialization
        CheckSpecialization --> CheckPerformance
        CheckPerformance --> SelectBest
        SelectBest --> [*]
    }
    
    AgentSelection --> Execution
    
    state Execution {
        [*] --> ValidateTools
        ValidateTools --> ExecuteTask
        ExecuteTask --> TrackUsage
        TrackUsage --> [*]
    }
    
    Execution --> Evaluation
    
    state Evaluation {
        [*] --> MeasureQuality
        MeasureQuality --> CalculateReward
        CalculateReward --> GenerateFeedback
        GenerateFeedback --> UpdatePerformance
        UpdatePerformance --> [*]
    }
    
    Evaluation --> [*]
```

## 8. Component Communication

```mermaid
graph TB
    subgraph "Frontend"
        CLI[CLI Commands]
        NLP[Natural Language]
    end
    
    subgraph "Hooks"
        UP[UserPromptSubmit]
        PT[PreToolUse]
        PO[PostToolUse]
        ST[Stop]
    end
    
    subgraph "Core Services"
        TD[Task Detector]
        AS[Agent Selector]
        EV[Evaluator]
    end
    
    subgraph "Data Store"
        FS[File System]
        JSON[JSONL Files]
    end
    
    CLI --> UP
    NLP --> UP
    UP --> TD
    TD --> AS
    AS --> FS
    
    PT --> FS
    PO --> JSON
    ST --> EV
    EV --> JSON
    
    JSON --> AS
    FS --> TD
```

## 9. Security Model

```mermaid
graph TD
    subgraph "Security Layers"
        A[Input Validation] --> B[Tool Permission Check]
        B --> C[Sandboxed Execution]
        C --> D[Output Sanitization]
    end
    
    subgraph "Constraints"
        E[No Network Access]
        F[No System Commands]
        G[Limited File Access]
        H[Python Stdlib Only]
    end
    
    B --> E
    B --> F
    B --> G
    C --> H
```

## 10. Agent Lifecycle

```mermaid
graph LR
    subgraph "Agent States"
        N[New Agent] --> J[Junior]
        J --> S[Senior]
        S --> P[Principal]
        
        J --> SU[Suspended]
        S --> SU
        P --> SU
        
        SU --> J
    end
    
    subgraph "Transitions"
        PT[Performance<br/>Threshold]
        RT[Reward<br/>Tracking]
        TU[Tier<br/>Update]
    end
    
    RT --> PT
    PT --> TU
    TU --> J
    TU --> S
    TU --> P
    TU --> SU
```

## Usage

These diagrams can be:
1. Rendered in GitHub README files
2. Used in documentation tools like MkDocs
3. Copied to Mermaid Live Editor (https://mermaid.live)
4. Integrated into presentations
5. Used in technical specifications

To use in markdown, wrap the diagram code in triple backticks with `mermaid` as the language identifier.