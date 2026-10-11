"use client";

import { useEffect, useState } from "react";

import { useLatest } from "@/lib/hooks/use-latest";

import { cropRect, OUTPUT_HEIGHT, OUTPUT_WIDTH } from "@/lib/framing";
import type { Framing } from "@/lib/types";

const CANVAS_SCALE = 0.5; // draw at 540x960: sharp enough for a preview, cheap per frame

/**
 * Paints the source video into the 9:16 frame, following the crop track
 * (or the blurred "fit" layout). Redraws every animation frame.
 */
export function FramedVideo({ video, framing }: { video: HTMLVideoElement | null; framing: Framing }) {
  const [canvas, setCanvas] = useState<HTMLCanvasElement | null>(null);
  const framingRef = useLatest(framing);

  useEffect(() => {
    const context = canvas?.getContext("2d");
    if (!video || !canvas || !context) return;

    let frame = 0;
    const draw = () => {
      if (video.readyState >= 2 && video.videoWidth) {
        paint(context, video, framingRef.current, canvas.width, canvas.height);
      }
      frame = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(frame);
  }, [video, canvas, framingRef]);

  return (
    <canvas
      ref={setCanvas}
      width={OUTPUT_WIDTH * CANVAS_SCALE}
      height={OUTPUT_HEIGHT * CANVAS_SCALE}
      className="absolute inset-0 size-full bg-black"
    />
  );
}

function paint(context: CanvasRenderingContext2D, video: HTMLVideoElement, framing: Framing, width: number, height: number) {
  const srcW = video.videoWidth;
  const srcH = video.videoHeight;

  if (framing.mode === "fit") {
    // Background: the frame scaled to cover, blurred and darkened.
    const cover = Math.max(width / srcW, height / srcH);
    context.filter = "blur(24px) brightness(0.88)";
    context.drawImage(video, (width - srcW * cover) / 2, (height - srcH * cover) / 2, srcW * cover, srcH * cover);
    context.filter = "none";
    // Foreground: the whole frame, fitted.
    const fit = Math.min(width / srcW, height / srcH);
    context.drawImage(video, (width - srcW * fit) / 2, (height - srcH * fit) / 2, srcW * fit, srcH * fit);
    return;
  }

  const rect = cropRect(framing, srcW, srcH, video.currentTime);
  context.drawImage(video, rect.x, rect.y, rect.width, rect.height, 0, 0, width, height);
}
