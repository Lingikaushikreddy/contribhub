/**
 * Comment generation and posting for ContribHub GitHub Action.
 *
 * Creates professional GitHub markdown comments for:
 * - Duplicate issue detection with similarity scores
 * - Issue quality improvement suggestions
 * - Triage summary annotations
 */

import * as core from '@actions/core';
import type { GitHub } from '@actions/github/lib/utils';
import type { ContribHubConfig, DuplicateMatch, DuplicateResult, TriageResult } from './types';

type OctokitClient = InstanceType<typeof GitHub>;

const CONTRIBHUB_MARKER = '<!-- contribhub-bot -->';

/**
 * Build a markdown comment body for duplicate detection results.
 */
export function buildDuplicateComment(duplicateResult: DuplicateResult): string {
  if (!duplicateResult.hasDuplicates || duplicateResult.duplicates.length === 0) {
    return '';
  }

  const lines: string[] = [
    CONTRIBHUB_MARKER,
    '',
    '### Possible Duplicate Issues',
    '',
    'ContribHub detected similar issues that may be related:',
    '',
    '| Issue | Similarity | Status |',
    '| --- | --- | --- |',
  ];

  for (const dup of duplicateResult.duplicates) {
    const similarityPct = Math.round(dup.similarity * 100);
    const statusBadge = dup.state === 'open' ? 'Open' : 'Closed';
    const similarityBar = buildSimilarityBar(dup.similarity);
    lines.push(
      `| [#${dup.issueNumber} — ${escapeMarkdown(dup.issueTitle)}](${dup.htmlUrl}) | ${similarityBar} ${similarityPct}% | ${statusBadge} |`
    );
  }

  lines.push(
    '',
    '<details>',
    '<summary>What does this mean?</summary>',
    '',
    'ContribHub uses semantic analysis to detect issues that discuss similar topics.',
    'A high similarity score means the issues may be addressing the same problem.',
    '',
    '- **90%+** — Very likely a duplicate',
    '- **80-90%** — Probably related, worth checking',
    '- **70-80%** — Possibly related',
    '',
    'If this is indeed a duplicate, a maintainer can close it with a reference to the original issue.',
    '',
    '</details>',
    '',
    buildFooter(),
  );

  return lines.join('\n');
}

/**
 * Build a markdown comment for low-quality issues with improvement suggestions.
 */
export function buildQualitySuggestionsComment(
  triageResult: TriageResult,
  config: ContribHubConfig
): string {
  if (triageResult.qualityScore >= 40 || triageResult.qualitySuggestions.length === 0) {
    return '';
  }

  const toneGreeting = getToneGreeting(config.responses.tone);

  const lines: string[] = [
    CONTRIBHUB_MARKER,
    '',
    '### Issue Quality Suggestions',
    '',
    toneGreeting,
    '',
    'To help maintainers address this issue more effectively, consider adding the following:',
    '',
  ];

  for (const suggestion of triageResult.qualitySuggestions) {
    lines.push(`- [ ] ${suggestion}`);
  }

  lines.push(
    '',
    `> **Quality score:** ${triageResult.qualityScore}/100 — Adding the above information will help us prioritize and resolve this faster.`,
    '',
  );

  if (config.responses.customFooter) {
    lines.push(config.responses.customFooter, '');
  }

  lines.push(buildFooter());

  return lines.join('\n');
}

/**
 * Post a comment on a GitHub issue. If a previous ContribHub comment exists
 * for the same type, it is updated instead of creating a new one.
 */
export async function postComment(
  octokit: OctokitClient,
  owner: string,
  repo: string,
  issueNumber: number,
  body: string
): Promise<void> {
  if (!body || body.trim() === '') {
    core.debug('Empty comment body — skipping');
    return;
  }

  const existingCommentId = await findExistingComment(octokit, owner, repo, issueNumber);

  if (existingCommentId) {
    await octokit.rest.issues.updateComment({
      owner,
      repo,
      comment_id: existingCommentId,
      body,
    });
    core.info(`Updated existing comment on ${owner}/${repo}#${issueNumber}`);
  } else {
    await octokit.rest.issues.createComment({
      owner,
      repo,
      issue_number: issueNumber,
      body,
    });
    core.info(`Posted new comment on ${owner}/${repo}#${issueNumber}`);
  }
}

/**
 * Post a duplicate detection comment if duplicates are found.
 */
export async function postDuplicateComment(
  octokit: OctokitClient,
  owner: string,
  repo: string,
  issueNumber: number,
  duplicateResult: DuplicateResult,
  config: ContribHubConfig
): Promise<void> {
  if (!config.duplicates.commentOnDuplicate) {
    core.info('Duplicate commenting is disabled in config — skipping');
    return;
  }

  const body = buildDuplicateComment(duplicateResult);
  if (body) {
    await postComment(octokit, owner, repo, issueNumber, body);
  }
}

/**
 * Post quality suggestions if the issue quality score is below threshold.
 */
export async function postQualitySuggestionsComment(
  octokit: OctokitClient,
  owner: string,
  repo: string,
  issueNumber: number,
  triageResult: TriageResult,
  config: ContribHubConfig
): Promise<void> {
  const body = buildQualitySuggestionsComment(triageResult, config);
  if (body) {
    await postComment(octokit, owner, repo, issueNumber, body);
  }
}

/**
 * Look for an existing ContribHub comment on the issue to update.
 */
async function findExistingComment(
  octokit: OctokitClient,
  owner: string,
  repo: string,
  issueNumber: number
): Promise<number | null> {
  try {
    const comments = await octokit.rest.issues.listComments({
      owner,
      repo,
      issue_number: issueNumber,
      per_page: 100,
    });

    const contribhubComment = comments.data.find(
      comment => comment.body?.includes(CONTRIBHUB_MARKER)
    );

    return contribhubComment?.id ?? null;
  } catch (error) {
    core.debug(`Failed to list comments: ${error}`);
    return null;
  }
}

function buildSimilarityBar(similarity: number): string {
  const filled = Math.round(similarity * 5);
  const empty = 5 - filled;
  return '\u2588'.repeat(filled) + '\u2591'.repeat(empty);
}

function escapeMarkdown(text: string): string {
  return text
    .replace(/\|/g, '\\|')
    .replace(/\[/g, '\\[')
    .replace(/\]/g, '\\]')
    .substring(0, 80);
}

function getToneGreeting(tone: 'formal' | 'friendly' | 'minimal'): string {
  switch (tone) {
    case 'formal':
      return 'Thank you for reporting this issue. We have a few suggestions to help us process it more efficiently.';
    case 'friendly':
      return 'Thanks for opening this issue! We have a few suggestions that would help us look into this faster.';
    case 'minimal':
      return 'The following information would help resolve this issue:';
  }
}

function buildFooter(): string {
  return '*Automated by [ContribHub](https://contribhub.dev) — AI-powered issue triage*';
}
