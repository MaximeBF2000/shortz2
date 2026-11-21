"use client";

import useSWR from "swr";
import { TriangleAlert } from "lucide-react";

import { fetcher } from "@/lib/api";

interface ServiceStatus {
  ready: boolean;
  problem: string | null;
}

interface Health {
  transcriber: ServiceStatus;
  clip_finder: ServiceStatus;
}

/** Warns before a video is submitted if one of the AI services on this machine isn't ready. */
export function AiStatusNotice() {
  const { data } = useSWR<Health>("/api/health", fetcher, {
    refreshInterval: (d) => (d && d.transcriber.ready && d.clip_finder.ready ? 0 : 5000),
  });
  const problems = data ? [data.transcriber, data.clip_finder].filter((s) => !s.ready).map((s) => s.problem) : [];
  if (!problems.length) return null;

  return (
    <div role="status" className="mb-4 flex gap-3 rounded-2xl border border-caption/40 bg-caption/5 p-4 text-sm">
      <TriangleAlert className="mt-0.5 size-4 shrink-0 text-caption" aria-hidden />
      <div className="space-y-1 leading-relaxed">
        <p className="font-semibold">Videos can&apos;t be processed yet.</p>
        {problems.map((problem) => (
          <p key={problem}>{problem}</p>
        ))}
      </div>
    </div>
  );
}
