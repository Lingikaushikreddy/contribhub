/**
 * Shared type definitions for the ContribHub GitHub Action.
 */

export interface IssuePayload {
  owner: string;
  repo: string;
  issueNumber: number;
  title: string;
  body: string;
  author: string;
  labels: string[];
  createdAt: string;
  updatedAt: string;
  htmlUrl: string;
}

export interface TriageResult {
  category: IssueCategory;
  priority: IssuePriority;
  complexity: IssueComplexity;
  confidence: number;
  labels: LabelRecommendation[];
  qualityScore: number;
  qualitySuggestions: string[];
  responseDraftId: string | null;
  processingTimeMs: number;
}

export interface LabelRecommendation {
  name: string;
  color: string;
  description: string;
  confidence: number;
}

export interface DuplicateResult {
  hasDuplicates: boolean;
  duplicates: DuplicateMatch[];
  processingTimeMs: number;
}

export interface DuplicateMatch {
  issueNumber: number;
  issueTitle: string;
  similarity: number;
  htmlUrl: string;
  state: 'open' | 'closed';
}

export interface EventReport {
  repoFullName: string;
  issueNumber: number;
  eventType: string;
  labelsApplied: string[];
  duplicatesFound: number;
  confidence: number;
  processingTimeMs: number;
}

export type IssueCategory = 'bug' | 'feature' | 'question' | 'docs' | 'chore' | 'security' | 'performance';
export type IssuePriority = 'P0' | 'P1' | 'P2' | 'P3';
export type IssueComplexity = 'trivial' | 'easy' | 'medium' | 'hard' | 'expert';

export interface ContribHubConfig {
  version: number;
  triage: TriageConfig;
  labels: LabelsConfig;
  responses: ResponsesConfig;
  duplicates: DuplicatesConfig;
  notifications: NotificationsConfig;
}

export interface TriageConfig {
  enabled: boolean;
  autoLabel: boolean;
  autoRespond: boolean;
  autoClose: boolean;
  confidenceThreshold: number;
  ignoreLabels: string[];
  ignoreAuthors: string[];
  priorityKeywords: PriorityKeywords;
}

export interface PriorityKeywords {
  P0: string[];
  P1: string[];
  P2: string[];
  P3: string[];
}

export interface LabelsConfig {
  prefix: string;
  useEmoji: boolean;
  categoryColors: Record<string, string>;
  priorityColors: Record<string, string>;
  complexityColors: Record<string, string>;
}

export interface ResponsesConfig {
  tone: 'formal' | 'friendly' | 'minimal';
  language: string;
  includeLabels: boolean;
  includePriority: boolean;
  includeComplexity: boolean;
  customFooter: string;
}

export interface DuplicatesConfig {
  enabled: boolean;
  similarityThreshold: number;
  searchScope: 'open' | 'all';
  maxResults: number;
  commentOnDuplicate: boolean;
}

export interface NotificationsConfig {
  slackWebhook: string;
  discordWebhook: string;
  notifyOnP0: boolean;
  notifyOnDuplicate: boolean;
}

export interface ActionInputs {
  apiKey: string;
  configPath: string;
  apiBaseUrl: string;
  dryRun: boolean;
}
