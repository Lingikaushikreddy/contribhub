/**
 * Label management for ContribHub GitHub Action.
 *
 * Creates and applies labels via the GitHub API, ensuring they exist with
 * correct colors before assignment. Labels follow the format:
 *   {prefix}/{type}: {value}
 * e.g. "contribhub/category: bug", "contribhub/priority: P0"
 */

import * as core from '@actions/core';
import type { GitHub } from '@actions/github/lib/utils';
import type { ContribHubConfig, LabelRecommendation, TriageResult } from './types';

type OctokitClient = InstanceType<typeof GitHub>;

interface LabelDefinition {
  name: string;
  color: string;
  description: string;
}

const CATEGORY_EMOJI: Record<string, string> = {
  bug: '\uD83D\uDC1B',
  feature: '\u2728',
  question: '\u2753',
  docs: '\uD83D\uDCDA',
  chore: '\uD83E\uDDF9',
  security: '\uD83D\uDD12',
  performance: '\u26A1',
};

const PRIORITY_EMOJI: Record<string, string> = {
  P0: '\uD83D\uDD34',
  P1: '\uD83D\uDFE0',
  P2: '\uD83D\uDFE1',
  P3: '\uD83D\uDFE2',
};

const COMPLEXITY_EMOJI: Record<string, string> = {
  trivial: '\uD83C\uDFAF',
  easy: '\uD83D\uDFE2',
  medium: '\uD83D\uDFE1',
  hard: '\uD83D\uDFE0',
  expert: '\uD83D\uDD34',
};

/**
 * Build the full set of label definitions from triage results and config.
 */
export function buildLabelDefinitions(
  triageResult: TriageResult,
  config: ContribHubConfig
): LabelDefinition[] {
  const { prefix, useEmoji, categoryColors, priorityColors, complexityColors } = config.labels;
  const labels: LabelDefinition[] = [];

  const categoryEmoji = useEmoji ? `${CATEGORY_EMOJI[triageResult.category] ?? ''} ` : '';
  labels.push({
    name: `${prefix}/category: ${triageResult.category}`,
    color: categoryColors[triageResult.category] ?? 'ededed',
    description: `${categoryEmoji}Category: ${triageResult.category} (${Math.round(triageResult.confidence * 100)}% confidence)`,
  });

  const priorityEmoji = useEmoji ? `${PRIORITY_EMOJI[triageResult.priority] ?? ''} ` : '';
  labels.push({
    name: `${prefix}/priority: ${triageResult.priority}`,
    color: priorityColors[triageResult.priority] ?? 'ededed',
    description: `${priorityEmoji}Priority: ${triageResult.priority}`,
  });

  const complexityEmoji = useEmoji ? `${COMPLEXITY_EMOJI[triageResult.complexity] ?? ''} ` : '';
  labels.push({
    name: `${prefix}/complexity: ${triageResult.complexity}`,
    color: complexityColors[triageResult.complexity] ?? 'ededed',
    description: `${complexityEmoji}Complexity: ${triageResult.complexity}`,
  });

  for (const rec of triageResult.labels) {
    if (!labels.some(l => l.name === rec.name)) {
      labels.push({
        name: rec.name,
        color: rec.color,
        description: rec.description,
      });
    }
  }

  return labels;
}

/**
 * Ensure a label exists in the repository. Creates it if missing,
 * updates the color/description if they have drifted.
 */
async function ensureLabelExists(
  octokit: OctokitClient,
  owner: string,
  repo: string,
  label: LabelDefinition
): Promise<void> {
  try {
    const existing = await octokit.rest.issues.getLabel({
      owner,
      repo,
      name: label.name,
    });

    const needsUpdate =
      existing.data.color !== label.color ||
      existing.data.description !== label.description;

    if (needsUpdate) {
      await octokit.rest.issues.updateLabel({
        owner,
        repo,
        name: label.name,
        color: label.color,
        description: label.description,
      });
      core.debug(`Updated label: "${label.name}"`);
    }
  } catch (error: unknown) {
    const statusError = error as { status?: number };
    if (statusError.status === 404) {
      await octokit.rest.issues.createLabel({
        owner,
        repo,
        name: label.name,
        color: label.color,
        description: label.description,
      });
      core.info(`Created label: "${label.name}" (#${label.color})`);
    } else {
      throw error;
    }
  }
}

/**
 * Remove previously-applied ContribHub labels from an issue to prevent stale
 * labels from persisting after re-triage.
 */
async function removeStaleLabels(
  octokit: OctokitClient,
  owner: string,
  repo: string,
  issueNumber: number,
  prefix: string,
  newLabelNames: string[]
): Promise<void> {
  const { data: issueLabels } = await octokit.rest.issues.listLabelsOnIssue({
    owner,
    repo,
    issue_number: issueNumber,
  });

  const staleLabels = issueLabels
    .filter(l => l.name.startsWith(`${prefix}/`))
    .filter(l => !newLabelNames.includes(l.name));

  for (const label of staleLabels) {
    try {
      await octokit.rest.issues.removeLabel({
        owner,
        repo,
        issue_number: issueNumber,
        name: label.name,
      });
      core.info(`Removed stale label: "${label.name}"`);
    } catch (error: unknown) {
      const statusError = error as { status?: number };
      if (statusError.status !== 404) {
        core.warning(`Failed to remove label "${label.name}": ${error}`);
      }
    }
  }
}

/**
 * Apply triage labels to an issue. This is the main entry point that:
 * 1. Builds label definitions from triage results
 * 2. Ensures all labels exist in the repo
 * 3. Removes stale ContribHub labels
 * 4. Applies the new label set
 */
export async function applyLabels(
  octokit: OctokitClient,
  owner: string,
  repo: string,
  issueNumber: number,
  triageResult: TriageResult,
  config: ContribHubConfig
): Promise<string[]> {
  const labels = buildLabelDefinitions(triageResult, config);
  const labelNames = labels.map(l => l.name);

  core.info(`Applying ${labels.length} labels to ${owner}/${repo}#${issueNumber}`);

  const ensurePromises = labels.map(label =>
    ensureLabelExists(octokit, owner, repo, label)
  );
  await Promise.all(ensurePromises);

  await removeStaleLabels(octokit, owner, repo, issueNumber, config.labels.prefix, labelNames);

  await octokit.rest.issues.addLabels({
    owner,
    repo,
    issue_number: issueNumber,
    labels: labelNames,
  });

  core.info(`Successfully applied labels: ${labelNames.join(', ')}`);
  return labelNames;
}

/**
 * Build label definitions from raw API label recommendations.
 * Used when applying additional custom labels beyond the standard triage set.
 */
export function buildCustomLabels(
  recommendations: LabelRecommendation[],
  confidenceThreshold: number
): LabelDefinition[] {
  return recommendations
    .filter(rec => rec.confidence >= confidenceThreshold)
    .map(rec => ({
      name: rec.name,
      color: rec.color,
      description: rec.description,
    }));
}
