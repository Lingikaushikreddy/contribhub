// ─── Domain Types ───────────────────────────────────────────────────────────

export type IssueCategory = "bug" | "feature" | "question" | "docs" | "chore" | "security" | "performance";
export type IssuePriority = "P0" | "P1" | "P2" | "P3";
export type IssueComplexity = "trivial" | "easy" | "medium" | "hard" | "expert";
export type IssueState = "open" | "closed" | "triaged" | "in_progress";
export type TriageAction = "labeled" | "assigned" | "responded" | "closed" | "duplicated";
export type HealthLevel = 1 | 2 | 3 | 4 | 5;

export interface Repo {
  id: string;
  name: string;
  fullName: string;
  description: string;
  language: string;
  stars: number;
  forks: number;
  healthScore: number;
  healthBreakdown: HealthBreakdown;
  issuesThisWeek: number;
  lastSynced: string;
  avatarUrl: string;
  installationId: string;
}

export interface HealthBreakdown {
  documentation: number;
  responsiveness: number;
  issueResolution: number;
  communityEngagement: number;
  codeQuality: number;
  releaseFrequency: number;
}

export interface Issue {
  id: string;
  number: number;
  title: string;
  body: string;
  state: IssueState;
  category: IssueCategory;
  priority: IssuePriority;
  complexity: IssueComplexity;
  labels: string[];
  author: GitHubUser;
  assignees: GitHubUser[];
  createdAt: string;
  updatedAt: string;
  repoId: string;
  repoName: string;
  htmlUrl: string;
  confidence: number;
  estimatedMinutes: number;
  prerequisites: string[];
}

export interface TriageEvent {
  id: string;
  issueId: string;
  issueNumber: number;
  issueTitle: string;
  repoName: string;
  action: TriageAction;
  category: IssueCategory;
  priority: IssuePriority;
  confidence: number;
  draftResponse: string;
  duplicates: DuplicateResult[];
  labels: LabelSuggestion[];
  status: "pending" | "approved" | "discarded";
  createdAt: string;
}

export interface DuplicateResult {
  issueNumber: number;
  issueTitle: string;
  similarity: number;
  htmlUrl: string;
}

export interface LabelSuggestion {
  name: string;
  confidence: number;
  color: string;
}

export interface GitHubUser {
  login: string;
  avatarUrl: string;
  htmlUrl: string;
}

export interface TriageStats {
  totalTriaged: number;
  aiAccuracy: number;
  avgResponseTime: number;
  activeContributors: number;
  issueVolume: DailyCount[];
  categoryBreakdown: CategoryCount[];
  priorityDistribution: PriorityCount[];
  recentEvents: TriageEvent[];
}

export interface DailyCount {
  date: string;
  count: number;
}

export interface CategoryCount {
  category: IssueCategory;
  count: number;
}

export interface PriorityCount {
  priority: IssuePriority;
  count: number;
}

export interface Recommendation {
  id: string;
  issue: Issue;
  matchScore: number;
  healthLevel: HealthLevel;
  difficulty: number;
  estimatedMinutes: number;
  prerequisites: string[];
  maintainerResponseTime: string;
  repoAvatarUrl: string;
}

export interface SkillProfile {
  username: string;
  avatarUrl: string;
  bio: string;
  skills: SkillCategory[];
  languages: LanguageProficiency[];
  contributions: ContributionEntry[];
  domains: string[];
  isPublic: boolean;
  totalContributions: number;
  currentStreak: number;
  longestStreak: number;
}

export interface SkillCategory {
  name: string;
  skills: Skill[];
}

export interface Skill {
  name: string;
  proficiency: number; // 0-100
  endorsements: number;
}

export interface LanguageProficiency {
  language: string;
  proficiency: number; // 0-100
  linesWritten: number;
  color: string;
}

export interface ContributionEntry {
  id: string;
  repoName: string;
  issueTitle: string;
  difficulty: IssueComplexity;
  completedAt: string;
  htmlUrl: string;
}

export interface FeedbackPayload {
  recommendationId: string;
  type: "positive" | "negative";
  reason?: "too_hard" | "too_easy" | "not_interested" | "already_taken";
}

export interface TriageConfig {
  labelMapping: Record<string, string>;
  responseTone: "formal" | "friendly" | "minimal";
  autoApproveThreshold: number;
  enableDuplicateDetection: boolean;
  enableAutoLabeling: boolean;
  enableAutoResponse: boolean;
}

// ─── Filter Types ───────────────────────────────────────────────────────────

export interface IssueFilters {
  category?: IssueCategory;
  priority?: IssuePriority;
  complexity?: IssueComplexity;
  state?: IssueState;
  search?: string;
}

export interface RecommendationFilters {
  language?: string;
  difficulty?: IssueComplexity;
  domain?: string;
}
