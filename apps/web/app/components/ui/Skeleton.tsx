import clsx from "clsx";

interface SkeletonProps {
  className?: string;
  variant?: "line" | "circle" | "card";
}

export function Skeleton({ className, variant = "line" }: SkeletonProps) {
  const baseClass = "animate-pulse bg-zinc-800 rounded";

  if (variant === "circle") {
    return (
      <div className={clsx(baseClass, "rounded-full w-10 h-10", className)} />
    );
  }

  if (variant === "card") {
    return (
      <div className={clsx("rounded-xl border border-zinc-800 bg-zinc-900 p-6", className)}>
        <div className="space-y-4">
          <div className={clsx(baseClass, "h-4 w-3/4")} />
          <div className={clsx(baseClass, "h-4 w-1/2")} />
          <div className="flex gap-2 mt-4">
            <div className={clsx(baseClass, "h-6 w-16 rounded-md")} />
            <div className={clsx(baseClass, "h-6 w-20 rounded-md")} />
          </div>
          <div className={clsx(baseClass, "h-20 w-full mt-4")} />
        </div>
      </div>
    );
  }

  return <div className={clsx(baseClass, "h-4 w-full", className)} />;
}

export function SkeletonList({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton key={i} className={i === 0 ? "w-full" : i === 1 ? "w-5/6" : "w-4/6"} />
      ))}
    </div>
  );
}

export function SkeletonCards({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton key={i} variant="card" />
      ))}
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 overflow-hidden">
      <div className="p-4 border-b border-zinc-800">
        <Skeleton className="h-4 w-48" />
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="flex items-center gap-4 px-4 py-3 border-b border-zinc-800/50 last:border-0"
        >
          <Skeleton variant="circle" className="w-8 h-8" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-3.5 w-3/5" />
            <Skeleton className="h-3 w-2/5" />
          </div>
          <Skeleton className="h-6 w-16 rounded-md" />
          <Skeleton className="h-6 w-12 rounded-md" />
        </div>
      ))}
    </div>
  );
}
