import type { ClipStyle } from "@/lib/types";

/** Same defaults as backend/app/captions/style.py */
export const DEFAULT_STYLE: ClipStyle = {
  captions: {
    enabled: true,
    font: "Montserrat",
    font_size: 78,
    uppercase: true,
    text_color: "#FFFFFF",
    highlight_color: "#FFD83D",
    emphasis_color: "#4ADE80",
    stroke_color: "#000000",
    stroke_width: 7,
    shadow: true,
    position: 0.7,
    max_words: 3,
    animation: "pop",
  },
  hook: {
    enabled: true,
    duration: 3,
    font: "Montserrat",
    font_size: 58,
    text_color: "#111111",
    background_color: "#FFFFFF",
    position: 0.2,
  },
  logo: { enabled: false, corner: "top-right", size: 160, opacity: 0.9 },
  brand_kit_id: null,
};
