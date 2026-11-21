"use client";

import clsx from "clsx";

import { Group } from "@/components/style/caption-style-editor";
import { FillEditor } from "@/components/style/fill-editor";
import { Toggle } from "@/components/ui/toggle";
import { cutCount } from "@/lib/framing";
import type { FramingMode } from "@/lib/types";

import type { PanelProps } from "./inspector";
import { SourceOverview } from "./source-overview";

const MODES: { value: FramingMode; title: string; description: string }[] = [
  { value: "auto", title: "Follow the speaker", description: "Tracks faces and cuts with each camera change." },
  { value: "manual", title: "Fixed position", description: "Drag the frame below to choose what stays in view." },
  { value: "fit", title: "Show the whole frame", description: "Shows the full shot, with the empty space filled (see below). Good for screen recordings." },
];

export function FramingPanel({ project, clip, update, video }: PanelProps) {
  const { mode, smart_crop, smart_track, track } = clip.framing;
  const cuts = cutCount(track);
  const layoutFound = smart_track.length > 0;

  return (
    <div className="space-y-6">
      <div role="radiogroup" aria-label="Framing" className="space-y-2">
        {MODES.map((option) => (
          <button
            key={option.value}
            type="button"
            role="radio"
            aria-checked={mode === option.value}
            onClick={() => update({ framing_mode: option.value })}
            className={clsx(
              "block w-full rounded-xl border p-3.5 text-left transition-colors",
              mode === option.value ? "border-caption bg-caption/5" : "border-line hover:border-line-strong",
            )}
          >
            <span className="block text-sm font-medium">{option.title}</span>
            <span className="mt-0.5 block text-[12px] leading-relaxed text-muted">{option.description}</span>
          </button>
        ))}
      </div>

      {mode === "auto" && (
        <div className="rounded-xl border border-line bg-ink p-3.5">
          <Toggle label="Smart crop" checked={smart_crop} onChange={(value) => update({ smart_crop: value })} />
          <p className="mt-1 text-[12px] leading-relaxed text-muted">
            {layoutFound
              ? "This clip uses a designed layout: only the speaker's video panel is kept."
              : "No layout found in this clip: the speaker fills the frame as usual."}
          </p>
        </div>
      )}

      {mode !== "fit" && (
        <div>
          <p className="mb-2 text-[13px] text-muted">
            {mode === "auto"
              ? `Source view: the box shows what's kept${cuts ? `, across ${cuts + 1} shots` : ""}.`
              : "Source view: drag to reposition."}
          </p>
          <SourceOverview
            video={video}
            framing={clip.framing}
            aspect={(project.width ?? 16) / (project.height ?? 9)}
            onMove={(manual_x) => update({ framing_mode: "manual", manual_x })}
          />
        </div>
      )}

      <Group title="Empty space">
        <p className="-mt-1 text-[12px] leading-relaxed text-faint">
          What fills the frame when the kept video isn&apos;t vertical.
        </p>
        <FillEditor value={clip.style.fill} onChange={(fill) => update({ style: { ...clip.style, fill } })} />
      </Group>
    </div>
  );
}
