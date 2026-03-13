/**
 * Shared constants for ContribHub.
 * UI color mappings, thresholds, and default configuration values
 * used across the frontend and GitHub Action.
 */

// ---------------------------------------------------------------------------
// Category colors — used by Badge and label components
// ---------------------------------------------------------------------------
export const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  bug: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/20' },
  feature: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/20' },
  enhancement: { bg: 'bg-violet-500/10', text: 'text-violet-400', border: 'border-violet-500/20' },
  documentation: { bg: 'bg-green-500/10', text: 'text-green-400', border: 'border-green-500/20' },
  question: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/20' },
  security: { bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/20' },
  performance: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20' },
  testing: { bg: 'bg-cyan-500/10', text: 'text-cyan-400', border: 'border-cyan-500/20' },
  refactor: { bg: 'bg-indigo-500/10', text: 'text-indigo-400', border: 'border-indigo-500/20' },
  chore: { bg: 'bg-zinc-500/10', text: 'text-zinc-400', border: 'border-zinc-500/20' },
  'ci-cd': { bg: 'bg-slate-500/10', text: 'text-slate-400', border: 'border-slate-500/20' },
  design: { bg: 'bg-pink-500/10', text: 'text-pink-400', border: 'border-pink-500/20' },
};

// ---------------------------------------------------------------------------
// Priority colors — used by priority badges and triage views
// ---------------------------------------------------------------------------
export const PRIORITY_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  critical: { bg: 'bg-red-600/10', text: 'text-red-500', label: 'Critical' },
  high: { bg: 'bg-orange-500/10', text: 'text-orange-400', label: 'High' },
  medium: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', label: 'Medium' },
  low: { bg: 'bg-zinc-500/10', text: 'text-zinc-400', label: 'Low' },
};

// ---------------------------------------------------------------------------
// Complexity levels — maps numeric score ranges to display labels
// ---------------------------------------------------------------------------
export const COMPLEXITY_LEVELS: Record<
  string,
  { range: [number, number]; color: string; label: string }
> = {
  trivial: { range: [1, 2], color: 'emerald', label: 'Trivial' },
  easy: { range: [3, 4], color: 'green', label: 'Easy' },
  moderate: { range: [5, 6], color: 'yellow', label: 'Moderate' },
  hard: { range: [7, 8], color: 'orange', label: 'Hard' },
  expert: { range: [9, 10], color: 'red', label: 'Expert' },
};

// ---------------------------------------------------------------------------
// Health score thresholds — determines badge color for repo health
// ---------------------------------------------------------------------------
export const HEALTH_THRESHOLDS = {
  excellent: 80,
  good: 60,
  fair: 40,
  poor: 20,
} as const;

// ---------------------------------------------------------------------------
// Default .contribhub.yml configuration
// ---------------------------------------------------------------------------
export const DEFAULT_CONFIG = {
  version: 1 as const,
  triage: {
    enabled: true,
    labels: {
      categories: ['bug', 'feature', 'enhancement', 'documentation', 'question', 'chore'],
      priorities: ['critical', 'high', 'medium', 'low'],
      complexity: ['trivial', 'easy', 'moderate', 'hard', 'expert'],
    },
    auto_label_confidence_threshold: 0.75,
    duplicate_detection: {
      enabled: true,
      similarity_threshold: 0.85,
    },
    response_drafts: {
      enabled: true,
      tone: 'friendly' as const,
      auto_post_quality_requests: false,
    },
    excluded_labels: ['wontfix', 'invalid', 'duplicate'],
    trusted_reporters: [],
  },
  matching: {
    enabled: true,
    exclude_dormant_days: 90,
    exclude_claimed_issues: true,
  },
};

// ---------------------------------------------------------------------------
// Pagination defaults
// ---------------------------------------------------------------------------
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PER_PAGE: 20,
  MAX_PER_PAGE: 100,
} as const;

// ---------------------------------------------------------------------------
// API rate limiting
// ---------------------------------------------------------------------------
export const RATE_LIMITS = {
  DEFAULT_RPM: 60,
  AUTHENTICATED_RPM: 300,
  WEBHOOK_RPM: 1000,
} as const;

// ---------------------------------------------------------------------------
// Match scoring weights
// ---------------------------------------------------------------------------
export const MATCH_WEIGHTS = {
  SKILL_MATCH: 0.35,
  EXPERIENCE_MATCH: 0.25,
  AVAILABILITY_MATCH: 0.15,
  HISTORY_MATCH: 0.15,
  RECENCY_BONUS: 0.10,
} as const;
