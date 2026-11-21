"use client";

import { ColorField } from "@/components/ui/color-field";
import { Segmented } from "@/components/ui/segmented";
import type { FillStyle } from "@/lib/types";

/** What fills the frame around video that isn't 9:16 (a layout panel, "whole frame"). */
export function FillEditor({ value, onChange }: { value: FillStyle; onChange: (fill: FillStyle) => void }) {
  return (
    <div className="space-y-3">
      <Segmented
        label="Empty space"
        value={value.mode}
        options={[
          { value: "blur", label: "Blurred video" },
          { value: "color", label: "Solid color" },
        ]}
        onChange={(mode) => onChange({ ...value, mode })}
      />
      {value.mode === "color" && (
        <ColorField label="Color" value={value.color} onChange={(color) => onChange({ ...value, color })} />
      )}
    </div>
  );
}
