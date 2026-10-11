"use client";

import useSWR from "swr";

import { fetcher } from "../api";
import type { BrandKit, CaptionFont, CaptionPreset } from "../types";

const STATIC = { revalidateOnFocus: false, revalidateIfStale: false };

export function useFonts() {
  return useSWR<CaptionFont[]>("/api/fonts", fetcher, STATIC).data ?? [];
}

export function usePresets() {
  return useSWR<CaptionPreset[]>("/api/presets", fetcher, STATIC).data ?? [];
}

export function useBrandKits() {
  return useSWR<BrandKit[]>("/api/brand-kits", fetcher);
}

/** CSS line-height that matches libass line spacing for a font. */
export function useLineRatio(family: string) {
  const fonts = useFonts();
  return fonts.find((font) => font.family === family)?.line_ratio ?? 1.2;
}
