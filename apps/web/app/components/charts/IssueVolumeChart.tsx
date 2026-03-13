"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";
import { format, parseISO } from "date-fns";
import type { DailyCount } from "@/lib/types";

interface IssueVolumeChartProps {
  data: DailyCount[];
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 shadow-xl">
      <p className="text-xs text-zinc-400">
        {format(parseISO(label), "MMM d, yyyy")}
      </p>
      <p className="text-sm font-semibold text-zinc-100 mt-0.5">
        {payload[0].value} issues
      </p>
    </div>
  );
}

export function IssueVolumeChart({ data }: IssueVolumeChartProps) {
  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
          <defs>
            <linearGradient id="issueGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
          <XAxis
            dataKey="date"
            stroke="#52525b"
            tick={{ fill: "#71717a", fontSize: 11 }}
            tickFormatter={(val) => format(parseISO(val), "MMM d")}
            tickLine={false}
            axisLine={false}
            interval={Math.floor(data.length / 6)}
          />
          <YAxis
            stroke="#52525b"
            tick={{ fill: "#71717a", fontSize: 11 }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="count"
            stroke="#6366f1"
            strokeWidth={2}
            fill="url(#issueGradient)"
            dot={false}
            activeDot={{ r: 4, fill: "#6366f1", stroke: "#1e1b4b", strokeWidth: 2 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
