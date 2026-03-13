"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Check, Pencil, X, ExternalLink, User, Calendar, Tag } from "lucide-react";
import { Button } from "../../../components/ui/Button";
import { Badge, CategoryBadge, PriorityBadge } from "../../../components/ui/Badge";
import { Card } from "../../../components/ui/Card";
import { mockTriageStats, mockIssues } from "@/lib/mock-data";
import clsx from "clsx";
import Link from "next/link";

export default function TriageDetailPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.eventId as string;

  const event = mockTriageStats.recentEvents.find((e) => e.id === eventId) ||
    mockTriageStats.recentEvents[0];
  const issue = mockIssues.find((i) => i.id === event.issueId) || mockIssues[0];

  const [draftResponse, setDraftResponse] = useState(event.draftResponse);
  const [isEditing, setIsEditing] = useState(false);
  const [actionTaken, setActionTaken] = useState<string | null>(null);

  const handleApprove = () => {
    setActionTaken("approved");
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleDiscard = () => {
    setActionTaken("discarded");
  };

  return (
    <div className="p-6 space-y-6">
      {/* Back navigation */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.back()}
          className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-zinc-100 tracking-tight">
            Triage Review
          </h1>
          <p className="text-xs text-zinc-500 font-mono">
            {event.repoName} #{event.issueNumber}
          </p>
        </div>
      </div>

      {/* Action taken banner */}
      {actionTaken && (
        <div
          className={clsx(
            "rounded-xl border p-4 flex items-center gap-3",
            actionTaken === "approved"
              ? "border-emerald-500/30 bg-emerald-500/10"
              : "border-red-500/30 bg-red-500/10"
          )}
        >
          <div
            className={clsx(
              "w-8 h-8 rounded-full flex items-center justify-center",
              actionTaken === "approved"
                ? "bg-emerald-500/20"
                : "bg-red-500/20"
            )}
          >
            {actionTaken === "approved" ? (
              <Check className="w-4 h-4 text-emerald-400" />
            ) : (
              <X className="w-4 h-4 text-red-400" />
            )}
          </div>
          <div>
            <p
              className={clsx(
                "text-sm font-medium",
                actionTaken === "approved"
                  ? "text-emerald-400"
                  : "text-red-400"
              )}
            >
              {actionTaken === "approved"
                ? "Response approved and posted"
                : "Response discarded"}
            </p>
            <p className="text-xs text-zinc-500 mt-0.5">
              The triage action has been recorded.
            </p>
          </div>
        </div>
      )}

      {/* Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel: Original Issue */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-zinc-100">
              Original Issue
            </h2>
            <a
              href={issue.htmlUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-zinc-400 hover:text-indigo-400 transition-colors"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              View on GitHub
            </a>
          </div>

          <h3 className="text-lg font-semibold text-zinc-100 mb-3">
            {issue.title}
          </h3>

          {/* Issue Meta */}
          <div className="flex flex-wrap items-center gap-3 mb-4 text-xs text-zinc-400">
            <div className="flex items-center gap-1.5">
              <User className="w-3.5 h-3.5" />
              <a
                href={issue.author.htmlUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-indigo-400 transition-colors"
              >
                {issue.author.login}
              </a>
            </div>
            <div className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5" />
              {new Date(issue.createdAt).toLocaleDateString("en-US", {
                month: "long",
                day: "numeric",
                year: "numeric",
              })}
            </div>
          </div>

          {/* Labels */}
          <div className="flex flex-wrap gap-1.5 mb-4">
            {issue.labels.map((label) => (
              <div
                key={label}
                className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-zinc-800 border border-zinc-700 text-xs text-zinc-300"
              >
                <Tag className="w-3 h-3 text-zinc-500" />
                {label}
              </div>
            ))}
          </div>

          {/* Issue Body */}
          <div className="p-4 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
            <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
              {issue.body}
            </p>
          </div>
        </Card>

        {/* Right Panel: AI Draft Response */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-zinc-100">
              AI-Drafted Response
            </h2>
            <div
              className={clsx(
                "px-2.5 py-1 rounded-full text-xs font-bold",
                event.confidence >= 90
                  ? "bg-emerald-500/15 text-emerald-400"
                  : event.confidence >= 75
                    ? "bg-blue-500/15 text-blue-400"
                    : "bg-yellow-500/15 text-yellow-400"
              )}
            >
              {event.confidence.toFixed(1)}% confidence
            </div>
          </div>

          {/* Suggested Labels with confidence */}
          <div className="mb-4">
            <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">
              Suggested Labels
            </p>
            <div className="flex flex-wrap gap-2">
              {event.labels.map((label) => (
                <div
                  key={label.name}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-zinc-700 bg-zinc-800/50"
                >
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: label.color }}
                  />
                  <span className="text-xs font-medium text-zinc-300">
                    {label.name}
                  </span>
                  <span
                    className={clsx(
                      "text-[10px] font-mono font-semibold",
                      label.confidence >= 90
                        ? "text-emerald-400"
                        : label.confidence >= 75
                          ? "text-yellow-400"
                          : "text-orange-400"
                    )}
                  >
                    {label.confidence.toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Classification Badges */}
          <div className="flex items-center gap-2 mb-4">
            <CategoryBadge category={event.category} />
            <PriorityBadge priority={event.priority} />
          </div>

          {/* Draft Response Textarea */}
          <div className="mb-4">
            <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">
              Response Preview
            </p>
            {isEditing ? (
              <textarea
                value={draftResponse}
                onChange={(e) => setDraftResponse(e.target.value)}
                rows={8}
                className="w-full rounded-lg border border-indigo-500 bg-zinc-800 px-4 py-3 text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 focus:ring-offset-zinc-950 resize-y"
              />
            ) : (
              <div className="p-4 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
                  {draftResponse}
                </p>
              </div>
            )}
          </div>

          {/* Duplicate Detection Section */}
          {event.duplicates.length > 0 && (
            <div className="mb-4 p-4 rounded-lg border border-amber-500/30 bg-amber-500/5">
              <p className="text-xs font-medium text-amber-400 uppercase tracking-wider mb-2">
                Possible Duplicates Detected
              </p>
              <div className="space-y-2">
                {event.duplicates.map((dup) => (
                  <a
                    key={dup.issueNumber}
                    href={dup.htmlUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-between p-2.5 rounded-lg bg-zinc-800/50 border border-zinc-700/50 hover:border-zinc-600 transition-colors group"
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      <ExternalLink className="w-3.5 h-3.5 text-zinc-500 group-hover:text-amber-400 shrink-0" />
                      <span className="text-sm text-zinc-300 truncate">
                        #{dup.issueNumber} {dup.issueTitle}
                      </span>
                    </div>
                    <div className="flex items-center gap-1 shrink-0 ml-2">
                      <div className="w-12 h-1.5 bg-zinc-700 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full bg-amber-500"
                          style={{
                            width: `${dup.similarity * 100}%`,
                          }}
                        />
                      </div>
                      <span className="text-xs font-mono font-semibold text-amber-400 w-10 text-right">
                        {(dup.similarity * 100).toFixed(0)}%
                      </span>
                    </div>
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          {!actionTaken && (
            <div className="flex items-center gap-3 pt-4 border-t border-zinc-800">
              <Button
                variant="primary"
                icon={<Check className="w-4 h-4" />}
                onClick={handleApprove}
                className="bg-emerald-600 hover:bg-emerald-500 shadow-emerald-500/20"
              >
                Approve & Post
              </Button>
              <Button
                variant="secondary"
                icon={<Pencil className="w-4 h-4" />}
                onClick={handleEdit}
              >
                {isEditing ? "Editing..." : "Edit Draft"}
              </Button>
              <Button variant="ghost" onClick={handleDiscard} className="text-red-400 hover:text-red-300 hover:bg-red-500/10">
                <X className="w-4 h-4 mr-1" />
                Discard
              </Button>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
