"use client";

import { ColorField } from "@/components/ui/color-field";
import { Segmented } from "@/components/ui/segmented";
import { SliderField } from "@/components/ui/slider-field";
import { Toggle } from "@/components/ui/toggle";
import type { Animation, CaptionStyle } from "@/lib/types";

import { FontPicker } from "./font-picker";
import { PresetPicker } from "./preset-picker";

const ANIMATIONS: { value: Animation; label: string }[] = [
  { value: "pop", label: "Pop" },
  { value: "highlight", label: "Highlight" },
  { value: "karaoke", label: "Karaoke" },
  { value: "single", label: "One word" },
  { value: "none", label: "Static" },
];

/** Every caption design control. Used by the clip editor and the brand kit editor. */
export function CaptionStyleEditor({ value, onChange }: { value: CaptionStyle; onChange: (style: CaptionStyle) => void }) {
  const set = (changes: Partial<CaptionStyle>) => onChange({ ...value, ...changes });

  return (
    <div className="space-y-6">
      <Toggle label="Show captions" checked={value.enabled} onChange={(enabled) => set({ enabled })} />
      <Group title="Presets">
        <PresetPicker value={value} onPick={(preset) => onChange({ ...preset, enabled: true })} />
      </Group>
      <Group title="Font">
        <FontPicker value={value.font} onChange={(font) => set({ font })} />
      </Group>
      <Group title="Animation">
        <Segmented label="Animation" value={value.animation} options={ANIMATIONS} onChange={(animation) => set({ animation })} />
      </Group>
      <Group title="Layout">
        <SliderField label="Size" value={value.font_size} min={30} max={180} format={(v) => `${v}px`} onChange={(font_size) => set({ font_size })} />
        <SliderField
          label="Words on screen"
          value={value.max_words}
          min={1}
          max={8}
          onChange={(max_words) => set({ max_words })}
        />
        <SliderField
          label="Height"
          value={value.position}
          min={0.1}
          max={0.95}
          step={0.01}
          format={(v) => `${Math.round(v * 100)}% from top`}
          onChange={(position) => set({ position })}
        />
        <Toggle label="All caps" checked={value.uppercase} onChange={(uppercase) => set({ uppercase })} />
      </Group>
      <Group title="Colors">
        <div className="grid grid-cols-2 gap-2">
          <ColorField label="Text" value={value.text_color} onChange={(text_color) => set({ text_color })} />
          <ColorField label="Spoken word" value={value.highlight_color} onChange={(highlight_color) => set({ highlight_color })} />
          <ColorField label="Keywords" value={value.emphasis_color} onChange={(emphasis_color) => set({ emphasis_color })} />
          <ColorField label="Outline" value={value.stroke_color} onChange={(stroke_color) => set({ stroke_color })} />
        </div>
        <SliderField
          label="Outline width"
          value={value.stroke_width}
          min={0}
          max={20}
          format={(v) => (v ? `${v}px` : "None")}
          onChange={(stroke_width) => set({ stroke_width })}
        />
        <Toggle label="Drop shadow" checked={value.shadow} onChange={(shadow) => set({ shadow })} />
      </Group>
    </div>
  );
}

export function Group({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <fieldset className="space-y-3">
      <legend className="mb-3 text-[13px] font-semibold text-text">{title}</legend>
      {children}
    </fieldset>
  );
}
