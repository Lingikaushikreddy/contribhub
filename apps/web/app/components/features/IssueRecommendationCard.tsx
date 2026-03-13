"use client";

import { Clock, ThumbsUp, ThumbsDown, ArrowRight } from "lucide-react";
import { Button } from "../ui/Button";
import { CategoryBadge, PriorityBadge } from "../ui/Badge";
import { Avatar } from "../ui/Avatar";
import { HealthDots } from "./HealthDots";
import { DifficultyBar } from "./DifficultyBar";
import { SkillChip } from "./SkillChip";
import type { Recommendation, HealthLevel } from "@/lib/types";
import clsx from "clsx";

interface IssueRecommendationCardProps {
  recommendation: Recommendation;
  onAccept?: (id: string) => void;
  onThumbsUp?: (id: string) => void;
  onThumbsDown?: (id: string) => void;
}

export function IssueRecommendationCard({
  recommendation,
  onAccept,
  onThumbsUp,
  onThumbsDown,
}: IssueRecommendationCardProps) {
  const { issue, matchScore, healthLevel, difficulty, estimatedMinutes, prerequisites, maintainerResponseTime, repoAvatarUrl } = recommendation;

  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 hover:border-zinc-700 transition-all group">
      <div className="p-5">
        {/* Header: Repo + Match Score */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2.5">
            <Avatar src={repoAvatarUrl} alt={issue.repoName} size="md" />
            <div>
              <p className="text-xs font-medium text-zinc-300">{issue.repoName}</p>
              <p className="text-[11px] text-zinc-500">#{issue.number}</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <div
              className={clsx(
                "px-2.5 py-1 rounded-full text-xs font-bold",
                matchScore >= 90
                  ? "bg-emerald-500/15 text-emerald-400"
                  : matchScore >= 75
                    ? "bg-blue-500/15 text-blue-400"
                    : matchScore >= 60
                      ? "bg-yellow-500/15 text-yellow-400"
                      : "bg-zinc-500/15 text-zinc-400"
              )}
            >
              {matchScore}% match
            </div>
          </div>
        </div>

        {/* Issue Title */}
        <h3 className="text-base font-semibold text-zinc-100 mb-3 leading-snug">
          {issue.title}
        </h3>

        {/* Badges */}
        <div className="flex items-center gap-2 mb-3">
          <CategoryBadge category={issue.category} />
          <PriorityBadge priority={issue.priority} />
        </div>

        {/* Metrics Row */}
        <div className="grid grid-cols-3 gap-3 py-3 border-y border-zinc-800">
          <div>
            <p className="text-[10px] uppercase tracking-wider text-zinc-500 mb-1">Health</p>
            <HealthDots level={healthLevel as HealthLevel} />
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-wider text-zinc-500 mb-1">Difficulty</p>
            <DifficultyBar level={difficulty} />
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-wider text-zinc-500 mb-1">Est. Time</p>
            <div className="flex items-center gap-1 text-sm text-zinc-300">
              <Clock className="w-3.5 h-3.5 text-zinc-500" />
              {formatTime(estimatedMinutes)}
            </div>
          </div>
        </div>

        {/* Prerequisites */}
        <div className="mt-3">
          <p className="text-[10px] uppercase tracking-wider text-zinc-500 mb-1.5">Skills needed</p>
          <div className="flex flex-wrap gap-1.5">
            {prerequisites.map((skill) => (
              <SkillChip key={skill} name={skill} size="sm" />
            ))}
          </div>
        </div>

        {/* Response Time */}
        <div className="mt-3 flex items-center gap-1.5 text-xs text-zinc-500">
          <Clock className="w-3 h-3" />
          <span>Maintainer responds {maintainerResponseTime}</span>
        </div>

        {/* Actions */}
        <div className="mt-4 flex items-center gap-2">
          <Button
            size="sm"
            variant="primary"
            className="flex-1"
            icon={<ArrowRight className="w-3.5 h-3.5" />}
            onClick={() => onAccept?.(recommendation.id)}
          >
            I&apos;ll Take This
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onThumbsUp?.(recommendation.id)}
            aria-label="Good recommendation"
          >
            <ThumbsUp className="w-4 h-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onThumbsDown?.(recommendation.id)}
            aria-label="Bad recommendation"
          >
            <ThumbsDown className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
