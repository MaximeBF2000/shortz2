"use client";

import { useMemo } from "react";

import { activeWordIndex, buildPages, type Page } from "@/lib/captions/pages";
import { OUTPUT_HEIGHT } from "@/lib/framing";
import { useFonts } from "@/lib/hooks/use-catalog";
import type { CaptionStyle, CaptionWord } from "@/lib/types";

import { fontWeight } from "../../style/caption-font-faces";

interface Props {
  words: CaptionWord[];
  style: CaptionStyle;
  time: number;
}

/** Draws the caption page for the current time, mirroring the .ass output. */
export function CaptionLayer({ words, style, time }: Props) {
  const fonts = useFonts();
  const maxWords = style.animation === "single" ? 1 : style.max_words;
  const pages = useMemo(
    () => buildPages(words.filter((w) => !w.hidden), maxWords, style.font_size),
    [words, maxWords, style.font_size],
  );
  const page = pages.find((p) => time >= p.start && time < p.end);
  if (!style.enabled || !page) return null;

  const lineRatio = fonts.find((f) => f.family === style.font)?.line_ratio ?? 1.2;
  const animated = style.animation !== "none" && style.animation !== "single";
  const active = animated ? activeWordIndex(page, time) : null;

  return (
    <div
      className="absolute inset-x-0 px-10 text-center"
      style={{ top: style.position * OUTPUT_HEIGHT, transform: "translateY(-50%)" }}
    >
      <div
        key={page.start}
        className={style.animation === "pop" || !animated ? "animate-cap-pop" : undefined}
        style={{
          fontFamily: `"${style.font}"`,
          fontWeight: fontWeight(style.font, fonts),
          fontSize: style.font_size,
          lineHeight: lineRatio,
          textTransform: style.uppercase ? "uppercase" : "none",
          WebkitTextStroke: style.stroke_width ? `${style.stroke_width * 2}px ${style.stroke_color}` : undefined,
          paintOrder: "stroke fill",
          textShadow: style.shadow ? "5px 5px 0 rgba(0,0,0,0.5)" : undefined,
          whiteSpace: "nowrap",
        }}
      >
        {page.lines.map((line, lineIndex) => (
          <div key={lineIndex}>
            {line.map((wordIndex, i) => (
              <span key={wordIndex} style={{ color: wordColor(page, wordIndex, active, style) }}>
                {i > 0 && " "}
                {page.words[wordIndex].text.trim()}
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

function wordColor(page: Page, index: number, active: number | null, style: CaptionStyle) {
  if (active !== null) {
    if (style.animation === "karaoke" && index <= active) return style.highlight_color;
    if ((style.animation === "highlight" || style.animation === "pop") && index === active) return style.highlight_color;
  }
  return page.words[index].emphasis ? style.emphasis_color : style.text_color;
}
