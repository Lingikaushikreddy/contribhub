"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Star, GitFork, ExternalLink, AlertCircle } from "lucide-react";
import { Card, CardHeader, CardBody } from "../../../components/ui/Card";
import { Badge, CategoryBadge, PriorityBadge } from "../../../components/ui/Badge";
import { Tabs } from "../../../components/ui/Tabs";
import { Button } from "../../../components/ui/Button";
import { TriageEventCard } from "../../../components/features/TriageEventCard";
import { DifficultyBar } from "../../../components/features/DifficultyBar";
import { HealthScoreRadar } from "../../../components/charts/HealthScoreRadar";
import { mockRepos, mockIssues, mockTriageStats, mockTriageConfig } from "@/lib/mock-data";
import type { IssueComplexity } from "@/lib/types";
import clsx from "clsx";

const COMPLEXITY_LEVEL: Record<IssueComplexity, number> = {
  trivial: 1,
  easy: 2,
  medium: 3,
  hard: 4,
  expert: 5,
};

const LANGUAGE_COLORS: Record<string, string> = {
  TypeScript: "#3178c6",
  JavaScript: "#f1e05a",
  Python: "#3572A5",
  Go: "#00ADD8",
  Rust: "#dea584",
  Java: "#b07219",
  Ruby: "#701516",
  HCL: "#844fba",
  MDX: "#fcb32c",
};

