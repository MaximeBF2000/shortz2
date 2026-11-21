/** Shapes returned by the API. Mirrors backend/app/schemas. */

export type ProjectStatus =
  | "queued"
  | "downloading"
  | "transcribing"
  | "finding_clips"
  | "framing"
  | "ready"
  | "failed";

export type ClipLength = "auto" | "short" | "medium" | "long";

export interface ProjectSettings {
  clip_length: ClipLength;
  max_clips: number;
  language: string | null;
  focus: string;
  brand_kit_id: string | null;
  smart_crop: boolean;
}

export interface ProjectSummary {
  id: string;
  title: string;
  source_type: "youtube" | "upload";
  source_url: string | null;
  status: ProjectStatus;
  progress: number;
  error: string | null;
  duration: number | null;
  poster_url: string | null;
  clip_count: number;
  created_at: string;
}

export interface Project extends ProjectSummary {
  width: number | null;
  height: number | null;
  fps: number | null;
  language: string | null;
  settings: ProjectSettings;
  video_url: string | null;
  clips: Clip[];
}

export interface CaptionWord {
  text: string;
  start: number;
  end: number;
  emphasis: boolean;
  hidden?: boolean;
}

export interface TrackPoint {
  t: number;
  x: number;
  cut: boolean;
}

/** Smart-crop keyframe: the crop's size and vertical position, normalized. */
export interface SmartPoint extends TrackPoint {
  w: number;
  top: number;
  h: number;
}

export type FramingMode = "auto" | "fit" | "manual";

export interface Framing {
  mode: FramingMode;
  manual_x: number;
  smart_crop: boolean;
  track: TrackPoint[];
  smart_track: SmartPoint[];
}

export type Animation = "highlight" | "pop" | "karaoke" | "single" | "none";
export type LogoCorner = "top-left" | "top-right" | "bottom-left" | "bottom-right";

export interface CaptionStyle {
  enabled: boolean;
  font: string;
  font_size: number;
  uppercase: boolean;
  text_color: string;
  highlight_color: string;
  emphasis_color: string;
  stroke_color: string;
  stroke_width: number;
  shadow: boolean;
  position: number;
  max_words: number;
  animation: Animation;
}

export interface LogoStyle {
  enabled: boolean;
  corner: LogoCorner;
  size: number;
  opacity: number;
}

/** What fills the frame when the kept part of the video isn't 9:16. */
export interface FillStyle {
  mode: "blur" | "color";
  color: string;
}

export interface ClipStyle {
  captions: CaptionStyle;
  fill: FillStyle;
  logo: LogoStyle;
  brand_kit_id: string | null;
}

export type RenderStatus = "idle" | "queued" | "rendering" | "done" | "failed";

export interface Clip {
  id: string;
  project_id: string;
  rank: number;
  title: string;
  reason: string;
  score: number;
  start: number;
  end: number;
  words: CaptionWord[];
  framing: Framing;
  style: ClipStyle;
  thumbnail_url: string | null;
  render_status: RenderStatus;
  render_progress: number;
  render_error: string | null;
  output_url: string | null;
}

/** Fields of a clip the user can change. */
export interface ClipChanges {
  title?: string;
  start?: number;
  end?: number;
  words?: CaptionWord[];
  framing_mode?: FramingMode;
  manual_x?: number;
  smart_crop?: boolean;
  style?: ClipStyle;
}

export interface BrandKit {
  id: string;
  name: string;
  is_default: boolean;
  style: ClipStyle;
  logo_url: string | null;
  created_at: string;
}

export interface CaptionFont {
  family: string;
  weight: number;
  url: string;
  line_ratio: number;
}

export interface CaptionPreset {
  name: string;
  captions: CaptionStyle;
}

export interface TranscriptWord {
  text: string;
  start: number;
  end: number;
}
