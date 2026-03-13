"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { CategoryCount, IssueCategory } from "@/lib/types";

interface CategoryBreakdownProps {
  data: CategoryCount[];
}

const CATEGORY_COLORS: Record<IssueCategory, string> = {
  bug: "#ef4444",
  feature: "#3b82f6",
  question: "#eab308",
  docs: "#22c55e",
  chore: "#71717a",
  security: "#a855f7",
  performance: "#f59e0b",
};

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const data = payload[0];
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 shadow-xl">
      <div className="flex items-center gap-2">
        <div
          className="w-2.5 h-2.5 rounded-full"
          style={{ backgroundColor: data.payload.fill }}
        />
        <span className="text-sm font-medium text-zinc-100 capitalize">
          {data.name}
        </span>
      </div>
      <p className="text-xs text-zinc-400 mt-1">
        {data.value.toLocaleString()} issues ({((data.value / data.payload.total) * 100).toFixed(1)}%)
      </p>
    </div>
  );
}

function CustomLegend({ payload }: any) {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1.5 justify-center mt-2">
      {payload?.map((entry: any, index: number) => (
        <div key={index} className="flex items-center gap-1.5">
          <div
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-xs text-zinc-400 capitalize">{entry.value}</span>
        </div>
      ))}
    </div>
  );
}

export function CategoryBreakdown({ data }: CategoryBreakdownProps) {
  const total = data.reduce((sum, d) => sum + d.count, 0);
  const chartData = data.map((d) => ({
    name: d.category,
    value: d.count,
    fill: CATEGORY_COLORS[d.category],
    total,
  }));

  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="45%"
            innerRadius={55}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
            stroke="none"
          >
            {chartData.map((entry, index) => (
              <Cell key={index} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend content={<CustomLegend />} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
