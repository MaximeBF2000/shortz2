"use client";

import { useBrandKits } from "@/lib/hooks/use-catalog";
import type { Clip } from "@/lib/types";

import { CaptionLayer } from "./caption-layer";
import { FramedVideo } from "./framed-video";
import { LogoLayer } from "./logo-layer";
import { Stage } from "./stage";

/** Everything the export will contain, drawn live: video, captions, logo. */
export function ClipPreview({ clip, video, time }: { clip: Clip; video: HTMLVideoElement | null; time: number }) {
  const { data: kits } = useBrandKits();
  const logoUrl = kits?.find((kit) => kit.id === clip.style.brand_kit_id)?.logo_url ?? null;

  return (
    <Stage className="rounded-[26px] bg-black">
      <FramedVideo video={video} framing={clip.framing} fill={clip.style.fill} />
      <CaptionLayer words={clip.words} style={clip.style.captions} time={time} />
      <LogoLayer url={logoUrl} style={clip.style.logo} />
    </Stage>
  );
}
