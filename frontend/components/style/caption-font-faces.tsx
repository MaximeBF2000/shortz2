"use client";

import { useFonts } from "@/lib/hooks/use-catalog";

/**
 * Loads the caption fonts from the API, so the preview uses the exact
 * .ttf files the renderer burns into the video.
 */
export function CaptionFontFaces() {
  const fonts = useFonts();
  if (!fonts.length) return null;
  const css = fonts
    .map(
      (font) =>
        `@font-face{font-family:"${font.family}";src:url("${font.url}") format("truetype");font-weight:${font.weight};font-display:swap}`,
    )
    .join("\n");
  return <style>{css}</style>;
}

export function fontWeight(family: string, fonts: { family: string; weight: number }[]) {
  return fonts.find((font) => font.family === family)?.weight ?? 400;
}
