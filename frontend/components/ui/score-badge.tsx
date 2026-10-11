import clsx from "clsx";

/** The AI's estimate of how well a clip will perform, 0-100. */
export function ScoreBadge({ score, className }: { score: number; className?: string }) {
  const tier = score >= 80 ? "high" : score >= 60 ? "mid" : "low";
  return (
    <span
      title="Predicted performance, out of 100"
      className={clsx(
        "font-display tabular inline-flex h-7 min-w-9 items-center justify-center rounded-md px-1.5 text-[19px] leading-none font-extrabold",
        tier === "high" && "bg-caption text-caption-ink",
        tier === "mid" && "bg-text text-ink",
        tier === "low" && "bg-raise text-muted",
        className,
      )}
    >
      {score}
    </span>
  );
}
