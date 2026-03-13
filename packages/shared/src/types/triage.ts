/**
 * Triage engine types for ContribHub.
 * Mirrors the API schema at apps/api/app/schemas/triage.py
 */

import type { IssueCategory, IssuePriority, ComplexityLevel } from './issue';

export enum ResponseStatus {
  DRAFT = 'draft',
  APPROVED = 'approved',
  POSTED = 'posted',
  REJECTED = 'rejected',
}

export interface TriageEvent {
  id: string;
  issue_id: string;
  repo_id: string;
  triggered_by: 'webhook' | 'manual' | 'schedule';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result: TriageResult | null;
  error: string | null;
  duration_ms: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface TriageResult {
  category: IssueCategory;
  category_confidence: number;
  priority: IssuePriority;
  priority_confidence: number;
  complexity: ComplexityLevel;
  complexity_confidence: number;
  estimated_hours: number | null;
  required_skills: string[];
  is_good_first_issue: boolean;
  is_duplicate: boolean;
  duplicate_issue_number: number | null;
  duplicate_similarity: number | null;
  suggested_labels: string[];
  response_draft: ResponseDraft | null;
  reasoning: string;
}

export interface ResponseDraft {
  id: string;
  issue_id: string;
  triage_event_id: string;
  content: string;
  tone: 'formal' | 'friendly' | 'minimal';
  status: ResponseStatus;
  posted_at: string | null;
  posted_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface TriageSummary {
  total_triaged: number;
  auto_labeled: number;
  duplicates_detected: number;
  responses_drafted: number;
  responses_posted: number;
  average_confidence: number;
  average_duration_ms: number;
}

export interface TriageOverride {
  issue_id: string;
  category?: IssueCategory;
  priority?: IssuePriority;
  complexity?: ComplexityLevel;
  labels?: string[];
  reason: string;
}
