"use client";

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { HealthBreakdown } from "@/lib/types";

interface HealthScoreRadarProps {
  data: HealthBreakdown;
}

const DIMENSION_LABELS: Record<keyof HealthBreakdown, string> = {
  documentation: "Docs",
  responsiveness: "Response",
  issueResolution: "Resolution",
  communityEngagement: "Community",
  codeQuality: "Code Quality",
  releaseFrequency: "Releases",
};

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 shadow-xl">
      <p className="text-sm font-medium text-zinc-100">
        {payload[0].payload.dimension}
      </p>
      <p className="text-xs text-zinc-400 mt-0.5">
        Score: {payload[0].value}/100
      </p>
    </div>
  );
}

export function HealthScoreRadar({ data }: HealthScoreRadarProps) {
  const chartData = Object.entries(data).map(([key, value]) => ({
    dimension: DIMENSION_LABELS[key as keyof HealthBreakdown],
    score: value,
  }));

  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
          <PolarGrid stroke="#3f3f46" />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fill: "#a1a1aa", fontSize: 11 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: "#52525b", fontSize: 9 }}
            tickCount={5}
          />
          <Tooltip content={<CustomTooltip />} />
          <Radar
            name="Health"
            dataKey="score"
            stroke="#6366f1"
            fill="#6366f1"
            fillOpacity={0.2}
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
