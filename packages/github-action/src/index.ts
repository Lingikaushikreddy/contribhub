/**
 * ContribHub GitHub Action — Main Entry Point
 *
 * Handles issue triage when triggered by issues.opened or issues.edited events.
 *
 * Flow:
 * 1. Parse the GitHub event payload
 * 2. Load and validate .contribhub.yml config from the repo
 * 3. Call ContribHub API for AI triage (category, priority, complexity)
 * 4. Check for duplicate issues
 * 5. Apply labels to the issue via GitHub API
 * 6. Post comments for duplicates and quality suggestions
 * 7. Report the triage event back to ContribHub for analytics
 */

import * as core from '@actions/core';
import * as github from '@actions/github';
import { ContribHubApiClient } from './api-client';
import { postDuplicateComment, postQualitySuggestionsComment } from './comments';
import { loadConfig } from './config';
import { applyLabels } from './labels';
import type { ActionInputs, IssuePayload } from './types';

async function run(): Promise<void> {
  const startTime = Date.now();

  try {
    const inputs = getInputs();
    const context = github.context;

    if (!isSupportedEvent(context)) {
      core.info(
        `Unsupported event: ${context.eventName}.${context.payload.action ?? 'unknown'} — ` +
        'ContribHub Triage only runs on issues.opened and issues.edited'
      );
      return;
    }

    const issue = context.payload.issue;
    if (!issue) {
      core.setFailed('No issue found in event payload');
      return;
    }

    const { owner, repo } = context.repo;

    const config = await loadConfig(inputs.configPath);

    if (!config.triage.enabled) {
      core.info('Triage is disabled in config — exiting');
      return;
    }

    if (shouldSkipIssue(issue, config)) {
      core.info('Issue matches skip criteria — exiting');
      return;
    }

    const issuePayload: IssuePayload = {
      owner,
      repo,
      issueNumber: issue.number,
      title: issue.title,
      body: issue.body ?? '',
      author: issue.user?.login ?? 'unknown',
      labels: (issue.labels ?? []).map((l: { name: string }) => l.name),
      createdAt: issue.created_at,
      updatedAt: issue.updated_at,
      htmlUrl: issue.html_url,
    };

    const apiClient = new ContribHubApiClient(inputs.apiBaseUrl, inputs.apiKey);
    const octokit = github.getOctokit(process.env.GITHUB_TOKEN ?? '');

    core.startGroup('AI Triage');
    const triageResult = await apiClient.triageIssue(issuePayload);
    core.endGroup();

    core.startGroup('Duplicate Detection');
    let duplicateResult = null;
    if (config.duplicates.enabled) {
      duplicateResult = await apiClient.checkDuplicates(issuePayload);
    } else {
      core.info('Duplicate detection is disabled in config');
    }
    core.endGroup();

    if (inputs.dryRun) {
      core.info('--- DRY RUN MODE ---');
      core.info(`Would apply labels: ${JSON.stringify(triageResult.labels.map(l => l.name))}`);
      core.info(`Category: ${triageResult.category}, Priority: ${triageResult.priority}, Complexity: ${triageResult.complexity}`);
      if (duplicateResult?.hasDuplicates) {
        core.info(`Would post duplicate comment for ${duplicateResult.duplicates.length} match(es)`);
      }
      if (triageResult.qualityScore < 40) {
        core.info(`Would post quality suggestions (score: ${triageResult.qualityScore})`);
      }
      setOutputs(triageResult, duplicateResult, [], startTime);
      return;
    }

    core.startGroup('Apply Labels');
    let appliedLabels: string[] = [];
    if (config.triage.autoLabel && triageResult.confidence >= config.triage.confidenceThreshold) {
      appliedLabels = await applyLabels(octokit, owner, repo, issue.number, triageResult, config);
    } else if (triageResult.confidence < config.triage.confidenceThreshold) {
      core.info(
        `Confidence ${triageResult.confidence.toFixed(2)} is below threshold ` +
        `${config.triage.confidenceThreshold} — skipping auto-label`
      );
    } else {
      core.info('Auto-labeling is disabled in config');
    }
    core.endGroup();

    core.startGroup('Post Comments');
    if (duplicateResult?.hasDuplicates) {
      await postDuplicateComment(octokit, owner, repo, issue.number, duplicateResult, config);
    }

    if (triageResult.qualityScore < 40) {
      await postQualitySuggestionsComment(octokit, owner, repo, issue.number, triageResult, config);
    }
    core.endGroup();

    core.startGroup('Report Event');
    const processingTimeMs = Date.now() - startTime;
    await apiClient.reportEvent({
      repoFullName: `${owner}/${repo}`,
      issueNumber: issue.number,
      eventType: context.payload.action === 'opened' ? 'issue_opened' : 'issue_edited',
      labelsApplied: appliedLabels,
      duplicatesFound: duplicateResult?.duplicates.length ?? 0,
      confidence: triageResult.confidence,
      processingTimeMs,
    });
    core.endGroup();

    setOutputs(triageResult, duplicateResult, appliedLabels, startTime);

    core.info(
      `Triage complete for ${owner}/${repo}#${issue.number} in ${Date.now() - startTime}ms`
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    core.setFailed(`ContribHub Triage failed: ${message}`);
  }
}

function getInputs(): ActionInputs {
  return {
    apiKey: core.getInput('contribhub_api_key', { required: true }),
    configPath: core.getInput('config_path') || '.contribhub.yml',
    apiBaseUrl: core.getInput('api_base_url') || 'https://api.contribhub.dev',
    dryRun: core.getInput('dry_run') === 'true',
  };
}

function isSupportedEvent(context: typeof github.context): boolean {
  if (context.eventName !== 'issues') {
    return false;
  }
  const action = context.payload.action;
  return action === 'opened' || action === 'edited';
}

function shouldSkipIssue(
  issue: { labels?: Array<{ name: string }>; user?: { login: string } },
  config: { triage: { ignoreLabels: string[]; ignoreAuthors: string[] } }
): boolean {
  const issueLabels = (issue.labels ?? []).map(l => l.name);
  const hasIgnoredLabel = issueLabels.some(label =>
    config.triage.ignoreLabels.includes(label)
  );
  if (hasIgnoredLabel) {
    core.info(`Skipping: issue has an ignored label (${issueLabels.join(', ')})`);
    return true;
  }

  const author = issue.user?.login ?? '';
  if (config.triage.ignoreAuthors.includes(author)) {
    core.info(`Skipping: author "${author}" is in the ignore list`);
    return true;
  }

  if (author.endsWith('[bot]')) {
    core.info(`Skipping: author "${author}" is a bot`);
    return true;
  }

  return false;
}

function setOutputs(
  triageResult: { category: string; priority: string; complexity: string; confidence: number; qualityScore: number; responseDraftId: string | null },
  duplicateResult: { hasDuplicates: boolean; duplicates: Array<{ issueNumber: number }> } | null,
  appliedLabels: string[],
  startTime: number
): void {
  core.setOutput('category', triageResult.category);
  core.setOutput('priority', triageResult.priority);
  core.setOutput('complexity', triageResult.complexity);
  core.setOutput('confidence', triageResult.confidence.toString());
  core.setOutput('quality_score', triageResult.qualityScore.toString());
  core.setOutput('labels_applied', JSON.stringify(appliedLabels));
  core.setOutput('has_duplicates', (duplicateResult?.hasDuplicates ?? false).toString());
  core.setOutput('duplicate_count', (duplicateResult?.duplicates.length ?? 0).toString());
  core.setOutput('response_draft_id', triageResult.responseDraftId ?? '');
  core.setOutput('processing_time_ms', (Date.now() - startTime).toString());
}

run();
