"use client";

import { useState } from "react";

import { useClipPlayer } from "@/lib/hooks/use-clip-player";
import type { Clip, ClipChanges, Project } from "@/lib/types";

import { ClipRail } from "./clip-rail";
import { EditorTopBar } from "./editor-top-bar";
import { Inspector } from "./inspector/inspector";
import { PreviewPanel } from "./preview/preview-panel";
import { useSpaceToPlay } from "./use-space-to-play";

interface Props {
  project: Project;
  clip: Clip;
  update: (changes: ClipChanges) => void;
  exportClip: () => Promise<void>;
  saving: boolean;
}

export function Editor({ project, clip, update, exportClip, saving }: Props) {
  const [video, setVideo] = useState<HTMLVideoElement | null>(null);
  const player = useClipPlayer(video, clip.start, clip.end);
  useSpaceToPlay(player.toggle);

  return (
    // Full-screen panes on desktop; a single scrolling page on phones.
    <div className="flex min-h-dvh flex-col lg:h-dvh">
      <EditorTopBar project={project} clip={clip} update={update} exportClip={exportClip} saving={saving} />
      <div className="grid flex-1 lg:min-h-0 lg:grid-cols-[200px_minmax(0,1fr)_400px]">
        <ClipRail project={project} activeId={clip.id} />
        <PreviewPanel project={project} clip={clip} update={update} player={player} video={video} />
        <Inspector project={project} clip={clip} update={update} player={player} video={video} />
      </div>
      {project.video_url && (
        <video
          ref={setVideo}
          src={project.video_url}
          preload="auto"
          playsInline
          className="pointer-events-none fixed top-0 left-0 size-px opacity-0"
          aria-hidden
        />
      )}
    </div>
  );
}
