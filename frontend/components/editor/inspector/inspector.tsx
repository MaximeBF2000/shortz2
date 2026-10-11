"use client";

import { useState } from "react";
import clsx from "clsx";

import type { ClipPlayer } from "@/lib/hooks/use-clip-player";
import type { Clip, ClipChanges, Project } from "@/lib/types";

import { CaptionsPanel } from "./captions-panel";
import { FramingPanel } from "./framing-panel";
import { OverlaysPanel } from "./overlays-panel";
import { TranscriptPanel } from "./transcript-panel";

const TABS = [
  { id: "captions", label: "Captions" },
  { id: "transcript", label: "Words" },
  { id: "framing", label: "Framing" },
  { id: "overlays", label: "Hook & logo" },
] as const;

type Tab = (typeof TABS)[number]["id"];

export interface PanelProps {
  project: Project;
  clip: Clip;
  update: (changes: ClipChanges) => void;
  player: ClipPlayer;
  video: HTMLVideoElement | null;
}

export function Inspector(props: PanelProps) {
  const [tab, setTab] = useState<Tab>("captions");

  return (
    <aside className="flex flex-col border-t border-line bg-panel lg:min-h-0 lg:border-t-0 lg:border-l">
      <div role="tablist" aria-label="Edit" className="flex shrink-0 gap-1 overflow-x-auto border-b border-line px-3 pt-2">
        {TABS.map((item) => (
          <button
            key={item.id}
            role="tab"
            type="button"
            aria-selected={tab === item.id}
            onClick={() => setTab(item.id)}
            className={clsx(
              "-mb-px border-b-2 px-3 py-2.5 text-[13px] whitespace-nowrap transition-colors",
              tab === item.id ? "border-caption text-text" : "border-transparent text-muted hover:text-text",
            )}
          >
            {item.label}
          </button>
        ))}
      </div>
      <div role="tabpanel" className="p-5 lg:min-h-0 lg:flex-1 lg:overflow-y-auto">
        {tab === "captions" && <CaptionsPanel {...props} />}
        {tab === "transcript" && <TranscriptPanel {...props} />}
        {tab === "framing" && <FramingPanel {...props} />}
        {tab === "overlays" && <OverlaysPanel {...props} />}
      </div>
    </aside>
  );
}
