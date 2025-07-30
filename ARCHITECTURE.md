# Kiro-RLVR System Architecture

## Overview

Kiro-RLVR is a sophisticated autonomous agent system that enhances Claude Code with intelligent task routing, performance evaluation, and continuous improvement capabilities.

## System Flow Diagram

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
        KT[Kiro Template<br/>Generator]
        PO[Prompt Optimizer]
        AS[Agent Selector]
        TC[Tool Validator]
        PC[Pre-Check<br/>Security]
    end

    subgraph "Agent Pool (.md files)"
        A1[agent-bugfix-junior.md]
        A2[agent-bugfix-senior.md]
        A3[agent-feature-junior.md]
        A4[agent-feature-senior.md]
        A5[agent-refactor-principal.md]
        A6[agent-security-senior.md]
    end

    subgraph "Evaluation Layer"
        EV[RLVR Evaluator]
        FB[Feedback Generator]
        PM[Performance Monitor]
    end

    subgraph "Storage Layer"
        TS[(Tasks<br/>Metadata)]
        SB[(Scoreboard<br/>RLVR Metrics)]
        FD[(Feedback<br/>History)]
        SP[(Sprint<br/>Data)]
    end

    subgraph "Claude Code Core"
        CC[Claude Code<br/>Execution Engine]
    end

    %% User Flow
    U --> H1
    H1 --> TD
    TD --> KT
    KT --> PO
    PO --> AS
    AS --> |Select Best Agent| A1
    AS --> A2
    AS --> A3
    AS --> A4
    AS --> A5
    AS --> A6

    %% Execution Flow
    A1 --> CC
    A2 --> CC
    A3 --> CC
    A4 --> CC
    A5 --> CC
    A6 --> CC

    %% Tool Validation
    CC --> H2
    H2 --> TC
    H2 --> PC
    TC --> |Approve/Deny| CC
    PC --> |Security Check| CC
    CC --> H3
    H3 --> |Track Usage| SB

    %% Evaluation Flow
    CC --> H4
    H4 --> EV
    EV --> FB
    EV --> PM
    PM --> SB
    FB --> FD

    %% Feedback Loop
    SB --> |Performance Data| AS
    FD --> |Learning| PO

    %% Data Storage
    H1 --> |Save Task| TS
    EV --> |Update Status| TS
```

## Component Details

### 1. Hook Layer

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
    UserPromptSubmit->>UserPromptSubmit: Generate Kiro template
    UserPromptSubmit->>UserPromptSubmit: Select agent from .md
    UserPromptSubmit->>Claude Code: Kiro-structured prompt
    
    Claude Code->>Claude Code: Process with agent context
    
    Claude Code->>PreToolUse: Before tool use
    PreToolUse->>PreToolUse: Validate permissions
    PreToolUse->>PreToolUse: Security checks (pre-check.py)
    PreToolUse->>Claude Code: Allow/Deny
    
    Claude Code->>PostToolUse: After tool use
    PostToolUse->>PostToolUse: Track usage
    
    Claude Code->>Stop: Task complete
    Stop->>Stop: Evaluate RLVR + template compliance
    Stop->>Stop: Update sprint metrics
    Stop->>Stop: Generate feedback
    Stop->>User: Show results with scores
```

### 2. Task Detection & Routing

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

### 3. RLVR Evaluation System

```mermaid
graph LR
    subgraph "Evaluation Components"
        TC[Test Coverage<br/>25%]
        CQ[Code Quality<br/>15%]
        SS[Security Scan<br/>15%]
        CC[Code Complexity<br/>10%]
        CI[CI/CD Status<br/>10%]
        RR[Review Readiness<br/>10%]
        KT[Kiro Template<br/>15%]
    end

    subgraph "Reward Calculation"
        TC --> RC[Reward<br/>Calculator]
        CQ --> RC
        SS --> RC
        CC --> RC
        CI --> RC
        RR --> RC
        KT --> RC
        RC --> FR[Final Reward<br/>0.0 - 5.0]
    end

    subgraph "Agent Update"
        FR --> AP[Agent Performance<br/>Update]
        AP --> AT{Tier<br/>Threshold?}
        AT -->|Promote| PR[Promotion]
        AT -->|Demote| DM[Demotion]
        AT -->|Maintain| MT[No Change]
    end
```

### 4. Data Flow

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

### 5. Autonomous Processing Pipeline

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

## Kiro Template Structure

The Kiro Prompt Template ensures consistent task structuring:

