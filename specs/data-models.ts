// Kiro-RLVR Data Models TypeScript Specification

// Core Domain Models

export interface Task {
  id: string;
  type: TaskType;
  status: TaskStatus;
  priority: TaskPriority;
  tags: string[];
  description: string;
  assignedAgent?: string;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  metadata: TaskMetadata;
  outcome?: TaskOutcome;
  constraints: TaskConstraints;
}

export interface TaskMetadata {
  source: 'cli' | 'api' | 'github' | 'webhook';
  projectId?: string;
  repositoryUrl?: string;
  issueNumber?: number;
  parentTaskId?: string;
  customFields?: Record<string, any>;
}

export interface TaskConstraints {
  maxTokens: number;
  timeoutMs: number;
  allowedTools?: string[];
  forbiddenPatterns?: string[];
  requiredChecks?: string[];
}

export interface TaskOutcome {
  success: boolean;
  prUrl?: string;
  commitHash?: string;
  errorMessage?: string;
  errorType?: ErrorType;
  tokensUsed: number;
  durationMs: number;
  toolsUsed: ToolUsage[];
  filesModified: string[];
  testsAdded: number;
  testsPassed: number;
  testsFailed: number;
}

export interface ToolUsage {
  tool: string;
  count: number;
  totalDurationMs: number;
  errors: number;
}

export enum TaskType {
  BUGFIX = 'bugfix',
  FEATURE = 'feature',
  REFACTOR = 'refactor',
  SECURITY = 'security',
  DOCUMENTATION = 'documentation',
  TESTING = 'testing',
  PERFORMANCE = 'performance'
}

export enum TaskStatus {
  PENDING = 'pending',
  ASSIGNED = 'assigned',
  IN_PROGRESS = 'in_progress',
  REVIEW = 'review',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  TIMEOUT = 'timeout'
}

export enum TaskPriority {
  P0 = 'P0', // Critical
  P1 = 'P1', // High
  P2 = 'P2', // Medium
  P3 = 'P3'  // Low
}

export enum ErrorType {
  TIMEOUT = 'timeout',
  TOKEN_LIMIT = 'token_limit',
  TOOL_ERROR = 'tool_error',
  VALIDATION_ERROR = 'validation_error',
  PERMISSION_ERROR = 'permission_error',
  RUNTIME_ERROR = 'runtime_error'
}

// Agent Models

export interface Agent {
  name: string;
  tier: AgentTier;
  status: AgentStatus;
  specializations: string[];
  createdAt: Date;
  lastActiveAt: Date;
  performance: AgentPerformance;
  config: AgentConfig;
  metadata: AgentMetadata;
}

export interface AgentConfig {
  systemPrompt: string;
  toolsAllowed: string[];
  toolsForbidden?: string[];
  maxContextTokens: number;
  temperature?: number;
  customHooks?: string[];
  environmentVars?: Record<string, string>;
  resourceLimits?: ResourceLimits;
}

export interface ResourceLimits {
  maxMemoryMb: number;
  maxCpuPercent: number;
  maxDiskIoMbps: number;
  maxNetworkMbps: number;
}

export interface AgentPerformance {
  rollingAvgReward: number;
  totalTasks: number;
  completedTasks: number;
  failedTasks: number;
  successRate: number;
  avgDurationMs: number;
  avgTokensUsed: number;
  last10Rewards: number[];
  rewardHistory: RewardHistoryEntry[];
  tierHistory: TierChangeEvent[];
  specialtyScores: Record<string, number>;
}

export interface RewardHistoryEntry {
  timestamp: Date;
  taskId: string;
  reward: number;
  components: RewardComponents;
}

export interface TierChangeEvent {
  timestamp: Date;
  fromTier: AgentTier;
  toTier: AgentTier;
  reason: string;
  automatic: boolean;
  rollingAvgAtChange: number;
}

export interface AgentMetadata {
  version: string;
  author?: string;
  description?: string;
  projectsUsed?: string[];
  totalRewards: number;
  suspensionCount: number;
  lastSuspensionReason?: string;
  customTags?: string[];
}

export enum AgentTier {
  JUNIOR = 'junior',
  SENIOR = 'senior',
  PRINCIPAL = 'principal',
  SUSPENDED = 'suspended'
}

export enum AgentStatus {
  AVAILABLE = 'available',
  BUSY = 'busy',
  SUSPENDED = 'suspended',
  MAINTENANCE = 'maintenance',
  OFFLINE = 'offline'
}

// Reward Models

export interface Reward {
  id: string;
  timestamp: Date;
  taskId: string;
  agentName: string;
  reward: number; // -5 to +5
  components: RewardComponents;
  metadata: RewardMetadata;
  manualOverride: boolean;
  overrideReason?: string;
}

