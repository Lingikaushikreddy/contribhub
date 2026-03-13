/**
 * Skill and contributor profile types for ContribHub.
 * Mirrors the API schema at apps/api/app/schemas/skill.py
 */

export enum SkillCategory {
  LANGUAGE = 'language',
  FRAMEWORK = 'framework',
  TOOL = 'tool',
  PLATFORM = 'platform',
  DOMAIN = 'domain',
  SOFT_SKILL = 'soft_skill',
}

export interface Skill {
  id: string;
  name: string;
  normalized_name: string;
  category: SkillCategory;
  aliases: string[];
  parent_skill_id: string | null;
}

export interface SkillProfile {
  skill_id: string;
  skill_name: string;
  category: SkillCategory;
  proficiency: number;
  evidence_count: number;
  last_used_at: string | null;
  source: SkillSource;
}

export enum SkillSource {
  GITHUB_LANGUAGE = 'github_language',
  GITHUB_TOPIC = 'github_topic',
  PR_ANALYSIS = 'pr_analysis',
  SELF_REPORTED = 'self_reported',
  INFERRED = 'inferred',
}

export interface ContributorProfile {
  user_id: string;
  username: string;
  avatar_url: string;
  skills: SkillProfile[];
  languages: LanguageStat[];
  total_prs: number;
  total_issues: number;
  repos_contributed_to: string[];
  active_since: string;
  last_active_at: string;
  availability_hours_per_week: number | null;
  preferred_categories: string[];
  preferred_complexity: string[];
  timezone: string | null;
}

export interface LanguageStat {
  language: string;
  bytes: number;
  percentage: number;
  repos_count: number;
}

export interface SkillGap {
  skill_name: string;
  required_proficiency: number;
  current_proficiency: number;
  gap: number;
}

export interface SkillMatch {
  skill_name: string;
  required: boolean;
  proficiency: number;
  match_quality: 'exact' | 'partial' | 'missing';
}
