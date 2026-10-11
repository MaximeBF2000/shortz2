"use client";

import clsx from "clsx";

import { useFonts, usePresets } from "@/lib/hooks/use-catalog";
import type { CaptionStyle } from "@/lib/types";

import { fontWeight } from "./caption-font-faces";

/** One-click caption looks, each previewed as a mini caption. */
export function PresetPicker({ value, onPick }: { value: CaptionStyle; onPick: (style: CaptionStyle) => void }) {
  const presets = usePresets();
  const fonts = useFonts();

  return (
    <div className="grid grid-cols-2 gap-2">
      {presets.map((preset) => {
        const s = preset.captions;
        const selected = s.font === value.font && s.animation === value.animation && s.highlight_color === value.highlight_color;
        return (
          <button
            key={preset.name}
            type="button"
            onClick={() => onPick(s)}
            className={clsx(
              "group flex h-20 flex-col justify-between rounded-xl border p-2.5 text-left transition-colors",
              selected ? "border-caption" : "border-line hover:border-line-strong",
            )}
            style={{ background: "linear-gradient(160deg, #2b2440, #120f18)" }}
          >
            <span
              className="block truncate text-[19px] leading-none"
              style={{
                fontFamily: `"${s.font}"`,
                fontWeight: fontWeight(s.font, fonts),
                textTransform: s.uppercase ? "uppercase" : "none",
                color: s.text_color,
                WebkitTextStroke: s.stroke_width ? `${Math.min(3, s.stroke_width / 2.5)}px ${s.stroke_color}` : undefined,
                paintOrder: "stroke fill",
              }}
            >
              Make <span style={{ color: s.highlight_color }}>it</span> pop
            </span>
            <span className="text-[12px] text-muted group-hover:text-text">{preset.name}</span>
          </button>
        );
      })}
    </div>
  );
}
