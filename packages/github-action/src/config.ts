/**
 * Configuration parser and validator for .contribhub.yml files.
 *
 * Reads the config from the repository, validates it with Zod, and applies
 * sensible defaults for any omitted fields.
 */

import * as core from '@actions/core';
import * as github from '@actions/github';
import YAML from 'yaml';
import { z } from 'zod';
import type { ContribHubConfig } from './types';

const PriorityKeywordsSchema = z.object({
  P0: z.array(z.string()).default(['crash', 'data loss', 'security vulnerability', 'production down']),
  P1: z.array(z.string()).default(['broken', 'regression', 'blocker', 'critical']),
  P2: z.array(z.string()).default(['bug', 'error', 'unexpected', 'wrong']),
  P3: z.array(z.string()).default(['minor', 'cosmetic', 'typo', 'enhancement']),
});

const TriageConfigSchema = z.object({
  enabled: z.boolean().default(true),
  autoLabel: z.boolean().default(true),
  autoRespond: z.boolean().default(false),
  autoClose: z.boolean().default(false),
  confidenceThreshold: z.number().min(0).max(1).default(0.7),
  ignoreLabels: z.array(z.string()).default(['wontfix', 'invalid', 'duplicate']),
  ignoreAuthors: z.array(z.string()).default([]),
  priorityKeywords: PriorityKeywordsSchema.default({}),
});

const LabelsConfigSchema = z.object({
  prefix: z.string().default('contribhub'),
  useEmoji: z.boolean().default(true),
  categoryColors: z.record(z.string()).default({
    bug: 'd73a4a',
    feature: 'a2eeef',
    question: 'd876e3',
    docs: '0075ca',
    chore: 'e4e669',
    security: 'b60205',
    performance: 'fbca04',
  }),
  priorityColors: z.record(z.string()).default({
    P0: 'b60205',
    P1: 'd93f0b',
    P2: 'fbca04',
    P3: '0e8a16',
  }),
  complexityColors: z.record(z.string()).default({
    trivial: '0e8a16',
    easy: '1d76db',
    medium: 'fbca04',
    hard: 'd93f0b',
    expert: 'b60205',
  }),
});

const ResponsesConfigSchema = z.object({
  tone: z.enum(['formal', 'friendly', 'minimal']).default('friendly'),
  language: z.string().default('en'),
  includeLabels: z.boolean().default(true),
  includePriority: z.boolean().default(true),
  includeComplexity: z.boolean().default(true),
  customFooter: z.string().default(''),
});

const DuplicatesConfigSchema = z.object({
  enabled: z.boolean().default(true),
  similarityThreshold: z.number().min(0).max(1).default(0.85),
  searchScope: z.enum(['open', 'all']).default('open'),
  maxResults: z.number().min(1).max(10).default(3),
  commentOnDuplicate: z.boolean().default(true),
});

const NotificationsConfigSchema = z.object({
  slackWebhook: z.string().default(''),
  discordWebhook: z.string().default(''),
  notifyOnP0: z.boolean().default(true),
  notifyOnDuplicate: z.boolean().default(false),
});

const ContribHubConfigSchema = z.object({
  version: z.number().default(1),
  triage: TriageConfigSchema.default({}),
  labels: LabelsConfigSchema.default({}),
  responses: ResponsesConfigSchema.default({}),
  duplicates: DuplicatesConfigSchema.default({}),
  notifications: NotificationsConfigSchema.default({}),
});

/**
 * Load and parse the .contribhub.yml configuration from the repository.
 * Falls back to full defaults if the file is missing or unparseable.
 */
export async function loadConfig(configPath: string): Promise<ContribHubConfig> {
  const token = process.env.GITHUB_TOKEN ?? '';
  const octokit = github.getOctokit(token);
  const { owner, repo } = github.context.repo;

  let rawContent: string | null = null;

  try {
    const response = await octokit.rest.repos.getContent({
      owner,
      repo,
      path: configPath,
      ref: github.context.sha,
    });

    if ('content' in response.data && response.data.type === 'file') {
      rawContent = Buffer.from(response.data.content, 'base64').toString('utf-8');
      core.info(`Loaded config from ${configPath}`);
    }
  } catch (error: unknown) {
    const statusError = error as { status?: number };
    if (statusError.status === 404) {
      core.info(`Config file ${configPath} not found — using defaults`);
    } else {
      core.warning(`Failed to load config from ${configPath}: ${error}`);
    }
  }

  return parseConfig(rawContent);
}

/**
 * Parse raw YAML string into a validated ContribHubConfig.
 * Returns full defaults when input is null or empty.
 */
export function parseConfig(rawYaml: string | null): ContribHubConfig {
  if (!rawYaml || rawYaml.trim() === '') {
    core.info('Using default configuration');
    return ContribHubConfigSchema.parse({});
  }

  try {
    const parsed = YAML.parse(rawYaml);
    const validated = ContribHubConfigSchema.parse(parsed ?? {});
    core.info(`Config validated: version=${validated.version}, triage.enabled=${validated.triage.enabled}`);
    return validated;
  } catch (error) {
    if (error instanceof z.ZodError) {
      core.warning('Config validation errors:');
      for (const issue of error.issues) {
        core.warning(`  - ${issue.path.join('.')}: ${issue.message}`);
      }
      core.warning('Falling back to defaults for invalid fields');
    } else {
      core.warning(`Failed to parse YAML config: ${error}`);
    }
    return ContribHubConfigSchema.parse({});
  }
}

/**
 * Get the default configuration without loading from a file.
 */
export function getDefaultConfig(): ContribHubConfig {
  return ContribHubConfigSchema.parse({});
}