export default function RepoDetailPage() {
  const params = useParams();
  const repoId = params.id as string;
  const repo = mockRepos.find((r) => r.id === repoId) || mockRepos[0];
  const repoIssues = mockIssues.filter((i) => i.repoId === repo.id);
  const repoEvents = mockTriageStats.recentEvents.filter(
    (e) => e.repoName === repo.fullName
  );

  // Config form state
  const [tone, setTone] = useState<string>(mockTriageConfig.responseTone);
  const [threshold, setThreshold] = useState(mockTriageConfig.autoApproveThreshold);
  const [excludedLabels, setExcludedLabels] = useState("wontfix, invalid");

  function getScoreColor(score: number): string {
    if (score >= 85) return "text-emerald-400";
    if (score >= 70) return "text-yellow-400";
    if (score >= 50) return "text-orange-400";
    return "text-red-400";
  }

  const tabs = [
    { id: "issues", label: "Issues", count: repoIssues.length },
    { id: "triage", label: "Triage Events", count: repoEvents.length },
    { id: "config", label: "Config" },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Repo Header */}
      <div className="flex flex-col lg:flex-row lg:items-start gap-6">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-zinc-100 tracking-tight truncate">
              {repo.fullName}
            </h1>
            <a
              href={`https://github.com/${repo.fullName}`}
              target="_blank"
              rel="noopener noreferrer"
              className="shrink-0 p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
          <p className="text-sm text-zinc-400 mb-4">{repo.description}</p>

          <div className="flex flex-wrap items-center gap-3">
            <Badge color="indigo">
              <Star className="w-3 h-3 mr-1" />
              {repo.stars.toLocaleString()}
            </Badge>
            <Badge color="zinc">
              <GitFork className="w-3 h-3 mr-1" />
              {repo.forks.toLocaleString()}
            </Badge>
            <div className="flex items-center gap-1.5">
              <span
                className="w-3 h-3 rounded-full"
                style={{
                  backgroundColor:
                    LANGUAGE_COLORS[repo.language] || "#71717a",
                }}
              />
              <span className="text-xs text-zinc-300">{repo.language}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5 text-zinc-500" />
              <span className="text-xs text-zinc-400">
                {repo.issuesThisWeek} issues this week
              </span>
            </div>
          </div>
        </div>

        {/* Health Score Breakdown */}
        <Card className="lg:w-[340px] shrink-0">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-zinc-300">
              Health Score
            </h3>
            <span
              className={clsx(
                "text-2xl font-bold",
                getScoreColor(repo.healthScore)
              )}
            >
              {repo.healthScore}
            </span>
          </div>
          <HealthScoreRadar data={repo.healthBreakdown} />
        </Card>
      </div>

      {/* Tabs */}
      <Tabs tabs={tabs} defaultTab="issues">
        {(activeTab) => (
          <>
            {/* Issues Tab */}
            {activeTab === "issues" && (
              <div className="overflow-x-auto">
                {repoIssues.length > 0 ? (
                  <table className="w-full text-left">
                    <thead>
                      <tr className="border-b border-zinc-800">
                        <th className="pb-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">
                          Title
                        </th>
                        <th className="pb-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">
                          Category
                        </th>
                        <th className="pb-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">
                          Priority
                        </th>
                        <th className="pb-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">
                          Complexity
                        </th>
                        <th className="pb-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">
                          State
                        </th>
                        <th className="pb-3 text-xs font-medium text-zinc-500 uppercase tracking-wider text-right">
                          Created
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/50">
                      {repoIssues.map((issue) => (
                        <tr
                          key={issue.id}
                          className="hover:bg-zinc-800/30 transition-colors"
                        >
                          <td className="py-3 pr-4">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-mono text-zinc-500">
                                #{issue.number}
                              </span>
                              <span className="text-sm text-zinc-200 truncate max-w-[280px]">
                                {issue.title}
                              </span>
                            </div>
                          </td>
                          <td className="py-3 pr-4">
                            <CategoryBadge category={issue.category} />
                          </td>
                          <td className="py-3 pr-4">
                            <PriorityBadge priority={issue.priority} />
                          </td>
                          <td className="py-3 pr-4">
                            <DifficultyBar
                              level={COMPLEXITY_LEVEL[issue.complexity]}
                              showLabel
                            />
                          </td>
                          <td className="py-3 pr-4">
                            <span
                              className={clsx(
                                "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
                                issue.state === "open"
                                  ? "bg-emerald-500/15 text-emerald-400"
                                  : issue.state === "triaged"
                                    ? "bg-blue-500/15 text-blue-400"
                                    : issue.state === "in_progress"
                                      ? "bg-amber-500/15 text-amber-400"
                                      : "bg-zinc-500/15 text-zinc-400"
                              )}
                            >
                              {issue.state}
                            </span>
                          </td>
                          <td className="py-3 text-right">
                            <span className="text-xs text-zinc-500">
                              {new Date(issue.createdAt).toLocaleDateString(
                                "en-US",
                                {
                                  month: "short",
                                  day: "numeric",
                                }
                              )}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="flex flex-col items-center justify-center py-16 text-center">
                    <p className="text-sm text-zinc-400">
                      No issues found for this repository.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Triage Events Tab */}
            {activeTab === "triage" && (
              <div className="space-y-3">
                {repoEvents.length > 0 ? (
                  repoEvents.map((event) => (
                    <TriageEventCard key={event.id} event={event} />
                  ))
                ) : (
                  <div className="flex flex-col items-center justify-center py-16 text-center">
                    <p className="text-sm text-zinc-400">
                      No triage events yet for this repository.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Config Tab */}
            {activeTab === "config" && (
              <div className="max-w-xl space-y-6">
                {/* Response Tone */}
                <div>
                  <label className="block text-sm font-medium text-zinc-300 mb-2">
                    Response Tone
                  </label>
                  <div className="flex gap-2">
                    {(["formal", "friendly", "minimal"] as const).map((t) => (
                      <button
                        key={t}
                        onClick={() => setTone(t)}
                        className={clsx(
                          "px-4 py-2 rounded-lg text-sm font-medium border transition-colors capitalize",
                          tone === t
                            ? "border-indigo-500 bg-indigo-500/15 text-indigo-400"
                            : "border-zinc-700 bg-zinc-800 text-zinc-400 hover:border-zinc-600"
                        )}
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                  <p className="mt-1.5 text-xs text-zinc-500">
                    Controls the tone of AI-generated responses to issues.
                  </p>
                </div>

                {/* Confidence Threshold Slider */}
                <div>
                  <label className="block text-sm font-medium text-zinc-300 mb-2">
                    Auto-Approve Confidence Threshold
                  </label>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min="50"
                      max="100"
                      step="1"
                      value={threshold}
                      onChange={(e) =>
                        setThreshold(Number(e.target.value))
                      }
                      className="flex-1 h-2 bg-zinc-700 rounded-full appearance-none cursor-pointer accent-indigo-500"
                    />
                    <span className="text-sm font-mono font-semibold text-zinc-200 w-12 text-right">
                      {threshold}%
                    </span>
                  </div>
                  <p className="mt-1.5 text-xs text-zinc-500">
                    Triage events above this confidence threshold will be
                    auto-approved without manual review.
                  </p>
                </div>

                {/* Excluded Labels */}
                <div>
                  <label className="block text-sm font-medium text-zinc-300 mb-2">
                    Excluded Labels
                  </label>
                  <input
                    type="text"
                    value={excludedLabels}
                    onChange={(e) => setExcludedLabels(e.target.value)}
                    className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 focus:ring-offset-zinc-950 hover:border-zinc-600 transition-colors"
                    placeholder="e.g., wontfix, invalid, duplicate"
                  />
                  <p className="mt-1.5 text-xs text-zinc-500">
                    Comma-separated labels that should be excluded from
                    automatic triage.
                  </p>
                </div>

                {/* Feature Toggles */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-zinc-300 mb-1">
                    Feature Toggles
                  </label>
                  {[
                    {
                      id: "duplicate",
                      label: "Duplicate Detection",
                      desc: "Automatically detect and flag duplicate issues",
                      checked: mockTriageConfig.enableDuplicateDetection,
                    },
                    {
                      id: "autoLabel",
                      label: "Auto Labeling",
                      desc: "Automatically apply labels to incoming issues",
                      checked: mockTriageConfig.enableAutoLabeling,
                    },
                    {
                      id: "autoRespond",
                      label: "Auto Response",
                      desc: "Post AI-drafted responses when confidence is high",
                      checked: mockTriageConfig.enableAutoResponse,
                    },
                  ].map((toggle) => (
                    <label
                      key={toggle.id}
                      className="flex items-center justify-between p-3 rounded-lg border border-zinc-800 bg-zinc-800/30 hover:bg-zinc-800/60 transition-colors cursor-pointer"
                    >
                      <div>
                        <p className="text-sm font-medium text-zinc-200">
                          {toggle.label}
                        </p>
                        <p className="text-xs text-zinc-500 mt-0.5">
                          {toggle.desc}
                        </p>
                      </div>
                      <input
                        type="checkbox"
                        defaultChecked={toggle.checked}
                        className="w-4 h-4 rounded border-zinc-600 bg-zinc-800 text-indigo-500 focus:ring-indigo-500 focus:ring-offset-zinc-950 cursor-pointer"
                      />
                    </label>
                  ))}
                </div>

                {/* Save Button */}
                <div className="pt-2">
                  <Button variant="primary">Save Configuration</Button>
                </div>
              </div>
            )}
          </>
        )}
      </Tabs>
    </div>
  );
}
