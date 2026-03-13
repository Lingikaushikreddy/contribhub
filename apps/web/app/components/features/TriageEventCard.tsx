"use client";

import { formatDistanceToNow } from "date-fns";
import { Check, X, ExternalLink } from "lucide-react";
import { CategoryBadge, PriorityBadge } from "../ui/Badge";
import { Button } from "../ui/Button";
import type { TriageEvent } from "@/lib/types";
import clsx from "clsx";

interface TriageEventCardProps {
  event: TriageEvent;
  onApprove?: (eventId: string) => void;
  onDiscard?: (eventId: string) => void;
  compact?: boolean;
}

export function TriageEventCard({
  event,
  onApprove,
  onDiscard,
  compact = false,
}: TriageEventCardProps) {
  const timeAgo = formatDistanceToNow(new Date(event.createdAt), { addSuffix: true });

  return (
    <div
      className={clsx(
        "rounded-xl border bg-zinc-900 transition-colors",
        event.status === "approved"
          ? "border-emerald-500/30"
          : event.status === "discarded"
            ? "border-red-500/30 opacity-60"
            : "border-zinc-800 hover:border-zinc-700"
      )}
    >
      <div className={clsx("p-4", !compact && "sm:p-5")}>
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 text-xs text-zinc-500 mb-1.5">
              <span className="font-mono">{event.repoName}</span>
              <span>#{event.issueNumber}</span>
              <span>{timeAgo}</span>
            </div>
            <h4 className="text-sm font-medium text-zinc-100 truncate">
              {event.issueTitle}
            </h4>
          </div>
          <div className="flex items-center gap-1.5 shrink-0">
            <CategoryBadge category={event.category} />
            <PriorityBadge priority={event.priority} />
          </div>
        </div>

        {/* Confidence Bar */}
        <div className="mt-3 flex items-center gap-3">
          <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className={clsx(
                "h-full rounded-full transition-all",
                event.confidence >= 90
                  ? "bg-emerald-500"
                  : event.confidence >= 75
                    ? "bg-yellow-500"
                    : "bg-orange-500"
              )}
              style={{ width: `${event.confidence}%` }}
            />
          </div>
          <span className="text-xs font-mono text-zinc-400 w-12 text-right">
            {event.confidence.toFixed(1)}%
          </span>
        </div>

        {/* Draft Response Preview */}
        {!compact && event.draftResponse && (
          <div className="mt-3 p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
            <p className="text-xs text-zinc-400 line-clamp-2">
              {event.draftResponse}
            </p>
          </div>
        )}

        {/* Duplicate Alerts */}
        {!compact && event.duplicates.length > 0 && (
          <div className="mt-2.5">
            <p className="text-xs font-medium text-amber-400 mb-1">
              Possible duplicates found:
            </p>
            {event.duplicates.map((dup) => (
              <a
                key={dup.issueNumber}
                href={dup.htmlUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-xs text-zinc-400 hover:text-zinc-200 transition-colors py-0.5"
              >
                <ExternalLink className="w-3 h-3" />
                <span className="truncate">#{dup.issueNumber} {dup.issueTitle}</span>
                <span className="shrink-0 font-mono text-amber-400">
                  {(dup.similarity * 100).toFixed(0)}%
                </span>
              </a>
            ))}
          </div>
        )}

        {/* Actions */}
        {event.status === "pending" && (onApprove || onDiscard) && (
          <div className="mt-3 flex items-center gap-2 pt-3 border-t border-zinc-800">
            {onApprove && (
              <Button
                size="sm"
                variant="primary"
                icon={<Check className="w-3.5 h-3.5" />}
                onClick={() => onApprove(event.id)}
              >
                Approve
              </Button>
            )}
            {onDiscard && (
              <Button
                size="sm"
                variant="ghost"
                icon={<X className="w-3.5 h-3.5" />}
                onClick={() => onDiscard(event.id)}
              >
                Discard
              </Button>
            )}
          </div>
        )}

        {/* Status indicator for resolved events */}
        {event.status !== "pending" && (
          <div className="mt-3 pt-3 border-t border-zinc-800">
            <span
              className={clsx(
                "text-xs font-medium",
                event.status === "approved" ? "text-emerald-400" : "text-red-400"
              )}
            >
              {event.status === "approved" ? "Approved & Posted" : "Discarded"}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
