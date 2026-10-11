import type { ProjectStatus } from "@/lib/types";

/** The processing pipeline, in order, with how much of the total time each step takes (roughly). */
export const STAGES: { status: ProjectStatus; label: string; detail: string; weight: number }[] = [
  { status: "downloading", label: "Getting the video", detail: "Downloading and preparing the source", weight: 0.2 },
  { status: "transcribing", label: "Transcribing", detail: "Writing down every word with its timing", weight: 0.45 },
  { status: "finding_clips", label: "Finding the best moments", detail: "Looking for hooks, stories and payoffs", weight: 0.15 },
  { status: "framing", label: "Framing for vertical", detail: "Following the speaker in each shot", weight: 0.2 },
];

export const STAGE_LABELS: Record<ProjectStatus, string> = {
  queued: "Waiting to start",
  downloading: "Getting the video",
  transcribing: "Transcribing",
  finding_clips: "Finding the best moments",
  framing: "Framing for vertical",
  ready: "Ready",
  failed: "Failed",
};

export function overallProgress(status: ProjectStatus, progress: number): number {
  if (status === "ready") return 1;
  const index = STAGES.findIndex((stage) => stage.status === status);
  if (index < 0) return 0;
  const done = STAGES.slice(0, index).reduce((sum, stage) => sum + stage.weight, 0);
  return done + STAGES[index].weight * progress;
}
