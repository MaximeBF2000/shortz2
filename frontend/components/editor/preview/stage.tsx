"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

import { OUTPUT_HEIGHT, OUTPUT_WIDTH } from "@/lib/framing";

/**
 * A 1080x1920 canvas scaled down to fit its container.
 * Children are positioned in output pixels, exactly like the renderer.
 */
export function Stage({ children, className }: { children: ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(0);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    const observer = new ResizeObserver(([entry]) => setScale(entry.contentRect.width / OUTPUT_WIDTH));
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className={`relative aspect-[9/16] w-full overflow-hidden ${className ?? ""}`}>
      {scale > 0 && (
        <div
          className="absolute top-0 left-0 origin-top-left"
          style={{ width: OUTPUT_WIDTH, height: OUTPUT_HEIGHT, transform: `scale(${scale})` }}
        >
          {children}
        </div>
      )}
    </div>
  );
}
