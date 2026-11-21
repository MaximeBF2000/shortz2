import clsx from "clsx";

const SPEEDS = [0.5, 1, 1.5, 2];

/** Playback speed of the preview (the export is always at normal speed). */
export function SpeedPicker({ rate, onChange }: { rate: number; onChange: (rate: number) => void }) {
  return (
    <div role="radiogroup" aria-label="Playback speed" className="flex rounded-lg bg-panel p-0.5">
      {SPEEDS.map((speed) => (
        <button
          key={speed}
          type="button"
          role="radio"
          aria-checked={rate === speed}
          onClick={() => onChange(speed)}
          className={clsx(
            "tabular rounded-md px-2 py-1 text-[12px] transition-colors",
            rate === speed ? "bg-raise text-text" : "text-faint hover:text-text",
          )}
        >
          {speed}×
        </button>
      ))}
    </div>
  );
}
