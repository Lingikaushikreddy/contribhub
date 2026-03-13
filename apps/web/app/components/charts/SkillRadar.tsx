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
import type { Skill } from "@/lib/types";

interface SkillRadarProps {
  skills: Skill[];
  color?: string;
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 shadow-xl">
      <p className="text-sm font-medium text-zinc-100">
        {payload[0].payload.name}
      </p>
      <p className="text-xs text-zinc-400 mt-0.5">
        Proficiency: {payload[0].value}%
      </p>
      <p className="text-xs text-zinc-500">
        {payload[0].payload.endorsements} endorsements
      </p>
    </div>
  );
}

export function SkillRadar({ skills, color = "#6366f1" }: SkillRadarProps) {
  return (
    <div className="w-full h-[250px]">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={skills}>
          <PolarGrid stroke="#3f3f46" />
          <PolarAngleAxis
            dataKey="name"
            tick={{ fill: "#a1a1aa", fontSize: 11 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={false}
            tickCount={5}
          />
          <Tooltip content={<CustomTooltip />} />
          <Radar
            name="Skill"
            dataKey="proficiency"
            stroke={color}
            fill={color}
            fillOpacity={0.2}
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
