/**
 * Contributor-issue matching types for ContribHub.
 * Mirrors the API schema at apps/api/app/schemas/match.py
 */

export enum MatchStatus {
  SUGGESTED = 'suggested',
  NOTIFIED = 'notified',
  ACCEPTED = 'accepted',
  DECLINED = 'declined',
  EXPIRED = 'expired',
  COMPLETED = 'completed',
}

export interface Match {
  id: string;
  issue_id: string;
  user_id: string;
  score: MatchScore;
  overall_score: number;
  status: MatchStatus;
  reason: string;
  notified_at: string | null;
  responded_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface MatchScore {
  skill_match: number;
  experience_match: number;
  availability_match: number;
  history_match: number;
  recency_bonus: number;
  overall: number;
}

export interface MatchFeedback {
  match_id: string;
  user_id: string;
  rating: 1 | 2 | 3 | 4 | 5;
  difficulty_rating: 'too_easy' | 'just_right' | 'too_hard';
  would_do_again: boolean;
  time_spent_hours: number | null;
  comment: string | null;
  created_at: string;
}

export interface MatchRequest {
  issue_id: string;
  max_matches?: number;
  required_skills?: string[];
  min_experience_level?: string;
}

export interface MatchResult {
  issue_id: string;
  matches: Match[];
  total_candidates_evaluated: number;
  matching_duration_ms: number;
}

export interface MatchSummary {
  id: string;
  issue_title: string;
  issue_number: number;
  repo_full_name: string;
  overall_score: number;
  status: MatchStatus;
  reason: string;
  created_at: string;
}

export interface MatchFilter {
  user_id?: string;
  issue_id?: string;
  status?: MatchStatus;
  min_score?: number;
}
