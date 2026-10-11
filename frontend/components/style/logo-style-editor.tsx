"use client";

import { Segmented } from "@/components/ui/segmented";
import { SliderField } from "@/components/ui/slider-field";
import { Toggle } from "@/components/ui/toggle";
import type { LogoCorner, LogoStyle } from "@/lib/types";

const CORNERS: { value: LogoCorner; label: string }[] = [
  { value: "top-left", label: "Top left" },
  { value: "top-right", label: "Top right" },
  { value: "bottom-left", label: "Bottom left" },
  { value: "bottom-right", label: "Bottom right" },
];

export function LogoStyleEditor({ value, onChange }: { value: LogoStyle; onChange: (style: LogoStyle) => void }) {
  const set = (changes: Partial<LogoStyle>) => onChange({ ...value, ...changes });
  return (
    <div className="space-y-4">
      <Toggle label="Show the logo" checked={value.enabled} onChange={(enabled) => set({ enabled })} />
      <Segmented label="Corner" value={value.corner} options={CORNERS} onChange={(corner) => set({ corner })} className="flex-wrap" />
      <SliderField label="Width" value={value.size} min={60} max={400} format={(v) => `${v}px`} onChange={(size) => set({ size })} />
      <SliderField
        label="Opacity"
        value={value.opacity}
        min={0.1}
        max={1}
        step={0.05}
        format={(v) => `${Math.round(v * 100)}%`}
        onChange={(opacity) => set({ opacity })}
      />
    </div>
  );
}
