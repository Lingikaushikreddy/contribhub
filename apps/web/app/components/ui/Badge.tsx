import clsx from "clsx";
import type { IssueCategory, IssuePriority, IssueComplexity } from "@/lib/types";

// ─── Category Badge ─────────────────────────────────────────────────────────

const categoryStyles: Record<IssueCategory, string> = {
  bug: "bg-red-500/15 text-red-400 border-red-500/30",
  feature: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  question: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
  docs: "bg-green-500/15 text-green-400 border-green-500/30",
  chore: "bg-zinc-500/15 text-zinc-400 border-zinc-500/30",
  security: "bg-purple-500/15 text-purple-400 border-purple-500/30",
  performance: "bg-amber-500/15 text-amber-400 border-amber-500/30",
};

const categoryIcons: Record<IssueCategory, string> = {
  bug: "\u2022",
  feature: "\u2726",
  question: "?",
  docs: "\u2261",
  chore: "\u2699",
  security: "\u26A1",
  performance: "\u26A1",
};

export function CategoryBadge({ category }: { category: IssueCategory }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium border",
        categoryStyles[category]
      )}
    >
      <span className="text-[10px]">{categoryIcons[category]}</span>
      {category}
    </span>
  );
}

// ─── Priority Badge ─────────────────────────────────────────────────────────

const priorityStyles: Record<IssuePriority, string> = {
  P0: "bg-red-500/15 text-red-400 border-red-500/30",
  P1: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  P2: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
  P3: "bg-zinc-500/15 text-zinc-400 border-zinc-500/30",
};

export function PriorityBadge({ priority }: { priority: IssuePriority }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold border font-mono",
        priorityStyles[priority]
      )}
    >
      {priority}
    </span>
  );
}

// ─── Complexity Badge ───────────────────────────────────────────────────────

const complexityStyles: Record<IssueComplexity, string> = {
  trivial: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  easy: "bg-green-500/15 text-green-400 border-green-500/30",
  medium: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
  hard: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  expert: "bg-red-500/15 text-red-400 border-red-500/30",
};

export function ComplexityBadge({ complexity }: { complexity: IssueComplexity }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border",
        complexityStyles[complexity]
      )}
    >
      {complexity}
    </span>
  );
}

// ─── Generic Badge ──────────────────────────────────────────────────────────

interface BadgeProps {
  children: React.ReactNode;
  color?: "red" | "orange" | "yellow" | "green" | "blue" | "purple" | "zinc" | "indigo" | "emerald" | "amber";
  className?: string;
}

const colorStyles: Record<NonNullable<BadgeProps["color"]>, string> = {
  red: "bg-red-500/15 text-red-400 border-red-500/30",
  orange: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  yellow: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
  green: "bg-green-500/15 text-green-400 border-green-500/30",
  blue: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  purple: "bg-purple-500/15 text-purple-400 border-purple-500/30",
  zinc: "bg-zinc-500/15 text-zinc-400 border-zinc-500/30",
  indigo: "bg-indigo-500/15 text-indigo-400 border-indigo-500/30",
  emerald: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  amber: "bg-amber-500/15 text-amber-400 border-amber-500/30",
};

export function Badge({ children, color = "zinc", className }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border",
        colorStyles[color],
        className
      )}
    >
      {children}
    </span>
  );
}