export interface RewardComponents {
  testCoverageDelta: number;     // -1 to +1
  lintScore: number;              // 0 to 1
  securityScanScore: number;      // 0 to 1
  codeComplexityDelta: number;    // -1 to +1
  ciPipelineStatus: number;       // 0 or 1
  reviewFeedbackScore: number;    // -1 to +1
  customComponents?: Record<string, number>;
}

export interface RewardMetadata {
  evaluatorVersion: string;
  hookDurationMs: number;
  dataSource: RewardDataSource[];
  computationDetails?: Record<string, any>;
}

export interface RewardDataSource {
  type: 'ci' | 'lint' | 'security' | 'coverage' | 'review' | 'custom';
  provider: string;
  timestamp: Date;
  rawData?: any;
}

// Hook Models

export interface Hook {
  name: string;
  eventType: HookEventType;
  scriptPath: string;
  enabled: boolean;
  timeoutMs: number;
  retryCount: number;
  environment: Record<string, string>;
  permissions: HookPermissions;
  lastExecution?: HookExecution;
}

export interface HookPermissions {
  allowNetwork: boolean;
  allowedHosts?: string[];
  allowFileWrite: boolean;
  allowedPaths?: string[];
  maxMemoryMb: number;
  maxCpuMs: number;
}

export interface HookExecution {
  timestamp: Date;
  taskId: string;
  agentName: string;
  success: boolean;
  durationMs: number;
  output?: string;
  error?: string;
  retriesUsed: number;
}

export enum HookEventType {
  TASK_START = 'TaskStart',
  POST_TOOL_USE = 'PostToolUse',
  SUBAGENT_STOP = 'SubagentStop',
  TASK_COMPLETE = 'TaskComplete',
  REWARD_CALCULATED = 'RewardCalculated',
  TIER_CHANGED = 'TierChanged'
}

// Scoreboard Models

export interface ScoreboardEntry {
  agentName: string;
  tier: AgentTier;
  rollingAvgReward: number;
  totalTasks: number;
  successRate: number;
  rank: number;
  trend: TrendDirection;
  lastUpdated: Date;
}

export interface Leaderboard {
  metric: LeaderboardMetric;
  period: TimePeriod;
  entries: LeaderboardEntry[];
  generatedAt: Date;
}

export interface LeaderboardEntry extends ScoreboardEntry {
  metricValue: number;
  percentile: number;
  badges?: Badge[];
}

export enum LeaderboardMetric {
  REWARD = 'reward',
  TASKS = 'tasks',
  SUCCESS_RATE = 'success_rate',
  SPEED = 'speed',
  EFFICIENCY = 'efficiency'
}

export enum TimePeriod {
  HOUR_24 = '24h',
  DAYS_7 = '7d',
  DAYS_30 = '30d',
  ALL_TIME = 'all'
}

export enum TrendDirection {
  UP = 'up',
  DOWN = 'down',
  STABLE = 'stable'
}

export interface Badge {
  type: BadgeType;
  name: string;
  description: string;
  awardedAt: Date;
}

export enum BadgeType {
  STREAK = 'streak',
  MILESTONE = 'milestone',
  SPECIALTY = 'specialty',
  QUALITY = 'quality'
}

// Configuration Models

export interface SystemConfig {
  coordinator: CoordinatorConfig;
  evaluator: EvaluatorConfig;
  scoreboard: ScoreboardConfig;
  tiers: TierConfig;
  security: SecurityConfig;
}

export interface CoordinatorConfig {
  port: number;
  maxConcurrentAgents: number;
  taskTimeoutDefaultMs: number;
  retryPolicy: RetryPolicy;
  queueConfig: QueueConfig;
}

export interface RetryPolicy {
  maxRetries: number;
  backoffMultiplier: number;
  maxBackoffMs: number;
  retryableErrors: ErrorType[];
}

export interface QueueConfig {
  maxQueueSize: number;
  priorityBoostP0: number;
  priorityBoostP1: number;
  staleTaskThresholdMs: number;
}

export interface EvaluatorConfig {
  weights: RewardWeights;
  thresholds: EvaluatorThresholds;
  providers: EvaluatorProviders;
}

export interface RewardWeights {
  testCoverage: number;
  lintScore: number;
  securityScan: number;
  complexity: number;
  ciStatus: number;
  reviewFeedback: number;
}

export interface EvaluatorThresholds {
  minTestCoverage: number;
  maxComplexityIncrease: number;
  criticalSecurityFailThreshold: number;
  lintErrorTolerance: number;
}

export interface EvaluatorProviders {
  coverage: CoverageProvider;
  lint: LintProvider;
  security: SecurityProvider;
  ci: CIProvider;
}

