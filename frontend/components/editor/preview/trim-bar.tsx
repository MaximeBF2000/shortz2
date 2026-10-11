"use client";

import { useRef, useState } from "react";
import useSWR from "swr";

import { fetcher } from "@/lib/api";
import { formatTimecode } from "@/lib/format";
import { seekVideo } from "@/lib/video";
import type { Clip, TranscriptWord } from "@/lib/types";

const MIN_LENGTH = 3;
const MAX_LENGTH = 180;

interface Props {
  clip: Clip;
  duration: number;
  time: number;
  video: HTMLVideoElement | null;
  onSeek: (t: number) => void;
  onTrim: (start: number, end: number) => void;
}

/**
 * A zoomed timeline around the clip. Drag the handles to trim; cuts snap to
 * word boundaries so captions never start or end mid-word.
 */
export function TrimBar({ clip, duration, time, video, onSeek, onTrim }: Props) {
  const track = useRef<HTMLDivElement>(null);
  const [drag, setDrag] = useState<{ edge: "start" | "end"; start: number; end: number } | null>(null);
  const { data: transcript } = useSWR<{ words: TranscriptWord[] }>(`/api/projects/${clip.project_id}/transcript`, fetcher, {
    revalidateOnFocus: false,
  });
  const words = transcript?.words ?? [];

  const start = drag?.start ?? clip.start;
  const end = drag?.end ?? clip.end;
  const padding = Math.max(8, (clip.end - clip.start) * 0.35);
  const viewStart = Math.max(0, Math.min(clip.start, start) - padding);
  const viewEnd = Math.min(duration, Math.max(clip.end, end) + padding);
  const toPercent = (t: number) => ((t - viewStart) / (viewEnd - viewStart)) * 100;

  function timeAt(clientX: number) {
    const rect = track.current!.getBoundingClientRect();
    return viewStart + ((clientX - rect.left) / rect.width) * (viewEnd - viewStart);
  }

  function onPointerDown(edge: "start" | "end", event: React.PointerEvent) {
    event.stopPropagation();
    (event.target as HTMLElement).setPointerCapture(event.pointerId);
    setDrag({ edge, start: clip.start, end: clip.end });
  }

  function onPointerMove(event: React.PointerEvent) {
    if (!drag) return;
    const t = timeAt(event.clientX);
    const next =
      drag.edge === "start"
        ? { ...drag, start: clamp(t, Math.max(0, drag.end - MAX_LENGTH), drag.end - MIN_LENGTH) }
        : { ...drag, end: clamp(t, drag.start + MIN_LENGTH, Math.min(duration, drag.start + MAX_LENGTH)) };
    setDrag(next);
    if (video) seekVideo(video, drag.edge === "start" ? next.start : next.end); // show the frame under the handle
  }

  function onPointerUp() {
    if (!drag) return;
    const snappedStart = snap(words, drag.start, "start");
    const snappedEnd = snap(words, drag.end, "end");
    setDrag(null);
    if (snappedStart !== clip.start || snappedEnd !== clip.end) onTrim(snappedStart, snappedEnd);
  }

  return (
    <div>
      <div
        ref={track}
        className="relative h-14 cursor-pointer touch-none rounded-xl bg-panel select-none"
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onClick={(event) => !drag && onSeek(timeAt(event.clientX))}
      >
        <WordTicks words={words} viewStart={viewStart} viewEnd={viewEnd} />
        <div
          className="absolute inset-y-0 rounded-lg border-2 border-caption bg-caption/10"
          style={{ left: `${toPercent(start)}%`, width: `${toPercent(end) - toPercent(start)}%` }}
        >
          <Handle side="left" label="Trim start" value={start} onPointerDown={(e) => onPointerDown("start", e)} />
          <Handle side="right" label="Trim end" value={end} onPointerDown={(e) => onPointerDown("end", e)} />
        </div>
        {!drag && time >= viewStart && time <= viewEnd && (
          <div className="pointer-events-none absolute -inset-y-1 w-0.5 rounded bg-text" style={{ left: `${toPercent(time)}%` }} />
        )}
      </div>
      <div className="tabular mt-1.5 flex justify-between text-[11px] text-faint">
        <span>{formatTimecode(viewStart)}</span>
        <span className="text-muted">
          {formatTimecode(start)} – {formatTimecode(end)} ({(end - start).toFixed(1)}s)
        </span>
        <span>{formatTimecode(viewEnd)}</span>
      </div>
    </div>
  );
}

interface HandleProps {
  side: "left" | "right";
  label: string;
  value: number;
  onPointerDown: (e: React.PointerEvent) => void;
}

function Handle({ side, label, value, onPointerDown }: HandleProps) {
  return (
    <div
      role="slider"
      aria-label={label}
      aria-valuenow={Math.round(value * 10) / 10}
      aria-valuetext={formatTimecode(value)}
      tabIndex={0}
      onPointerDown={onPointerDown}
      onClick={(e) => e.stopPropagation()}
      className={`absolute inset-y-0 w-3 cursor-ew-resize bg-caption ${side === "left" ? "-left-1.5 rounded-l-lg" : "-right-1.5 rounded-r-lg"}`}
    >
      <span className="absolute inset-y-4 left-1/2 w-0.5 -translate-x-1/2 rounded bg-caption-ink/50" />
    </div>
  );
}

/** One tick per spoken word: a quick way to see speech and pauses. */
function WordTicks({ words, viewStart, viewEnd }: { words: TranscriptWord[]; viewStart: number; viewEnd: number }) {
  const span = viewEnd - viewStart;
  return (
    <div className="pointer-events-none absolute inset-x-0 inset-y-4">
      {words
        .filter((w) => w.end > viewStart && w.start < viewEnd)
        .map((w) => (
          <span
            key={w.start}
            className="absolute inset-y-0 rounded-sm bg-line-strong"
            style={{ left: `${((w.start - viewStart) / span) * 100}%`, width: `max(2px, ${((w.end - w.start) / span) * 100 - 0.15}%)` }}
          />
        ))}
    </div>
  );
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function snap(words: TranscriptWord[], t: number, edge: "start" | "end") {
  if (!words.length) return t;
  let best = t;
  let bestDistance = 0.6; // only snap when a word boundary is close
  for (const word of words) {
    const boundary = edge === "start" ? word.start : word.end;
    const distance = Math.abs(boundary - t);
    if (distance < bestDistance) {
      best = boundary;
      bestDistance = distance;
    }
  }
  return Math.round(best * 1000) / 1000;
}
