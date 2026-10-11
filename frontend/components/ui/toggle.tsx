import clsx from "clsx";

export function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className="flex w-full items-center justify-between py-1 text-sm text-text"
    >
      {label}
      <span className={clsx("relative h-5 w-9 rounded-full transition-colors", checked ? "bg-caption" : "bg-line")}>
        <span
          className={clsx(
            "absolute top-0.5 size-4 rounded-full transition-all",
            checked ? "left-[18px] bg-caption-ink" : "left-0.5 bg-muted",
          )}
        />
      </span>
    </button>
  );
}
