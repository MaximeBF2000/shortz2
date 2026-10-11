"use client";

import { useEffect, useMemo, useState } from "react";
import useSWR from "swr";

import { CaptionLayer } from "@/components/editor/preview/caption-layer";
import { HookLayer } from "@/components/editor/preview/hook-layer";
import { LogoLayer } from "@/components/editor/preview/logo-layer";
import { Stage } from "@/components/editor/preview/stage";
import { fetcher } from "@/lib/api";
import type { CaptionWord, ClipStyle, ProjectSummary } from "@/lib/types";

const SAMPLE = "This is how your captions will look on every single clip you export".split(" ");
const WORD_SECONDS = 0.34;
const LOOP_SECONDS = SAMPLE.length * WORD_SECONDS + 1.2;

/** A looping fake clip that shows a style in motion, over one of your own videos when there is one. */
export function SamplePreview({ style, logoUrl }: { style: ClipStyle; logoUrl: string | null }) {
  const [time, setTime] = useState(0);
  const { data: projects } = useSWR<ProjectSummary[]>("/api/projects", fetcher);
  const backdrop = projects?.find((p) => p.poster_url)?.poster_url;

  const words = useMemo<CaptionWord[]>(
    () =>
      SAMPLE.map((text, i) => ({
        text,
        start: 0.4 + i * WORD_SECONDS,
        end: 0.4 + (i + 1) * WORD_SECONDS - 0.04,
        emphasis: text === "every",
      })),
    [],
  );

  useEffect(() => {
    let frame = 0;
    const startedAt = performance.now();
    const tick = (now: number) => {
      setTime(((now - startedAt) / 1000) % LOOP_SECONDS);
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, []);

  return (
    <div className="rounded-[30px] border-4 border-raise shadow-2xl shadow-black/50">
      <Stage className="rounded-[26px] bg-[linear-gradient(160deg,#3a2f57,#151019_60%)]">
        {backdrop && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={backdrop} alt="" className="absolute inset-0 size-full object-cover" />
        )}
        <HookLayer text="Your hook goes here" style={style.hook} time={time % 3.5} />
        <CaptionLayer words={words} style={style.captions} time={time} />
        <LogoLayer url={logoUrl} style={style.logo} />
      </Stage>
    </div>
  );
}
