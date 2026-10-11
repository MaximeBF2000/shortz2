import clsx from "clsx";

export function ProgressBar({ value, className }: { value: number; className?: string }) {
  return (
    <div
      role="progressbar"
      aria-valuenow={Math.round(value * 100)}
      aria-valuemin={0}
      aria-valuemax={100}
      className={clsx("h-1 overflow-hidden rounded-full bg-line", className)}
    >
      <div className="h-full rounded-full bg-caption transition-[width] duration-700" style={{ width: `${Math.max(2, value * 100)}%` }} />
    </div>
  );
}
