import clsx from "clsx";

interface Option<T extends string> {
  value: T;
  label: string;
}

interface Props<T extends string> {
  value: T;
  options: Option<T>[];
  onChange: (value: T) => void;
  label: string;
  className?: string;
}

/** A row of mutually exclusive choices. */
export function Segmented<T extends string>({ value, options, onChange, label, className }: Props<T>) {
  return (
    <div role="radiogroup" aria-label={label} className={clsx("flex rounded-[10px] bg-ink p-1", className)}>
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          role="radio"
          aria-checked={value === option.value}
          onClick={() => onChange(option.value)}
          className={clsx(
            "flex-1 rounded-[7px] px-3 py-1.5 text-[13px] whitespace-nowrap transition-colors",
            value === option.value ? "bg-raise text-text shadow-sm" : "text-muted hover:text-text",
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
