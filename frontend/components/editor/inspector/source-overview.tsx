"use client";

import { useEffect, useRef, useState } from "react";

import { cropRect } from "@/lib/framing";
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
        const rect = cropRect(framingRef.current, video.videoWidth, video.videoHeight, video.currentTime);
        const scale = width / video.videoWidth;
        // Dim everything outside the crop window.
        context.fillStyle = "rgba(10, 8, 14, 0.62)";
        context.fillRect(0, 0, rect.x * scale, height);
        context.fillRect((rect.x + rect.width) * scale, 0, width - (rect.x + rect.width) * scale, height);
        context.strokeStyle = "#FFD83D";
        context.lineWidth = 3;
        context.strokeRect(rect.x * scale + 1.5, rect.y * scale + 1.5, rect.width * scale - 3, rect.height * scale - 3);
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
