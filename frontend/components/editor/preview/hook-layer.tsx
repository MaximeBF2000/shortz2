"use client";

import { wrapHook } from "@/lib/captions/pages";
import { OUTPUT_HEIGHT } from "@/lib/framing";
import { useFonts } from "@/lib/hooks/use-catalog";
import type { HookStyle } from "@/lib/types";

import { fontWeight } from "../../style/caption-font-faces";

/** The headline shown over the first seconds of a clip. `time` is relative to the clip start. */
export function HookLayer({ text, style, time }: { text: string; style: HookStyle; time: number }) {
  const fonts = useFonts();
  // Seeking can land a few frames before the clip start, so allow a little slack.
  if (!style.enabled || !text.trim() || time < -0.25 || time > style.duration) return null;

  const lineRatio = fonts.find((f) => f.family === style.font)?.line_ratio ?? 1.2;
  const fadeIn = Math.min(1, Math.max(0, time) / 0.15);
  const fadeOut = Math.min(1, (style.duration - time) / 0.2);

  return (
    <div
      className="absolute inset-x-0 flex justify-center text-center"
      style={{ top: style.position * OUTPUT_HEIGHT, transform: "translateY(-50%)", opacity: Math.min(fadeIn, fadeOut) }}
    >
      <div
        style={{
          fontFamily: `"${style.font}"`,
          fontWeight: fontWeight(style.font, fonts),
          fontSize: style.font_size,
          lineHeight: lineRatio,
          color: style.text_color,
          background: style.background_color,
          padding: 18,
          whiteSpace: "nowrap",
        }}
      >
        {wrapHook(text, style.font_size).map((line, i) => (
          <div key={i}>{line}</div>
        ))}
      </div>
    </div>
  );
}
