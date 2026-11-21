"use client";

import { useEffect, useRef, useState } from "react";

import { rectAt } from "@/lib/framing";
import { useLatest } from "@/lib/hooks/use-latest";
import type { Framing } from "@/lib/types";

interface Props {
  video: HTMLVideoElement | null;
  framing: Framing;
  aspect: number;
  onMove: (centerX: number) => void;
}

/** The full landscape frame with the 9:16 window drawn on top. Drag to move it. */
export function SourceOverview({ video, framing, aspect, onMove }: Props) {
  const [canvas, setCanvas] = useState<HTMLCanvasElement | null>(null);
  const framingRef = useLatest(framing);
  const dragging = useRef(false);

  useEffect(() => {
    const context = canvas?.getContext("2d");
    if (!video || !canvas || !context) return;
    let frame = 0;
    const draw = () => {
      if (video.readyState >= 2 && video.videoWidth) {
        const { width, height } = canvas;
        context.drawImage(video, 0, 0, width, height);
        const rect = rectAt(framingRef.current, video.videoWidth, video.videoHeight, video.currentTime);
        const scale = width / video.videoWidth;
        // Dim everything outside the crop window.
        const [x0, y0, x1, y1] = [rect.x * scale, rect.y * scale, (rect.x + rect.width) * scale, (rect.y + rect.height) * scale];
        context.fillStyle = "rgba(10, 8, 14, 0.62)";
        context.fillRect(0, 0, width, y0);
        context.fillRect(0, y1, width, height - y1);
        context.fillRect(0, y0, x0, y1 - y0);
        context.fillRect(x1, y0, width - x1, y1 - y0);
        context.strokeStyle = "#FFD83D";
        context.lineWidth = 3;
        context.strokeRect(x0 + 1.5, y0 + 1.5, x1 - x0 - 3, y1 - y0 - 3);
      }
      frame = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(frame);
  }, [video, canvas, framingRef]);

  function move(event: React.PointerEvent<HTMLCanvasElement>) {
    const rect = event.currentTarget.getBoundingClientRect();
    onMove(Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width)));
  }

  return (
    <canvas
      ref={setCanvas}
      width={640}
      height={Math.round(640 / aspect)}
      className="w-full cursor-grab touch-none rounded-xl bg-black active:cursor-grabbing"
      onPointerDown={(event) => {
        dragging.current = true;
        event.currentTarget.setPointerCapture(event.pointerId);
        move(event);
      }}
      onPointerMove={(event) => dragging.current && move(event)}
      onPointerUp={() => (dragging.current = false)}
    />
  );
}