```mermaid
graph TD
    subgraph "Template Fields"
        G[$GOAL<br/>Single Objective]
        C[$CONTEXT<br/>Background Info]
        I[$INPUT<br/>Artifacts/Code]
        CN[$CONSTRAINTS<br/>Limits/Security]
        O[$OUTPUT_EXPECTED<br/>Deliverables]
        A[$ACCEPTANCE_CRITERIA<br/>Checklist]
        D[$DEADLINE<br/>ISO 8601]
    end
    
    subgraph "Template Processing"
        TP[Template Parser] --> TV[Template Validator]
        TV --> TS[Template Scorer]
        TS --> |15% weight| RLVR[RLVR Evaluation]
    end
    
    G --> TP
    C --> TP
    I --> TP
    CN --> TP
    O --> TP
    A --> TP
    D --> TP
```

## Sprint Management System

```mermaid
stateDiagram-v2
    [*] --> SprintPlanning
    
    SprintPlanning --> SprintActive: /start-sprint
    
    state SprintActive {
        [*] --> TaskExecution
        TaskExecution --> VelocityTracking
        VelocityTracking --> BurndownUpdate
        BurndownUpdate --> TaskExecution
    }
    
    SprintActive --> SprintReview: /end-sprint
    
    state SprintReview {
        [*] --> MetricsCalculation
        MetricsCalculation --> VelocityReport
        VelocityReport --> CompletionAnalysis
        CompletionAnalysis --> [*]
    }
    
    SprintReview --> [*]
```

## Key Design Principles

### 1. **Zero Configuration**
- Works immediately after installation
- No API keys or external services required
- Intelligent defaults for all settings

### 2. **Natural Language Interface**
- No special syntax or commands needed
- Automatic intent detection
- Context-aware processing

### 3. **Continuous Learning**
- Performance tracking over time
- Feedback-driven improvements
- Adaptive agent selection

### 4. **Modular Architecture**
- Each component is independent
- Easy to extend or modify
- Clear separation of concerns

### 5. **Claude Code Native**
- Uses only standard Claude Code features
- No external dependencies
- File-based state management

## Performance Characteristics

### Latency
- Task detection: < 50ms
- Agent selection: < 100ms
- Prompt optimization: < 200ms
- Total overhead: < 500ms

### Scalability
- Handles unlimited tasks
- Efficient file-based storage
- No memory leaks or accumulation

### Reliability
- Graceful error handling
- Fallback mechanisms
- Comprehensive logging

## Security Model

```mermaid
graph TD
    subgraph "Security Layers"
        A[Input Validation] --> B[Tool Permission Check]
        B --> PC[Pre-Check Security<br/>Validation]
        PC --> C[Sandboxed Execution]
        C --> D[Output Sanitization]
    end
    
    subgraph "Validation Points"
        PC1[Agent Permissions<br/>Check]
        PC2[Tool Usage<br/>Patterns]
        PC3[Path Security<br/>Validation]
        PC4[Command<br/>Whitelisting]
    end
    
    subgraph "Constraints"
        E[No Network Access]
        F[No System Commands]
        G[Limited File Access]
        H[Python Stdlib Only]
    end
    
    PC --> PC1
    PC --> PC2
    PC --> PC3
    PC --> PC4
    
    B --> E
    B --> F
    B --> G
    C --> H
```

## Extension Points

### Adding New Task Types
1. Update keyword detection in `UserPromptSubmit`
2. Create optimization template
3. Add specialized agent if needed

### Custom Evaluation Metrics
1. Modify `rlvr-evaluate.py`
2. Add new component to reward calculation
3. Update feedback generation

### Integration with External Tools
1. Use PreToolUse hook for validation
2. Track usage in PostToolUse
3. Include in evaluation metrics

## Monitoring & Observability

### Key Metrics
- Task completion rate
- Average reward per agent
- Task type distribution
- Tool usage patterns

### Log Files
- `events.jsonl` - All system events
- `rlvr.jsonl` - Evaluation results  
- `*_performance.jsonl` - Agent metrics
- `errors.log` - Error tracking

### Health Checks
```bash
# System status
/kiro-status

# Performance metrics
/kiro-leaderboard

# Detailed report
/kiro-report

# Sprint management
/start-sprint "Sprint Name" 14
/burndown
/end-sprint
```

## Future Enhancements

### Planned Features
1. Multi-project agent sharing
2. Advanced learning algorithms
3. Custom reward functions
4. Visual analytics dashboard

### Research Areas
1. Transformer-based task detection
2. Reinforcement learning optimization
3. Cross-agent knowledge transfer
4. Automated prompt engineering

---

This architecture ensures Kiro-RLVR provides intelligent, autonomous assistance while maintaining simplicity, security, and extensibility.