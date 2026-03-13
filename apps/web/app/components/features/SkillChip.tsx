import clsx from "clsx";

interface SkillChipProps {
  name: string;
  proficiency?: number; // 0-100
  removable?: boolean;
  onRemove?: () => void;
  size?: "sm" | "md";
}

function getProficiencyColor(proficiency: number) {
  if (proficiency >= 80) return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
  if (proficiency >= 60) return "bg-blue-500/15 text-blue-400 border-blue-500/30";
  if (proficiency >= 40) return "bg-yellow-500/15 text-yellow-400 border-yellow-500/30";
  return "bg-zinc-500/15 text-zinc-400 border-zinc-500/30";
}

export function SkillChip({
  name,
  proficiency,
  removable = false,
  onRemove,
  size = "md",
}: SkillChipProps) {
  const colorClass = proficiency !== undefined
    ? getProficiencyColor(proficiency)
    : "bg-zinc-500/15 text-zinc-300 border-zinc-500/30";

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full border font-medium",
        colorClass,
        size === "sm" ? "px-2 py-0.5 text-[11px]" : "px-3 py-1 text-xs"
      )}
    >
      {proficiency !== undefined && (
        <span className="flex items-center gap-0.5">
          <span
            className={clsx(
              "inline-block rounded-full",
              size === "sm" ? "w-1 h-1" : "w-1.5 h-1.5",
              proficiency >= 80
                ? "bg-emerald-400"
                : proficiency >= 60
                  ? "bg-blue-400"
                  : proficiency >= 40
                    ? "bg-yellow-400"
                    : "bg-zinc-400"
            )}
          />
        </span>
      )}
      {name}
      {removable && (
        <button
          onClick={onRemove}
          className="ml-0.5 hover:text-zinc-100 transition-colors"
          aria-label={`Remove ${name}`}
        >
          x
        </button>
      )}
    </span>
  );
}
