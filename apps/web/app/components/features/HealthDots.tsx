import clsx from "clsx";
import type { HealthLevel } from "@/lib/types";

interface HealthDotsProps {
  level: HealthLevel | number;
  maxDots?: number;
  size?: "sm" | "md";
}

export function HealthDots({ level, maxDots = 5, size = "md" }: HealthDotsProps) {
  const sizeClass = size === "sm" ? "w-1.5 h-1.5" : "w-2 h-2";

  const filledColor = (idx: number) => {
    const ratio = idx / maxDots;
    if (ratio < 0.4) return "bg-emerald-400";
    if (ratio < 0.7) return "bg-yellow-400";
    return "bg-red-400";
  };

  return (
    <div className="flex items-center gap-1" title={`Health: ${level}/${maxDots}`}>
      {Array.from({ length: maxDots }).map((_, i) => (
        <div
          key={i}
          className={clsx(
            "rounded-full transition-colors",
            sizeClass,
            i < level ? filledColor(i) : "bg-zinc-700"
          )}
        />
      ))}
    </div>
  );
}

// Score-based variant (0-100)
interface HealthScoreDotsProps {
  score: number;
  size?: "sm" | "md";
}

export function HealthScoreDots({ score, size = "md" }: HealthScoreDotsProps) {
  const level = Math.round(score / 20) as HealthLevel;
  return <HealthDots level={level} size={size} />;
}