export interface CoverageProvider {
  type: 'jest' | 'pytest' | 'go-test' | 'custom';
  configPath?: string;
  minimumCoverage: number;
}

export interface LintProvider {
  type: 'eslint' | 'pylint' | 'golint' | 'custom';
  configPath?: string;
  rulesets?: string[];
}

export interface SecurityProvider {
  type: 'snyk' | 'sonarqube' | 'semgrep' | 'custom';
  apiKey?: string;
  severityThreshold: 'low' | 'medium' | 'high' | 'critical';
}

export interface CIProvider {
  type: 'github-actions' | 'jenkins' | 'gitlab-ci' | 'custom';
  apiEndpoint?: string;
  requiredChecks: string[];
}

export interface ScoreboardConfig {
  retentionDays: number;
  compactOnStartup: boolean;
  backupEnabled: boolean;
  backupPath?: string;
  aggregationInterval: number;
}

export interface TierConfig {
  promotionThreshold: number;
  demotionThreshold: number;
  suspensionThreshold: number;
  evaluationWindow: number;
  gracePeriodTasks: number;
  manualOverrideEnabled: boolean;
}

export interface SecurityConfig {
  sandboxEnabled: boolean;
  allowedHosts: string[];
  forbiddenPaths: string[];
  secretsManagement: SecretsConfig;
  auditLog: AuditConfig;
}

export interface SecretsConfig {
  provider: 'env' | 'vault' | 'aws-secrets' | 'azure-keyvault';
  encryptionEnabled: boolean;
  rotationIntervalDays?: number;
}

export interface AuditConfig {
  enabled: boolean;
  retentionDays: number;
  logLevel: 'error' | 'warn' | 'info' | 'debug';
  sensitiveDataMasking: boolean;
}

// Event Models

export interface SystemEvent {
  id: string;
  type: SystemEventType;
  timestamp: Date;
  source: string;
  severity: EventSeverity;
  message: string;
  metadata?: Record<string, any>;
}

export enum SystemEventType {
  AGENT_CREATED = 'agent_created',
  AGENT_SUSPENDED = 'agent_suspended',
  AGENT_PROMOTED = 'agent_promoted',
  AGENT_DEMOTED = 'agent_demoted',
  TASK_TIMEOUT = 'task_timeout',
  HOOK_FAILED = 'hook_failed',
  EVALUATION_ERROR = 'evaluation_error',
  SYSTEM_ERROR = 'system_error',
  CONFIG_CHANGED = 'config_changed'
}

export enum EventSeverity {
  DEBUG = 'debug',
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical'
}

// Metrics Models

export interface SystemMetrics {
  timestamp: Date;
  tasks: TaskMetrics;
  agents: AgentMetrics;
  system: ResourceMetrics;
  performance: PerformanceMetrics;
}

export interface TaskMetrics {
  total: number;
  pending: number;
  inProgress: number;
  completed: number;
  failed: number;
  avgDurationMs: number;
  throughputPerHour: number;
}

export interface AgentMetrics {
  total: number;
  available: number;
  busy: number;
  suspended: number;
  byTier: Record<AgentTier, number>;
  avgReward: number;
  topPerformers: string[];
}

export interface ResourceMetrics {
  cpuUsagePercent: number;
  memoryUsageMb: number;
  diskUsageMb: number;
  networkIoMbps: number;
  goroutines?: number;
  openFileDescriptors?: number;
}

export interface PerformanceMetrics {
  coordinatorLatencyP50: number;
  coordinatorLatencyP99: number;
  evaluatorDurationP50: number;
  evaluatorDurationP99: number;
  hookExecutionP50: number;
  hookExecutionP99: number;
  queueDepth: number;
  droppedTasks: number;
}

// Repository Models

export interface AgentRepository {
  id: string;
  url: string;
  name: string;
  description?: string;
  agents: AgentReference[];
  lastSync: Date;
  syncStatus: SyncStatus;
}

export interface AgentReference {
  name: string;
  version: string;
  checksum: string;
  tier: AgentTier;
  rating: number;
  downloads: number;
  lastUpdated: Date;
}

export enum SyncStatus {
  SYNCED = 'synced',
  SYNCING = 'syncing',
  FAILED = 'failed',
  PENDING = 'pending'
}

// Session Models

export interface CoordinatorSession {
  id: string;
  startedAt: Date;
  projectId: string;
  activeAgents: Set<string>;
  taskQueue: TaskQueueItem[];
  metrics: SessionMetrics;
}

export interface TaskQueueItem {
  task: Task;
  priority: number;
  enqueuedAt: Date;
  attempts: number;
  lastError?: string;
}

export interface SessionMetrics {
  tasksProcessed: number;
  avgProcessingTime: number;
  errorRate: number;
  agentUtilization: Record<string, number>;
}