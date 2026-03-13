"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { PriorityCount, IssuePriority } from "@/lib/types";

interface PriorityDistributionProps {
  data: PriorityCount[];
}

const PRIORITY_COLORS: Record<IssuePriority, string> = {
  P0: "#ef4444",
  P1: "#f97316",
  P2: "#eab308",
  P3: "#71717a",
};

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const data = payload[0];
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 shadow-xl">
      <p className="text-sm font-semibold text-zinc-100">{data.payload.priority}</p>
      <p className="text-xs text-zinc-400 mt-0.5">
        {data.value.toLocaleString()} issues
      </p>
    </div>
  );
}

export function PriorityDistribution({ data }: PriorityDistributionProps) {
  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
          <XAxis
            dataKey="priority"
            stroke="#52525b"
            tick={{ fill: "#71717a", fontSize: 12, fontWeight: 600 }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke="#52525b"
            tick={{ fill: "#71717a", fontSize: 11 }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
          <Bar dataKey="count" radius={[6, 6, 0, 0]} maxBarSize={56}>
            {data.map((entry, index) => (
              <Cell key={index} fill={PRIORITY_COLORS[entry.priority]} fillOpacity={0.8} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
