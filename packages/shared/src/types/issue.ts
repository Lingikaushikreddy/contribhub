/**
 * Issue domain types for ContribHub.
 * Mirrors the API schema at apps/api/app/schemas/issue.py
 */

export enum IssueCategory {
  BUG = 'bug',
  FEATURE = 'feature',
  ENHANCEMENT = 'enhancement',
  DOCUMENTATION = 'documentation',
  QUESTION = 'question',
  SECURITY = 'security',
  PERFORMANCE = 'performance',
  TESTING = 'testing',
  REFACTOR = 'refactor',
  CHORE = 'chore',
  CI_CD = 'ci-cd',
  DESIGN = 'design',
}

export enum IssuePriority {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export enum ComplexityLevel {
  TRIVIAL = 'trivial',
  EASY = 'easy',
  MODERATE = 'moderate',
  HARD = 'hard',
  EXPERT = 'expert',
}

export enum IssueStatus {
  OPEN = 'open',
  TRIAGED = 'triaged',
  ASSIGNED = 'assigned',
  IN_PROGRESS = 'in_progress',
  CLOSED = 'closed',
}

export interface Issue {
  id: string;
  repo_id: string;
  github_id: number;
  number: number;
  title: string;
  body: string | null;
  author: string;
  author_avatar_url: string | null;
  labels: string[];
  status: IssueStatus;
  category: IssueCategory | null;
  priority: IssuePriority | null;
  complexity: ComplexityLevel | null;
  category_confidence: number | null;
  priority_confidence: number | null;
  complexity_confidence: number | null;
  estimated_hours: number | null;
  required_skills: string[];
  is_good_first_issue: boolean;
  is_duplicate: boolean;
  duplicate_of_id: string | null;
  assigned_to: string | null;
  triaged_at: string | null;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
}

export interface IssueCreate {
  repo_id: string;
  github_id: number;
  number: number;
  title: string;
  body: string | null;
  author: string;
  author_avatar_url: string | null;
  labels: string[];
}

export interface IssueUpdate {
  title?: string;
  body?: string | null;
  labels?: string[];
  status?: IssueStatus;
  category?: IssueCategory | null;
  priority?: IssuePriority | null;
  complexity?: ComplexityLevel | null;
  category_confidence?: number | null;
  priority_confidence?: number | null;
  complexity_confidence?: number | null;
  estimated_hours?: number | null;
  required_skills?: string[];
  is_good_first_issue?: boolean;
  is_duplicate?: boolean;
  duplicate_of_id?: string | null;
  assigned_to?: string | null;
}

export interface IssueSummary {
  id: string;
  repo_full_name: string;
  number: number;
  title: string;
  category: IssueCategory | null;
  priority: IssuePriority | null;
  complexity: ComplexityLevel | null;
  is_good_first_issue: boolean;
  created_at: string;
}

export interface IssueFilter {
  repo_id?: string;
  category?: IssueCategory;
  priority?: IssuePriority;
  complexity?: ComplexityLevel;
  status?: IssueStatus;
  is_good_first_issue?: boolean;
  labels?: string[];
  search?: string;
}
