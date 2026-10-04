export type SourceType = 'jira' | 'openapi' | 'architecture' | 'upload' | 'usecase' | 'requirement';
export type BuildStage = 'Draft' | 'Understand' | 'Design' | 'Forge' | 'Prove' | 'Release' | 'Replay' | 'Error';
export type BuildStatus = 'Draft' | 'Running' | 'Awaiting Approval' | 'Refined' | 'Deployed' | 'Blocked' | 'Failed'| 'Completed';;
export type ApprovalGate = 'requirements' | 'blueprint' | 'artifacts' | 'skill' | 'release' | null;

export interface BuildCreateRequest {
  sourceType: SourceType;
  title: string;
  sourceText: string;
  files: string[];
  fileContents: { name: string; contentBase64: string }[];
}

export interface RequirementItem {
  id: string;
  text: string;
  priority: 'High' | 'Medium' | 'Low';
  confidence: number;
}

export interface AgentState {
  name: string;
  role: string;
  status: 'Ready' | 'Running' | 'Waiting' | 'Blocked' | 'Failed';
  detail: string;
  lastAction: string;
  tokens: number;
}

export interface AuditEvent {
  time: string;
  stage: string;
  message: string;
  agent: string | null;
  severity: 'info' | 'warning' | 'error';
  metadata: Record<string, unknown>;
}

export interface Blueprint {
  application: string;
  frontend: string;
  backend: string;
  data: string;
  storage: string;
  messaging: string;
  identity: string;
  deployment: string;
  security: string[];
  reasoning: string[];
  mode: string;
  assumptions: string[];
  openQuestions: string[];
}

export type BlueprintUpdate = Pick<Blueprint,
  'application' | 'frontend' | 'backend' | 'data' | 'storage' | 'messaging' | 'identity' | 'deployment' | 'security'
>;

export interface ProofFailure {
  failedTest: string;
  expected: string;
  received: string;
}

export interface ProofIteration {
  iteration: number;
  action: string;
  status: 'Detected' | 'Patched' | 'Passed';
}

export interface CriticFinding {
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  file: string | null;
  issue: string;
  recommendation: string;
}

export interface ProofResult {
  codeQuality: number;
  specFidelity: number;
  failureInjected: boolean;
  failure?: ProofFailure;
  iterations: ProofIteration[];
  integration: string;
  code: Record<string, string>;
  files: string[];
  artifacts: Record<string, string>;
  generatorMode: string;
  criticMode: string;
  criticSummary: string;
  criticFindings: CriticFinding[];
  requirementCoverage: string[];
  testPlan: string[];
  runtimeStatus: string;
  checks: Record<string, string>;
}

export interface SkillProposal {
  name: string;
  version: string;
  reason: string;
  status: 'Pending Approval' | 'Approved';
}

export type SkillRecipeStatus = 'draft' | 'pending_approval' | 'approved' | 'deprecated' | 'rejected';

export interface SkillRecipe {
  id: string;
  agent: string;
  title: string;
  tags: string[];
  useWhen: string;
  inputs: string[];
  steps: string[];
  doneWhen: string;
  pitfalls: string[];
  output: string;
  version: string;
  status: SkillRecipeStatus;
  audit: AuditEvent[];
}

export interface SkillUsage {
  id: string;
  version: string;
  usage: 'retrieved' | 'applied' | 'skipped';
  reason: string;
}

export interface ReleaseResult {
  specFidelity: number;
  unitTests: string;
  contractTests: string;
  securityScan: string;
  dependencyScan: string;
  containerImageScan: string;
  selfHealingIterations: number;
  target: string;
  privateNetwork: boolean;
  publicIngress: boolean;
  deploymentUrl?: string;
}

export interface SecurityReview {
  mode: string;
  decision: 'No high or critical findings' | 'Block release';
  summary: string;
  checks: Record<string, string>;
  findings: CriticFinding[];
  scannedFiles: number;
  skillsUsed: SkillUsage[];
  externalScans: Record<string, string>;
}

export interface DeploymentPlan {
  status: 'ready' | 'blocked';
  summary: string;
  target: string;
  imageTag: string;
  humanApprovalRequired: boolean;
  checks: Record<string, string>;
  blockers: string[];
  artifactManifest: { path: string; sizeBytes: number; sha256: string }[];
}

export interface BuildMetrics {
  tokens: number;
  toolCalls: number;
  buildSeconds: number;
  selfHealIterations: number;
  successRate: number;
}

export interface BuildState {
  id: string;
  title: string;
  sourceType: SourceType;
  sourceText: string;
  files: string[];
  stage: BuildStage;
  progress: number;
  status: BuildStatus;
  requirements: RequirementItem[];
  requirementSummary: string;
  acceptanceCriteria: string[];
  dependencies: string[];
  risks: string[];
  specConfidence: number;
  agentMode: string;
  blueprint: Blueprint | null;
  proof: ProofResult | null;
  release: ReleaseResult | null;
  securityReview: SecurityReview | null;
  deploymentPlan: DeploymentPlan | null;
  skillProposal: SkillProposal | null;
  skillsUsed: SkillUsage[];
  agents: AgentState[];
  audit: AuditEvent[];
  metrics: BuildMetrics;
  approvalGate: ApprovalGate;
  error: string | null;
}
