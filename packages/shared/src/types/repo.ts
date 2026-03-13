/**
 * Repository domain types for ContribHub.
 * Mirrors the API schema at apps/api/app/schemas/repo.py
 */

export interface Repo {
  id: string;
  github_id: number;
  owner: string;
  name: string;
  full_name: string;
  description: string | null;
  language: string | null;
  languages: Record<string, number>;
  topics: string[];
  stars: number;
  forks: number;
  open_issues_count: number;
  is_active: boolean;
  installation_id: number | null;
  config: RepoConfig | null;
  health_score: RepoHealthScore | null;
  created_at: string;
  updated_at: string;
  last_synced_at: string | null;
}

export interface RepoConfig {
  triage_enabled: boolean;
  matching_enabled: boolean;
  auto_label: boolean;
  auto_respond: boolean;
  response_tone: 'formal' | 'friendly' | 'minimal';
  excluded_labels: string[];
  trusted_reporters: string[];
  duplicate_detection: boolean;
  duplicate_similarity_threshold: number;
  confidence_threshold: number;
}

export interface RepoHealthScore {
  overall: number;
  documentation: number;
  responsiveness: number;
  issue_resolution: number;
  community: number;
  code_quality: number;
  calculated_at: string;
}

export interface RepoCreate {
  github_id: number;
  owner: string;
  name: string;
  full_name: string;
  description: string | null;
  language: string | null;
  installation_id: number;
}

export interface RepoUpdate {
  description?: string | null;
  language?: string | null;
  languages?: Record<string, number>;
  topics?: string[];
  stars?: number;
  forks?: number;
  open_issues_count?: number;
  is_active?: boolean;
  config?: Partial<RepoConfig>;
}

export interface RepoSummary {
  id: string;
  full_name: string;
  description: string | null;
  language: string | null;
  stars: number;
  open_issues_count: number;
  health_score: number | null;
}
