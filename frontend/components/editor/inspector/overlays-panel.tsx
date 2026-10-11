"use client";

import Link from "next/link";

import { Group } from "@/components/style/caption-style-editor";
import { HookStyleEditor } from "@/components/style/hook-style-editor";
import { LogoStyleEditor } from "@/components/style/logo-style-editor";
import { inputClass } from "@/components/ui/field";
import { useBrandKits } from "@/lib/hooks/use-catalog";

import type { PanelProps } from "./inspector";

export function OverlaysPanel({ clip, update }: PanelProps) {
  const { data: kits = [] } = useBrandKits();
  const kit = kits.find((k) => k.id === clip.style.brand_kit_id);

  return (
    <div className="space-y-8">
      <Group title="Hook headline">
        <p className="-mt-1 text-[12px] leading-relaxed text-faint">
          A line over the first seconds that tells viewers why to keep watching.
        </p>
        <textarea
          value={clip.hook}
          onChange={(event) => update({ hook: event.target.value })}
          rows={2}
          maxLength={120}
          placeholder="e.g. Nobody tells you this about procrastination"
          className={`${inputClass} h-auto py-2`}
        />
        <HookStyleEditor
          value={clip.style.hook}
          onChange={(hook) => update({ style: { ...clip.style, hook } })}
        />
      </Group>
      <Group title="Logo">
        {kit?.logo_url ? (
          <LogoStyleEditor value={clip.style.logo} onChange={(logo) => update({ style: { ...clip.style, logo } })} />
        ) : (
          <p className="text-[13px] leading-relaxed text-muted">
            {kit ? `“${kit.name}” has no logo yet.` : "Apply a brand kit with a logo to place it on this clip."}{" "}
            <Link href="/brand-kits" className="text-text underline">
              Add a logo in Brand kits
            </Link>
            .
          </p>
        )}
      </Group>
    </div>
  );
}
