"use client";

import Link from "next/link";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { inputClass } from "@/components/ui/field";
import { api } from "@/lib/api";
import { useBrandKits } from "@/lib/hooks/use-catalog";
import type { ClipStyle } from "@/lib/types";

/** Apply a saved brand kit to this clip, or save this clip's look as a new one. */
export function BrandKitBar({ style, onApply }: { style: ClipStyle; onApply: (style: ClipStyle) => void }) {
  const { data: kits = [], mutate } = useBrandKits();

  async function saveAsKit() {
    const name = prompt("Name this brand kit", "My style");
    if (!name?.trim()) return;
    try {
      const kit = await api.createBrandKit(name.trim(), style);
      await mutate();
      onApply({ ...style, brand_kit_id: kit.id });
      toast.success(`Saved “${kit.name}”`);
    } catch (error) {
      toast.error((error as Error).message);
    }
  }

  return (
    <div className="rounded-xl border border-line bg-ink p-3">
      <p className="mb-2 text-[13px] text-muted">Brand kit</p>
      <div className="flex gap-2">
        <select
          value={style.brand_kit_id ?? ""}
          onChange={(event) => {
            const kit = kits.find((k) => k.id === event.target.value);
            if (kit) onApply({ ...kit.style, brand_kit_id: kit.id });
          }}
          className={inputClass}
          aria-label="Apply a brand kit"
        >
          <option value="" disabled>
            {kits.length ? "Apply a brand kit…" : "No brand kits yet"}
          </option>
          {kits.map((kit) => (
            <option key={kit.id} value={kit.id}>
              {kit.name}
            </option>
          ))}
        </select>
        <Button size="md" onClick={saveAsKit}>
          Save as kit
        </Button>
      </div>
      {!kits.length && (
        <p className="mt-2 text-[12px] text-faint">
          Save this look to reuse it on every clip, or set one up in{" "}
          <Link href="/brand-kits" className="text-muted underline hover:text-text">
            Brand kits
          </Link>
          .
        </p>
      )}
    </div>
  );
}
