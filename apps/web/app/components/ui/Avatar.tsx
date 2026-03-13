import clsx from "clsx";

interface AvatarProps {
  src?: string;
  alt: string;
  size?: "sm" | "md" | "lg" | "xl";
  fallback?: string;
  className?: string;
}

const sizeMap = {
  sm: "w-6 h-6 text-[10px]",
  md: "w-8 h-8 text-xs",
  lg: "w-10 h-10 text-sm",
  xl: "w-16 h-16 text-lg",
};

function getInitials(name: string): string {
  return name
    .split(/[\s/.-]/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() || "")
    .join("");
}

export function Avatar({ src, alt, size = "md", fallback, className }: AvatarProps) {
  const initials = fallback || getInitials(alt);

  if (src) {
    return (
      <img
        src={src}
        alt={alt}
        className={clsx(
          "rounded-full object-cover ring-1 ring-zinc-700",
          sizeMap[size],
          className
        )}
      />
    );
  }

  return (
    <div
      className={clsx(
        "rounded-full flex items-center justify-center font-semibold",
        "bg-indigo-600/20 text-indigo-400 ring-1 ring-indigo-500/30",
        sizeMap[size],
        className
      )}
      aria-label={alt}
    >
      {initials}
    </div>
  );
}
