/**
 * Repository health score types for ContribHub.
 * Mirrors the API schema at apps/api/app/schemas/health.py
 */

export enum HealthCategory {
  DOCUMENTATION = 'documentation',
  RESPONSIVENESS = 'responsiveness',
  ISSUE_RESOLUTION = 'issue_resolution',
  COMMUNITY = 'community',
  CODE_QUALITY = 'code_quality',
}

export interface HealthScore {
  repo_id: string;
  overall: number;
  breakdown: HealthBreakdown;
  trend: HealthTrend;
  recommendations: HealthRecommendation[];
  calculated_at: string;
}

export interface HealthBreakdown {
  documentation: HealthCategoryScore;
  responsiveness: HealthCategoryScore;
  issue_resolution: HealthCategoryScore;
  community: HealthCategoryScore;
  code_quality: HealthCategoryScore;
}

export interface HealthCategoryScore {
  score: number;
  weight: number;
  metrics: HealthMetric[];
}

export interface HealthMetric {
  name: string;
  value: number;
  max_value: number;
  unit: string;
  description: string;
}

export interface HealthTrend {
  direction: 'improving' | 'stable' | 'declining';
  change_30d: number;
  change_90d: number;
  history: HealthHistoryPoint[];
}

export interface HealthHistoryPoint {
  date: string;
  overall: number;
  documentation: number;
  responsiveness: number;
  issue_resolution: number;
  community: number;
  code_quality: number;
}

export interface HealthRecommendation {
  category: HealthCategory;
  severity: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  action: string;
  estimated_impact: number;
}
