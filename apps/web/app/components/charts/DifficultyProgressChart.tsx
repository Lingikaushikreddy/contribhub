"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { format, parseISO } from "date-fns";
import type { ContributionEntry, IssueComplexity } from "@/lib/types";

interface DifficultyProgressChartProps {
  contributions: ContributionEntry[];
}

const DIFFICULTY_LEVEL: Record<IssueComplexity, number> = {
  trivial: 1,
  easy: 2,
  medium: 3,
  hard: 4,
  expert: 5,
};

const DIFFICULTY_LABEL: Record<number, string> = {
  1: "Trivial",
  2: "Easy",
  3: "Medium",
  4: "Hard",
  5: "Expert",
};

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const data = payload[0].payload;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 shadow-xl max-w-[240px]">
      <p className="text-sm font-medium text-zinc-100 truncate">{data.title}</p>
      <p className="text-xs text-zinc-400 mt-0.5">{data.repo}</p>
      <div className="flex items-center justify-between mt-1">
        <span className="text-xs text-zinc-500">
          {format(parseISO(data.date), "MMM d, yyyy")}
        </span>
        <span className="text-xs font-medium text-indigo-400">
          {DIFFICULTY_LABEL[data.level]}
        </span>
      </div>
    </div>
  );
}

export function DifficultyProgressChart({ contributions }: DifficultyProgressChartProps) {
  const chartData = contributions
    .slice()
    .sort((a, b) => new Date(a.completedAt).getTime() - new Date(b.completedAt).getTime())
    .map((c) => ({
      date: c.completedAt,
      level: DIFFICULTY_LEVEL[c.difficulty],
      title: c.issueTitle,
      repo: c.repoName,
    }));

  return (
    <div className="w-full h-[250px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
          <XAxis
            dataKey="date"
            stroke="#52525b"
            tick={{ fill: "#71717a", fontSize: 11 }}
            tickFormatter={(val) => format(parseISO(val), "MMM d")}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            domain={[0, 5]}
            ticks={[1, 2, 3, 4, 5]}
            stroke="#52525b"
            tick={{ fill: "#71717a", fontSize: 10 }}
            tickFormatter={(val) => DIFFICULTY_LABEL[val] || ""}
            tickLine={false}
            axisLine={false}
            width={60}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="level"
            stroke="#10b981"
            strokeWidth={2}
            dot={{ r: 5, fill: "#10b981", stroke: "#064e3b", strokeWidth: 2 }}
            activeDot={{ r: 7, fill: "#10b981", stroke: "#064e3b", strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
