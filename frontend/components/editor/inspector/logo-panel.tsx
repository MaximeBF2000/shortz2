"use client";

import Link from "next/link";

import { LogoStyleEditor } from "@/components/style/logo-style-editor";
import { useBrandKits } from "@/lib/hooks/use-catalog";

import type { PanelProps } from "./inspector";

export function LogoPanel({ clip, update }: PanelProps) {
  const { data: kits = [] } = useBrandKits();
  const kit = kits.find((k) => k.id === clip.style.brand_kit_id);

  if (!kit?.logo_url) {
    return (
      <p className="text-[13px] leading-relaxed text-muted">
        {kit ? `“${kit.name}” has no logo yet.` : "Apply a brand kit with a logo to place it on this clip."}{" "}
        <Link href="/brand-kits" className="text-text underline">
          Add a logo in Brand kits
        </Link>
        .
      </p>
    );
  }
  return <LogoStyleEditor value={clip.style.logo} onChange={(logo) => update({ style: { ...clip.style, logo } })} />;
}
