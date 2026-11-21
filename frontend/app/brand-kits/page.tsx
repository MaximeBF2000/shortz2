"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { toast } from "sonner";

import { BrandKitEditor } from "@/components/brand/brand-kit-editor";
import { BrandKitList } from "@/components/brand/brand-kit-list";
import { DEFAULT_STYLE } from "@/components/brand/default-style";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { useBrandKits } from "@/lib/hooks/use-catalog";

export default function BrandKitsPage() {
  const { data: kits, mutate } = useBrandKits();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selected = kits?.find((kit) => kit.id === selectedId) ?? kits?.[0];

  async function create() {
    try {
      const kit = await api.createBrandKit(`Brand kit ${(kits?.length ?? 0) + 1}`, DEFAULT_STYLE);
      await mutate();
      setSelectedId(kit.id);
    } catch (error) {
      toast.error((error as Error).message);
    }
  }

  return (
    <main className="mx-auto max-w-7xl px-4 pb-24 sm:px-8">
      <header className="flex flex-col gap-4 pt-4 pb-10 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="font-display text-[clamp(44px,6vw,72px)] leading-[0.9] font-black uppercase">Brand kits</h1>
          <p className="mt-3 max-w-lg text-[15px] text-muted">
            Save your caption look and logo once. New clips start with your default kit.
          </p>
        </div>
        <Button variant="primary" onClick={create}>
          <Plus className="size-4" /> New brand kit
        </Button>
      </header>

      {kits && kits.length === 0 && (
        <div className="rounded-3xl border border-dashed border-line-strong p-10 text-center">
          <p className="font-display text-3xl font-extrabold uppercase">No brand kits yet</p>
          <p className="mx-auto mt-2 max-w-md text-sm text-muted">
            Create one to keep every clip on-brand: fonts, colors, caption animation and your logo.
          </p>
          <Button variant="primary" className="mt-6" onClick={create}>
            <Plus className="size-4" /> Create your first kit
          </Button>
        </div>
      )}

      {kits && selected && (
        <div className="grid gap-6 lg:grid-cols-[240px_minmax(0,1fr)]">
          <BrandKitList kits={kits} selectedId={selected.id} onSelect={setSelectedId} />
          <BrandKitEditor key={selected.id} kit={selected} onChange={() => mutate()} onDelete={() => setSelectedId(null)} />
        </div>
      )}
    </main>
  );
}
