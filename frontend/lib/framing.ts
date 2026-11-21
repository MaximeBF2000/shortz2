/**
 * Where the crop sits in the source, and how it becomes a 9:16 frame.
 * Mirrors backend/app/render/framing.py: keep both in sync.
 */

import type { FillStyle, Framing, TrackPoint } from "./types";

export const OUTPUT_WIDTH = 1080;
export const OUTPUT_HEIGHT = 1920;
const ASPECT_TOLERANCE = 0.01;

export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

function even(value: number) {
  return Math.floor(value / 2) * 2;
}

/** Largest 9:16 window that fits in the source. */
export function cropSize(srcW: number, srcH: number) {
  const width = even(Math.min(srcW, (srcH * 9) / 16));
  const height = even(Math.min(srcH, (width * 16) / 9));
  return { width, height };
}

/** The camera at absolute time t: x eases between keyframes, everything jumps on cuts. */
export function pointAt<T extends TrackPoint>(track: T[], t: number): T | null {
  if (!track.length) return null;
  if (t <= track[0].t) return track[0];
  for (let i = 1; i < track.length; i++) {
    const previous = track[i - 1];
    const current = track[i];
    if (t < current.t) {
      if (current.cut) return previous;
      const span = current.t - previous.t || 1;
      return { ...previous, x: previous.x + ((current.x - previous.x) * (t - previous.t)) / span };
    }
  }
  return track[track.length - 1];
}

export function usesSmartTrack(framing: Framing) {
  return framing.mode === "auto" && framing.smart_crop && framing.smart_track.length > 0;
}

/** Source rectangle shown at time t. */
export function rectAt(framing: Framing, srcW: number, srcH: number, t: number): Rect {
  if (framing.mode === "fit") return { x: 0, y: 0, width: even(srcW), height: even(srcH) };

  let width: number;
  let height: number;
  let top: number;
  let x: number;
  const smart = usesSmartTrack(framing) ? pointAt(framing.smart_track, t) : null;
  if (smart) {
    width = even(Math.min(srcW, smart.w * srcW));
    height = even(Math.min(srcH, smart.h * srcH));
    top = Math.min(Math.max(0, Math.round(smart.top * srcH)), srcH - height);
    x = smart.x;
  } else {
    ({ width, height } = cropSize(srcW, srcH));
    top = Math.floor((srcH - height) / 2);
    x = framing.mode === "manual" ? framing.manual_x : (pointAt(framing.track, t)?.x ?? 0.5);
  }
  const left = Math.min(Math.max(0, Math.round(x * srcW - width / 2)), srcW - width);
  return { x: left, y: top, width, height };
}

export function fillsFrame(rect: Rect) {
  return Math.abs(rect.width / rect.height - OUTPUT_WIDTH / OUTPUT_HEIGHT) <= ASPECT_TOLERANCE;
}

/** Number of camera cuts, for display. */
export function cutCount(track: TrackPoint[]) {
  return track.filter((point) => point.cut).length;
}

/** Paints frame `rect` of `image` into a 9:16 canvas, filling leftover space like the export. */
export function paintFrame(
  context: CanvasRenderingContext2D,
  image: CanvasImageSource,
  rect: Rect,
  fill: FillStyle,
  width: number,
  height: number,
) {
  if (fillsFrame(rect)) {
    context.drawImage(image, rect.x, rect.y, rect.width, rect.height, 0, 0, width, height);
    return;
  }
  if (fill.mode === "color") {
    context.fillStyle = fill.color;
    context.fillRect(0, 0, width, height);
  } else {
    // The same picture, zoomed to cover and blurred.
    const cover = Math.max(width / rect.width, height / rect.height);
    context.filter = "blur(24px) brightness(0.88)";
    context.drawImage(image, rect.x, rect.y, rect.width, rect.height,
      (width - rect.width * cover) / 2, (height - rect.height * cover) / 2, rect.width * cover, rect.height * cover);
    context.filter = "none";
  }
  const fit = Math.min(width / rect.width, height / rect.height);
  context.drawImage(image, rect.x, rect.y, rect.width, rect.height,
    (width - rect.width * fit) / 2, (height - rect.height * fit) / 2, rect.width * fit, rect.height * fit);
}
