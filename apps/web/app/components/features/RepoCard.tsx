import { Star, GitFork, Clock, AlertCircle } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { Avatar } from "../ui/Avatar";
import { HealthScoreDots } from "./HealthDots";
import { Badge } from "../ui/Badge";
import type { Repo } from "@/lib/types";
import clsx from "clsx";
import Link from "next/link";

interface RepoCardProps {
  repo: Repo;
}

function getScoreColor(score: number): string {
  if (score >= 85) return "text-emerald-400";
  if (score >= 70) return "text-yellow-400";
  if (score >= 50) return "text-orange-400";
  return "text-red-400";
}

function getScoreDot(score: number): string {
  if (score >= 85) return "bg-emerald-400";
  if (score >= 70) return "bg-yellow-400";
  if (score >= 50) return "bg-orange-400";
  return "bg-red-400";
}

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

export function RepoCard({ repo }: RepoCardProps) {
  return (
    <Link href={`/dashboard/repos/${repo.id}`}>
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5 hover:border-zinc-700 hover:bg-zinc-800/50 transition-all group cursor-pointer h-full flex flex-col">
        {/* Header */}
        <div className="flex items-start gap-3">
          <Avatar src={repo.avatarUrl} alt={repo.name} size="lg" />
          <div className="min-w-0 flex-1">
            <h3 className="text-sm font-semibold text-zinc-100 group-hover:text-indigo-400 transition-colors truncate">
              {repo.fullName}
            </h3>
            <p className="text-xs text-zinc-500 mt-0.5 line-clamp-2">
              {repo.description}
            </p>
          </div>
        </div>

        {/* Language */}
        <div className="mt-3 flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: LANGUAGE_COLORS[repo.language] || "#71717a" }}
            />
            <span className="text-xs text-zinc-400">{repo.language}</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-zinc-400">
            <Star className="w-3.5 h-3.5" />
            {repo.stars.toLocaleString()}
          </div>
          <div className="flex items-center gap-1 text-xs text-zinc-400">
            <GitFork className="w-3.5 h-3.5" />
            {repo.forks.toLocaleString()}
          </div>
        </div>

        {/* Spacer to push bottom content down */}
        <div className="flex-1" />

        {/* Stats */}
        <div className="mt-4 pt-3 border-t border-zinc-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={clsx("w-2 h-2 rounded-full", getScoreDot(repo.healthScore))} />
            <span className={clsx("text-xs font-semibold", getScoreColor(repo.healthScore))}>
              {repo.healthScore}
            </span>
            <span className="text-xs text-zinc-500">health</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-zinc-400">
            <AlertCircle className="w-3 h-3" />
            {repo.issuesThisWeek} this week
          </div>
        </div>

        {/* Last synced */}
        <div className="mt-2 flex items-center gap-1 text-[11px] text-zinc-600">
          <Clock className="w-3 h-3" />
          Synced {formatDistanceToNow(new Date(repo.lastSynced), { addSuffix: true })}
        </div>
      </div>
    </Link>
  );
}
