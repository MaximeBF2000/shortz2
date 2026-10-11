/** 9:16 crop math. Mirrors backend/app/render/framing.py. */

import type { Framing, TrackPoint } from "./types";

export const OUTPUT_WIDTH = 1080;
export const OUTPUT_HEIGHT = 1920;

function even(value: number) {
  return Math.floor(value / 2) * 2;
}

/** Largest 9:16 window that fits in the source. */
export function cropSize(srcW: number, srcH: number) {
  const width = even(Math.min(srcW, (srcH * 9) / 16));
  const height = even(Math.min(srcH, (width * 16) / 9));
  return { width, height };
}

/** Crop center (0..1 of source width) at absolute time t. */
export function xAt(track: TrackPoint[], t: number): number {
  if (!track.length) return 0.5;
  if (t <= track[0].t) return track[0].x;
  for (let i = 1; i < track.length; i++) {
    const previous = track[i - 1];
    const current = track[i];
    if (t < current.t) {
      if (current.cut) return previous.x;
      const span = current.t - previous.t || 1;
      return previous.x + ((current.x - previous.x) * (t - previous.t)) / span;
    }
  }
  return track[track.length - 1].x;
}

/** Source rectangle to show at time t (fill modes only). */
export function cropRect(framing: Framing, srcW: number, srcH: number, t: number) {
  const { width, height } = cropSize(srcW, srcH);
  const center = framing.mode === "manual" ? framing.manual_x : xAt(framing.track, t);
  const left = Math.min(Math.max(0, Math.round(center * srcW - width / 2)), srcW - width);
  return { x: left, y: Math.floor((srcH - height) / 2), width, height };
}

/** Number of camera cuts, for display. */
export function cutCount(track: TrackPoint[]) {
  return track.filter((point) => point.cut).length;
}
