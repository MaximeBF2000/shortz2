"use client";

import { CaptionStyleEditor } from "@/components/style/caption-style-editor";

import { BrandKitBar } from "./brand-kit-bar";
import type { PanelProps } from "./inspector";

export function CaptionsPanel({ clip, update }: PanelProps) {
  return (
    <div className="space-y-6">
      <BrandKitBar style={clip.style} onApply={(style) => update({ style })} />
      <CaptionStyleEditor
        value={clip.style.captions}
        onChange={(captions) => update({ style: { ...clip.style, captions } })}
      />
    </div>
  );
}
