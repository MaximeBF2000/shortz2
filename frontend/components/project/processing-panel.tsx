import clsx from "clsx";
import { Check } from "lucide-react";

import { ProgressBar } from "@/components/ui/progress-bar";
import type { Project } from "@/lib/types";

import { STAGES } from "./stages";

/** Shows where the pipeline is: a real sequence, so the steps are numbered. */
export function ProcessingPanel({ project }: { project: Project }) {
  const current = STAGES.findIndex((stage) => stage.status === project.status);

  return (
    <section className="grid gap-8 rounded-3xl border border-line bg-panel p-6 sm:p-10 lg:grid-cols-[1fr_320px]">
      <div>
        <h2 className="font-display text-3xl font-extrabold uppercase">
          {project.status === "queued" ? "Waiting for a free worker" : "Working on your video"}
        </h2>
        <p className="mt-2 max-w-md text-sm leading-relaxed text-muted">
          This usually takes a few minutes for an hour of video. You can leave this page; processing continues in the
          background.
        </p>
        <ol className="mt-8 space-y-5">
          {STAGES.map((stage, index) => {
            const done = index < current;
            const active = index === current;
            return (
              <li key={stage.status} className="flex gap-4">
                <span
                  className={clsx(
                    "font-display grid size-9 shrink-0 place-items-center rounded-full text-lg font-extrabold",
                    done && "bg-caption text-caption-ink",
                    active && "border-2 border-caption text-caption",
                    !done && !active && "border border-line text-faint",
                  )}
                >
                  {done ? <Check className="size-4" strokeWidth={3} /> : index + 1}
                </span>
                <div className="min-w-0 flex-1 pt-1">
                  <p className={clsx("text-[15px]", active ? "text-text" : done ? "text-muted" : "text-faint")}>
                    {stage.label}
                  </p>
                  {active && (
                    <>
                      <p className="mt-0.5 text-[13px] text-muted">{stage.detail}</p>
                      <ProgressBar value={project.progress} className="mt-3 max-w-sm" />
                    </>
                  )}
                </div>
              </li>
            );
          })}
        </ol>
      </div>
      <PosterPreview url={project.poster_url} />
    </section>
  );
}

function PosterPreview({ url }: { url: string | null }) {
  return (
    <div className="relative mx-auto aspect-[9/16] w-full max-w-[260px] overflow-hidden rounded-[28px] border border-line bg-ink">
      {url ? (
        <>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={url} alt="" className="absolute inset-0 size-full object-cover opacity-60 blur-[2px]" />
          <div className="absolute inset-x-0 top-1/2 h-px animate-pulse bg-caption/80 shadow-[0_0_24px_4px] shadow-caption/40" />
        </>
      ) : (
        <div className="absolute inset-0 animate-pulse bg-raise" />
      )}
    </div>
  );
}
