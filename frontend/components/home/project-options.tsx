"use client";

import { Minus, Plus } from "lucide-react";

import { Segmented } from "@/components/ui/segmented";
import { inputClass } from "@/components/ui/field";
import { useBrandKits } from "@/lib/hooks/use-catalog";
import type { ClipLength, ProjectSettings } from "@/lib/types";

const LENGTHS: { value: ClipLength; label: string }[] = [
  { value: "auto", label: "Auto" },
  { value: "short", label: "Under 30s" },
  { value: "medium", label: "30–60s" },
  { value: "long", label: "60–90s" },
];

const LANGUAGES = [
  ["", "Detect language"],
  ["en", "English"],
  ["fr", "French"],
  ["es", "Spanish"],
  ["de", "German"],
  ["pt", "Portuguese"],
  ["it", "Italian"],
  ["nl", "Dutch"],
  ["ja", "Japanese"],
  ["ko", "Korean"],
  ["zh", "Chinese"],
  ["hi", "Hindi"],
  ["ar", "Arabic"],
  ["ru", "Russian"],
];

interface Props {
  settings: ProjectSettings;
  onChange: (settings: ProjectSettings) => void;
}

export function ProjectOptions({ settings, onChange }: Props) {
  const { data: kits = [] } = useBrandKits();
  const set = (changes: Partial<ProjectSettings>) => onChange({ ...settings, ...changes });

  return (
    <div className="grid gap-4 lg:grid-cols-[auto_auto_1fr_1fr] lg:items-end">
      <Option label="Clip length">
        <Segmented label="Clip length" value={settings.clip_length} options={LENGTHS} onChange={(clip_length) => set({ clip_length })} />
      </Option>
      <Option label="Clips">
        <div className="flex h-[42px] items-center rounded-[10px] bg-ink p-1">
          <StepButton label="Fewer clips" onClick={() => set({ max_clips: Math.max(1, settings.max_clips - 1) })}>
            <Minus className="size-3.5" />
          </StepButton>
          <span className="tabular w-8 text-center text-sm">{settings.max_clips}</span>
          <StepButton label="More clips" onClick={() => set({ max_clips: Math.min(20, settings.max_clips + 1) })}>
            <Plus className="size-3.5" />
          </StepButton>
        </div>
      </Option>
      <Option label="Spoken language">
        <select
          value={settings.language ?? ""}
          onChange={(event) => set({ language: event.target.value || null })}
          className={inputClass}
        >
          {LANGUAGES.map(([code, name]) => (
            <option key={code} value={code}>
              {name}
            </option>
          ))}
        </select>
      </Option>
      <Option label="Caption style">
        <select
          value={settings.brand_kit_id ?? ""}
          onChange={(event) => set({ brand_kit_id: event.target.value || null })}
          className={inputClass}
        >
          <option value="">{kits.some((k) => k.is_default) ? "Default brand kit" : "Shortz default"}</option>
          {kits.map((kit) => (
            <option key={kit.id} value={kit.id}>
              {kit.name}
            </option>
          ))}
        </select>
      </Option>
      <div className="lg:col-span-4">
        <Option label="What should the clips be about? (optional)">
          <input
            value={settings.focus}
            onChange={(event) => set({ focus: event.target.value })}
            placeholder="e.g. the funniest stories, advice for founders, anything about sleep"
            className={inputClass}
            maxLength={500}
          />
        </Option>
      </div>
    </div>
  );
}

function Option({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="mb-1.5 text-[13px] text-muted">{label}</p>
      {children}
    </div>
  );
}

function StepButton({ label, onClick, children }: { label: string; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      className="grid size-[34px] place-items-center rounded-[7px] text-muted hover:bg-raise hover:text-text"
    >
      {children}
    </button>
  );
}
