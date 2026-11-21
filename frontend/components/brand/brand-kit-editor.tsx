"use client";

import { useEffect, useRef, useState } from "react";
import { Star, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { CaptionStyleEditor, Group } from "@/components/style/caption-style-editor";
import { LogoStyleEditor } from "@/components/style/logo-style-editor";
import { Button } from "@/components/ui/button";
import { inputClass } from "@/components/ui/field";
import { api } from "@/lib/api";
import { useLatest } from "@/lib/hooks/use-latest";
import type { BrandKit, ClipStyle } from "@/lib/types";

import { LogoUpload } from "./logo-upload";
import { SamplePreview } from "./sample-preview";

const SAVE_DELAY = 600;

/** Edit a brand kit; changes save automatically. */
export function BrandKitEditor({ kit, onChange, onDelete }: { kit: BrandKit; onChange: () => void; onDelete: () => void }) {
  const [name, setName] = useState(kit.name);
  const [style, setStyle] = useState<ClipStyle>(kit.style);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);
  const latest = useLatest({ name, style });

  function schedule(next: { name?: string; style?: ClipStyle }) {
    if (next.name !== undefined) setName(next.name);
    if (next.style !== undefined) setStyle(next.style);
    clearTimeout(timer.current);
    timer.current = setTimeout(async () => {
      try {
        await api.updateBrandKit(kit.id, { name: latest.current.name.trim() || "Untitled kit", style: latest.current.style });
        onChange();
      } catch (error) {
        toast.error((error as Error).message);
      }
    }, SAVE_DELAY);
  }

  // Flush pending changes when switching kits.
  useEffect(
    () => () => {
      if (timer.current) {
        clearTimeout(timer.current);
        void api.updateBrandKit(kit.id, { name: latest.current.name.trim() || "Untitled kit", style: latest.current.style });
      }
    },
    [kit.id, latest],
  );

  async function makeDefault() {
    await api.updateBrandKit(kit.id, { is_default: true });
    onChange();
    toast.success(`New clips will use “${name}”`);
  }

  async function remove() {
    if (!confirm(`Delete “${name}”? Clips that use it keep their current look.`)) return;
    clearTimeout(timer.current);
    timer.current = undefined;
    await api.deleteBrandKit(kit.id);
    onDelete();
    onChange();
  }

  return (
    <div className="grid gap-8 rounded-3xl border border-line bg-panel p-5 sm:p-8 xl:grid-cols-[minmax(0,1fr)_300px]">
      <div className="min-w-0 space-y-8">
        <div className="flex flex-wrap items-center gap-2">
          <input
            value={name}
            onChange={(event) => schedule({ name: event.target.value })}
            className={`${inputClass} max-w-xs text-base`}
            aria-label="Brand kit name"
          />
          <Button onClick={makeDefault} disabled={kit.is_default}>
            <Star className={kit.is_default ? "size-4 fill-caption text-caption" : "size-4"} />
            {kit.is_default ? "Default kit" : "Make default"}
          </Button>
          <Button variant="danger" onClick={remove} aria-label="Delete brand kit">
            <Trash2 className="size-4" />
          </Button>
        </div>

        <div className="grid gap-10 2xl:grid-cols-2">
          <Group title="Captions">
            <CaptionStyleEditor value={style.captions} onChange={(captions) => schedule({ style: { ...style, captions } })} />
          </Group>
          <div className="space-y-10">
            <Group title="Logo">
              <LogoUpload kit={kit} onChange={onChange} />
              {kit.logo_url && <LogoStyleEditor value={style.logo} onChange={(logo) => schedule({ style: { ...style, logo } })} />}
            </Group>
          </div>
        </div>
      </div>

      <div className="order-first xl:order-none">
        <div className="mx-auto w-full max-w-[300px] xl:sticky xl:top-6">
          <SamplePreview style={style} logoUrl={kit.logo_url} />
        </div>
      </div>
    </div>
  );
}
