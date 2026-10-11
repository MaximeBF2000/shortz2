"use client";

import { ColorField } from "@/components/ui/color-field";
import { Field, inputClass } from "@/components/ui/field";
import { SliderField } from "@/components/ui/slider-field";
import { Toggle } from "@/components/ui/toggle";
import { useFonts } from "@/lib/hooks/use-catalog";
import type { HookStyle } from "@/lib/types";

/** Design of the headline shown over the first seconds. */
export function HookStyleEditor({ value, onChange }: { value: HookStyle; onChange: (style: HookStyle) => void }) {
  const fonts = useFonts();
  const set = (changes: Partial<HookStyle>) => onChange({ ...value, ...changes });

  return (
    <div className="space-y-4">
      <Toggle label="Show the hook headline" checked={value.enabled} onChange={(enabled) => set({ enabled })} />
      <SliderField
        label="Shown for"
        value={value.duration}
        min={0.5}
        max={10}
        step={0.5}
        format={(v) => `${v}s`}
        onChange={(duration) => set({ duration })}
      />
      <Field label="Font">
        <select value={value.font} onChange={(e) => set({ font: e.target.value })} className={inputClass}>
          {fonts.map((font) => (
            <option key={font.family}>{font.family}</option>
          ))}
        </select>
      </Field>
      <SliderField label="Size" value={value.font_size} min={30} max={120} format={(v) => `${v}px`} onChange={(font_size) => set({ font_size })} />
      <SliderField
        label="Height"
        value={value.position}
        min={0.05}
        max={0.9}
        step={0.01}
        format={(v) => `${Math.round(v * 100)}% from top`}
        onChange={(position) => set({ position })}
      />
      <div className="grid grid-cols-2 gap-2">
        <ColorField label="Text" value={value.text_color} onChange={(text_color) => set({ text_color })} />
        <ColorField label="Box" value={value.background_color} onChange={(background_color) => set({ background_color })} />
      </div>
    </div>
  );
}
