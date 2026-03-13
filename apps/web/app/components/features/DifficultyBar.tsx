import clsx from "clsx";

interface DifficultyBarProps {
  level: number; // 1-5
  maxSegments?: number;
  showLabel?: boolean;
}

const LABELS = ["", "Trivial", "Easy", "Medium", "Hard", "Expert"];

const COLORS = [
  "",
  "bg-emerald-400",
  "bg-green-400",
  "bg-yellow-400",
  "bg-orange-400",
  "bg-red-400",
];

export function DifficultyBar({ level, maxSegments = 5, showLabel = false }: DifficultyBarProps) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-0.5">
        {Array.from({ length: maxSegments }).map((_, i) => (
          <div
            key={i}
            className={clsx(
              "w-3.5 h-2 rounded-sm transition-colors",
              i < level ? COLORS[level] : "bg-zinc-700"
            )}
          />
        ))}
      </div>
      {showLabel && (
        <span className="text-xs text-zinc-400">{LABELS[level] || ""}</span>
      )}
    </div>
  );
}
