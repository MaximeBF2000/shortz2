"use client";

import { Pause, Play } from "lucide-react";

import { formatTimecode } from "@/lib/format";
import type { ClipPlayer } from "@/lib/hooks/use-clip-player";
import type { Clip, ClipChanges, Project } from "@/lib/types";

import { ClipPreview } from "./clip-preview";
import { SpeedPicker } from "./speed-picker";
import { TrimBar } from "./trim-bar";

interface Props {
  project: Project;
  clip: Clip;
  update: (changes: ClipChanges) => void;
  player: ClipPlayer;
  video: HTMLVideoElement | null;
}

export function PreviewPanel({ project, clip, update, player, video }: Props) {
  const elapsed = Math.max(0, player.time - clip.start);

  return (
    <section className="flex flex-col items-center gap-4 lg:min-h-0 lg:overflow-y-auto bg-[radial-gradient(ellipse_at_center,var(--color-panel),var(--color-ink)_70%)] px-4 py-6">
      <div className="w-full max-w-[min(360px,calc((100dvh-260px)*9/16))]">
        <button
          type="button"
          onClick={player.toggle}
          aria-label={player.playing ? "Pause" : "Play"}
          className="group relative block w-full rounded-[30px] border-4 border-raise shadow-2xl shadow-black/50"
        >
          <ClipPreview clip={clip} video={video} time={player.time} />
          {!player.playing && (
            <span className="absolute inset-0 grid place-items-center rounded-[26px] bg-black/20 opacity-0 transition-opacity group-hover:opacity-100">
              <span className="grid size-16 place-items-center rounded-full bg-caption text-caption-ink">
                <Play className="ml-1 size-7 fill-current" />
              </span>
            </span>
          )}
        </button>
      </div>

      <div className="w-full max-w-2xl">
        <div className="mb-3 flex items-center gap-3">
          <button
            type="button"
            onClick={player.toggle}
            className="grid size-10 place-items-center rounded-full bg-text text-ink hover:bg-caption"
            aria-label={player.playing ? "Pause" : "Play"}
          >
            {player.playing ? <Pause className="size-4 fill-current" /> : <Play className="ml-0.5 size-4 fill-current" />}
          </button>
          <span className="tabular text-sm whitespace-nowrap">
            {formatTimecode(elapsed)} <span className="text-faint">/ {formatTimecode(clip.end - clip.start)}</span>
          </span>
          <SpeedPicker rate={player.rate} onChange={player.setRate} />
          <span className="ml-auto hidden text-right text-[12px] text-faint 2xl:block">
            Space to play · drag the timeline to scrub · drag the yellow handles to trim
          </span>
        </div>
        <TrimBar
          clip={clip}
          duration={project.duration ?? clip.end}
          time={player.time}
          onTrim={(start, end) => update({ start, end })}
          video={video}
        />
      </div>
    </section>
  );
}
