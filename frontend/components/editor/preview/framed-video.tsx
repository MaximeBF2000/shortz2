"use client";

import { useEffect, useState } from "react";

import { useLatest } from "@/lib/hooks/use-latest";

import { OUTPUT_HEIGHT, OUTPUT_WIDTH, paintFrame, rectAt } from "@/lib/framing";
import type { FillStyle, Framing } from "@/lib/types";

const CANVAS_SCALE = 0.5; // draw at 540x960: sharp enough for a preview, cheap per frame

/**
 * Paints the source video into the 9:16 frame, following the crop track and
 * filling leftover space like the export. Redraws every animation frame.
 */
export function FramedVideo({ video, framing, fill }: { video: HTMLVideoElement | null; framing: Framing; fill: FillStyle }) {
  const [canvas, setCanvas] = useState<HTMLCanvasElement | null>(null);
  const framingRef = useLatest({ framing, fill });

  useEffect(() => {
    const context = canvas?.getContext("2d");
    if (!video || !canvas || !context) return;

    let frame = 0;
    const draw = () => {
      if (video.readyState >= 2 && video.videoWidth) {
        const { framing: current, fill: currentFill } = framingRef.current;
        const rect = rectAt(current, video.videoWidth, video.videoHeight, video.currentTime);
        paintFrame(context, video, rect, currentFill, canvas.width, canvas.height);
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
