import type { ReactNode } from "react";

/** A labelled control. */
export function Field({ label, hint, children }: { label: string; hint?: ReactNode; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 flex items-baseline justify-between text-[13px] text-muted">
        {label}
        {hint && <span className="tabular text-faint">{hint}</span>}
      </span>
      {children}
    </label>
  );
}

export const inputClass =
  "h-10 w-full rounded-[10px] border border-line bg-ink px-3 text-sm text-text placeholder:text-faint focus:border-lilac focus:outline-none";
