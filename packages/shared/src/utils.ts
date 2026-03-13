/**
 * Shared utility functions for ContribHub.
 * Pure functions with no side effects — safe to use in any environment.
 */

import {
  CATEGORY_COLORS,
  PRIORITY_COLORS,
  COMPLEXITY_LEVELS,
  HEALTH_THRESHOLDS,
} from './constants';

// ---------------------------------------------------------------------------
// Time formatting
// ---------------------------------------------------------------------------

/**
 * Returns a human-readable relative time string (e.g. "3 hours ago", "2 days ago").
 * Handles future dates by returning "just now".
 */
export function formatTimeAgo(date: string | Date): string {
  const now = Date.now();
  const then = typeof date === 'string' ? new Date(date).getTime() : date.getTime();
  const diffMs = now - then;

  if (diffMs < 0) return 'just now';

  const seconds = Math.floor(diffMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const weeks = Math.floor(days / 7);
  const months = Math.floor(days / 30);
  const years = Math.floor(days / 365);

  if (seconds < 60) return 'just now';
  if (minutes === 1) return '1 minute ago';
  if (minutes < 60) return `${minutes} minutes ago`;
  if (hours === 1) return '1 hour ago';
  if (hours < 24) return `${hours} hours ago`;
  if (days === 1) return '1 day ago';
  if (days < 7) return `${days} days ago`;
  if (weeks === 1) return '1 week ago';
  if (weeks < 5) return `${weeks} weeks ago`;
  if (months === 1) return '1 month ago';
  if (months < 12) return `${months} months ago`;
  if (years === 1) return '1 year ago';
  return `${years} years ago`;
}

// ---------------------------------------------------------------------------
// Health score helpers
// ---------------------------------------------------------------------------

/**
 * Returns 1-5 filled dots based on a 0-100 health score.
 * Used by the HealthDots component.
 */
export function calculateHealthDots(score: number): number {
  if (score >= HEALTH_THRESHOLDS.excellent) return 5;
  if (score >= HEALTH_THRESHOLDS.good) return 4;
  if (score >= HEALTH_THRESHOLDS.fair) return 3;
  if (score >= HEALTH_THRESHOLDS.poor) return 2;
  return 1;
}

/**
 * Returns a label and Tailwind color class for a health score.
 */
export function getHealthLabel(score: number): { label: string; color: string } {
  if (score >= HEALTH_THRESHOLDS.excellent) return { label: 'Excellent', color: 'text-emerald-400' };
  if (score >= HEALTH_THRESHOLDS.good) return { label: 'Good', color: 'text-green-400' };
  if (score >= HEALTH_THRESHOLDS.fair) return { label: 'Fair', color: 'text-yellow-400' };
  if (score >= HEALTH_THRESHOLDS.poor) return { label: 'Poor', color: 'text-orange-400' };
  return { label: 'Critical', color: 'text-red-400' };
}

// ---------------------------------------------------------------------------
// Difficulty / complexity helpers
// ---------------------------------------------------------------------------

/**
 * Maps a complexity level string to its display metadata.
 * Falls back to "moderate" if the level is unrecognized.
 */
export function getDifficultyLevel(
  level: string,
): { range: [number, number]; color: string; label: string } {
  return COMPLEXITY_LEVELS[level] ?? COMPLEXITY_LEVELS['moderate'];
}

/**
 * Returns a 1-10 numeric midpoint for a named complexity level.
 */
export function complexityToNumeric(level: string): number {
  const entry = COMPLEXITY_LEVELS[level];
  if (!entry) return 5;
  const [low, high] = entry.range;
  return Math.round((low + high) / 2);
}

// ---------------------------------------------------------------------------
// Category / priority color helpers
// ---------------------------------------------------------------------------

/**
 * Returns Tailwind classes for a given issue category.
 * Falls back to neutral zinc colors for unknown categories.
 */
export function getCategoryColor(
  category: string,
): { bg: string; text: string; border: string } {
  return (
    CATEGORY_COLORS[category] ?? {
      bg: 'bg-zinc-500/10',
      text: 'text-zinc-400',
      border: 'border-zinc-500/20',
    }
  );
}

/**
 * Returns Tailwind classes and a display label for a given priority.
 * Falls back to neutral styling for unknown priorities.
 */
export function getPriorityColor(
  priority: string,
): { bg: string; text: string; label: string } {
  return (
    PRIORITY_COLORS[priority] ?? {
      bg: 'bg-zinc-500/10',
      text: 'text-zinc-400',
      label: priority,
    }
  );
}

// ---------------------------------------------------------------------------
// Text helpers
// ---------------------------------------------------------------------------

/**
 * Truncates text to a maximum length, appending an ellipsis if truncated.
 * Breaks at the last word boundary before maxLength.
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;

  const truncated = text.slice(0, maxLength);
  const lastSpace = truncated.lastIndexOf(' ');

  if (lastSpace > maxLength * 0.5) {
    return truncated.slice(0, lastSpace) + '...';
  }

  return truncated + '...';
}

/**
 * Converts a slug-style string to title case.
 * Example: "good-first-issue" -> "Good First Issue"
 */
export function slugToTitle(slug: string): string {
  return slug
    .replace(/[-_]/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

// ---------------------------------------------------------------------------
// Number formatting
// ---------------------------------------------------------------------------

/**
 * Formats a number with compact suffixes (e.g. 1.2k, 3.4M).
 */
export function formatCompactNumber(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}k`;
  return value.toString();
}

/**
 * Formats a percentage value to one decimal place with a % suffix.
 * Clamps the value between 0 and 100.
 */
export function formatPercentage(value: number): string {
  const clamped = Math.min(100, Math.max(0, value));
  return `${clamped.toFixed(1)}%`;
}

// ---------------------------------------------------------------------------
// Score / confidence helpers
// ---------------------------------------------------------------------------

/**
 * Returns a Tailwind color class for a 0-1 confidence score.
 */
export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.9) return 'text-emerald-400';
  if (confidence >= 0.75) return 'text-green-400';
  if (confidence >= 0.5) return 'text-yellow-400';
  if (confidence >= 0.25) return 'text-orange-400';
  return 'text-red-400';
}

/**
 * Returns a human-readable label for a 0-1 confidence score.
 */
export function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.9) return 'Very High';
  if (confidence >= 0.75) return 'High';
  if (confidence >= 0.5) return 'Medium';
  if (confidence >= 0.25) return 'Low';
  return 'Very Low';
}

// ---------------------------------------------------------------------------
// Array / object helpers
// ---------------------------------------------------------------------------

/**
 * Groups an array of items by a key extracted via the selector function.
 */
export function groupBy<T>(items: T[], selector: (item: T) => string): Record<string, T[]> {
  const result: Record<string, T[]> = {};
  for (const item of items) {
    const key = selector(item);
    if (!result[key]) {
      result[key] = [];
    }
    result[key].push(item);
  }
  return result;
}

/**
 * Returns unique values from an array, preserving order.
 */
export function unique<T>(items: T[]): T[] {
  return [...new Set(items)];
}
