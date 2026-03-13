import clsx from "clsx";
import type { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  padding?: boolean;
  hover?: boolean;
}

export function Card({ children, className, padding = true, hover = false }: CardProps) {
  return (
    <div
      className={clsx(
        "rounded-xl border border-zinc-800 bg-zinc-900",
        padding && "p-6",
        hover && "transition-colors hover:border-zinc-700 hover:bg-zinc-800/50",
        className
      )}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps {
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function CardHeader({ title, description, action, className }: CardHeaderProps) {
  return (
    <div className={clsx("flex items-start justify-between", className)}>
      <div>
        <h3 className="text-lg font-semibold text-zinc-100">{title}</h3>
        {description && (
          <p className="mt-1 text-sm text-zinc-400">{description}</p>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

interface CardBodyProps {
  children: ReactNode;
  className?: string;
}

export function CardBody({ children, className }: CardBodyProps) {
  return <div className={clsx("mt-4", className)}>{children}</div>;
}

interface CardFooterProps {
  children: ReactNode;
  className?: string;
}

export function CardFooter({ children, className }: CardFooterProps) {
  return (
    <div
      className={clsx(
        "mt-4 pt-4 border-t border-zinc-800 flex items-center",
        className
      )}
    >
      {children}
    </div>
  );
}

// ─── Stat Card ──────────────────────────────────────────────────────────────

interface StatCardProps {
  label: string;
  value: string | number;
  change?: string;
  changeType?: "positive" | "negative" | "neutral";
  icon?: ReactNode;
}

export function StatCard({ label, value, change, changeType = "neutral", icon }: StatCardProps) {
  const changeColor = {
    positive: "text-emerald-400",
    negative: "text-red-400",
    neutral: "text-zinc-400",
  };

  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-zinc-400">{label}</p>
          <p className="mt-2 text-3xl font-bold text-zinc-100 tracking-tight">
            {typeof value === "number" ? value.toLocaleString() : value}
          </p>
          {change && (
            <p className={clsx("mt-1 text-sm font-medium", changeColor[changeType])}>
              {change}
            </p>
          )}
        </div>
        {icon && (
          <div className="p-2.5 rounded-lg bg-zinc-800 text-zinc-400">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}
