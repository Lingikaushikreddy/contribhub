/**
 * .contribhub.yml configuration types.
 * This is the schema for the per-repository configuration file.
 */

export interface ContribHubConfig {
  version: 1;
  triage: TriageConfig;
  matching: MatchingConfig;
}

export interface TriageConfig {
  enabled: boolean;
  labels: TriageLabelConfig;
  auto_label_confidence_threshold: number;
  duplicate_detection: DuplicateDetectionConfig;
  response_drafts: ResponseDraftConfig;
  excluded_labels: string[];
  trusted_reporters: string[];
}

export interface TriageLabelConfig {
  categories: string[];
  priorities: string[];
  complexity: string[];
}

export interface DuplicateDetectionConfig {
  enabled: boolean;
  similarity_threshold: number;
}

export interface ResponseDraftConfig {
  enabled: boolean;
  tone: 'formal' | 'friendly' | 'minimal';
  auto_post_quality_requests: boolean;
}

export interface MatchingConfig {
  enabled: boolean;
  exclude_dormant_days: number;
  exclude_claimed_issues: boolean;
}

export interface PartialContribHubConfig {
  version?: 1;
  triage?: Partial<TriageConfig> & {
    labels?: Partial<TriageLabelConfig>;
    duplicate_detection?: Partial<DuplicateDetectionConfig>;
    response_drafts?: Partial<ResponseDraftConfig>;
  };
  matching?: Partial<MatchingConfig>;
}
