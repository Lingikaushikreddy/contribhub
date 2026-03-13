/**
 * GitHub webhook event types for ContribHub.
 * Covers the subset of webhook events that ContribHub processes.
 */

export type WebhookEvent = IssueEvent | PullRequestEvent | PushEvent | InstallationEvent;

export interface WebhookEventBase {
  action: string;
  sender: WebhookUser;
  repository: WebhookRepository;
  installation: { id: number } | null;
}

export interface WebhookUser {
  id: number;
  login: string;
  avatar_url: string;
  type: 'User' | 'Bot' | 'Organization';
}

export interface WebhookRepository {
  id: number;
  name: string;
  full_name: string;
  owner: WebhookUser;
  private: boolean;
  html_url: string;
  description: string | null;
  language: string | null;
  default_branch: string;
}

export interface IssueEvent extends WebhookEventBase {
  action:
    | 'opened'
    | 'edited'
    | 'deleted'
    | 'closed'
    | 'reopened'
    | 'assigned'
    | 'unassigned'
    | 'labeled'
    | 'unlabeled'
    | 'transferred';
  issue: WebhookIssue;
  label?: WebhookLabel;
  assignee?: WebhookUser;
}

export interface WebhookIssue {
  id: number;
  number: number;
  title: string;
  body: string | null;
  user: WebhookUser;
  labels: WebhookLabel[];
  state: 'open' | 'closed';
  assignees: WebhookUser[];
  comments: number;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
  html_url: string;
}

export interface WebhookLabel {
  id: number;
  name: string;
  color: string;
  description: string | null;
}

export interface PullRequestEvent extends WebhookEventBase {
  action:
    | 'opened'
    | 'edited'
    | 'closed'
    | 'reopened'
    | 'synchronize'
    | 'assigned'
    | 'review_requested'
    | 'merged';
  pull_request: WebhookPullRequest;
}

export interface WebhookPullRequest {
  id: number;
  number: number;
  title: string;
  body: string | null;
  user: WebhookUser;
  state: 'open' | 'closed';
  merged: boolean;
  merged_at: string | null;
  head: WebhookBranch;
  base: WebhookBranch;
  additions: number;
  deletions: number;
  changed_files: number;
  created_at: string;
  updated_at: string;
  html_url: string;
}

export interface WebhookBranch {
  ref: string;
  sha: string;
  repo: WebhookRepository;
}

export interface PushEvent extends WebhookEventBase {
  action: 'push';
  ref: string;
  before: string;
  after: string;
  commits: WebhookCommit[];
  head_commit: WebhookCommit | null;
  forced: boolean;
}

export interface WebhookCommit {
  id: string;
  message: string;
  author: { name: string; email: string; username: string };
  timestamp: string;
  added: string[];
  removed: string[];
  modified: string[];
}

export interface InstallationEvent {
  action: 'created' | 'deleted' | 'suspend' | 'unsuspend' | 'new_permissions_accepted';
  installation: {
    id: number;
    account: WebhookUser;
    app_id: number;
    target_type: 'User' | 'Organization';
    permissions: Record<string, string>;
    events: string[];
  };
  repositories?: Array<{ id: number; name: string; full_name: string; private: boolean }>;
  sender: WebhookUser;
}
