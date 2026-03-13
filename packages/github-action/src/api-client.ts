/**
 * Typed HTTP client for the ContribHub API.
 *
 * Handles authentication, request construction, retries with exponential
 * backoff, and typed response parsing for all triage-related endpoints.
 */

import * as core from '@actions/core';
import type {
  DuplicateResult,
  EventReport,
  IssuePayload,
  TriageResult,
} from './types';

const MAX_RETRIES = 3;
const INITIAL_BACKOFF_MS = 1000;
const REQUEST_TIMEOUT_MS = 30_000;

interface ApiError {
  status: number;
  message: string;
  detail?: string;
}

export class ContribHubApiClient {
  private readonly baseUrl: string;
  private readonly apiKey: string;
  private readonly headers: Record<string, string>;

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this.apiKey = apiKey;
    this.headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.apiKey}`,
      'User-Agent': 'ContribHub-GitHubAction/1.0',
      'X-ContribHub-Source': 'github-action',
    };
  }

  /**
   * Send an issue to the ContribHub API for AI-powered triage.
   * Returns category, priority, complexity, labels, and a quality score.
   */
  async triageIssue(issue: IssuePayload): Promise<TriageResult> {
    core.info(`Triaging issue #${issue.issueNumber}: "${issue.title}"`);

    const response = await this.request<TriageResult>('POST', '/v1/triage', {
      owner: issue.owner,
      repo: issue.repo,
      issue_number: issue.issueNumber,
      title: issue.title,
      body: issue.body,
      author: issue.author,
      labels: issue.labels,
      created_at: issue.createdAt,
      updated_at: issue.updatedAt,
      html_url: issue.htmlUrl,
    });

    core.info(
      `Triage result: category=${response.category}, priority=${response.priority}, ` +
      `complexity=${response.complexity}, confidence=${response.confidence.toFixed(2)}, ` +
      `quality_score=${response.qualityScore}`
    );

    return response;
  }

  /**
   * Check for duplicate issues in the repository.
   * Returns a list of potential duplicates with similarity scores.
   */
  async checkDuplicates(issue: IssuePayload): Promise<DuplicateResult> {
    core.info(`Checking duplicates for issue #${issue.issueNumber}`);

    const response = await this.request<DuplicateResult>('POST', '/v1/duplicates/check', {
      owner: issue.owner,
      repo: issue.repo,
      issue_number: issue.issueNumber,
      title: issue.title,
      body: issue.body,
    });

    if (response.hasDuplicates) {
      core.info(
        `Found ${response.duplicates.length} potential duplicate(s) — ` +
        `highest similarity: ${(response.duplicates[0]?.similarity ?? 0).toFixed(2)}`
      );
    } else {
      core.info('No duplicates found');
    }

    return response;
  }

  /**
   * Report a triage event back to ContribHub for analytics and audit logging.
   */
  async reportEvent(event: EventReport): Promise<void> {
    core.info(`Reporting triage event for ${event.repoFullName}#${event.issueNumber}`);

    await this.request<void>('POST', '/v1/events/triage', {
      repo_full_name: event.repoFullName,
      issue_number: event.issueNumber,
      event_type: event.eventType,
      labels_applied: event.labelsApplied,
      duplicates_found: event.duplicatesFound,
      confidence: event.confidence,
      processing_time_ms: event.processingTimeMs,
    });

    core.info('Triage event reported successfully');
  }

  /**
   * Execute an HTTP request with retries, timeout, and error handling.
   */
  private async request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
      if (attempt > 0) {
        const backoffMs = INITIAL_BACKOFF_MS * Math.pow(2, attempt - 1);
        core.info(`Retrying request (attempt ${attempt + 1}/${MAX_RETRIES}) after ${backoffMs}ms`);
        await this.sleep(backoffMs);
      }

      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

        const response = await fetch(url, {
          method,
          headers: this.headers,
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          if (response.status === 204) {
            return undefined as T;
          }
          return (await response.json()) as T;
        }

        const errorBody = await this.safeParseErrorBody(response);

        if (response.status === 429) {
          const retryAfter = response.headers.get('Retry-After');
          const waitMs = retryAfter ? parseInt(retryAfter, 10) * 1000 : INITIAL_BACKOFF_MS * Math.pow(2, attempt);
          core.warning(`Rate limited — waiting ${waitMs}ms before retry`);
          await this.sleep(waitMs);
          continue;
        }

        if (response.status >= 500) {
          lastError = new Error(
            `API server error: ${response.status} ${response.statusText} — ${errorBody.message}`
          );
          continue;
        }

        throw new Error(
          `API request failed: ${response.status} ${response.statusText} — ${errorBody.message}` +
          (errorBody.detail ? ` (${errorBody.detail})` : '')
        );
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          lastError = new Error(`Request to ${url} timed out after ${REQUEST_TIMEOUT_MS}ms`);
          continue;
        }
        if (error instanceof Error && (error.message.startsWith('API request failed') || error.message.startsWith('API server error'))) {
          lastError = error;
          if (error.message.startsWith('API request failed')) {
            throw error;
          }
          continue;
        }
        lastError = error instanceof Error ? error : new Error(String(error));
        continue;
      }
    }

    throw lastError ?? new Error(`Request to ${url} failed after ${MAX_RETRIES} attempts`);
  }

  private async safeParseErrorBody(response: Response): Promise<ApiError> {
    try {
      const body = await response.json();
      return {
        status: response.status,
        message: body.message ?? body.error ?? response.statusText,
        detail: body.detail,
      };
    } catch {
      return {
        status: response.status,
        message: response.statusText,
      };
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
