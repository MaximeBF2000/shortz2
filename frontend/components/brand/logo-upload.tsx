"use client";

import { useRef } from "react";
import { ImageUp } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import type { BrandKit } from "@/lib/types";

export function LogoUpload({ kit, onChange }: { kit: BrandKit; onChange: () => void }) {
  const input = useRef<HTMLInputElement>(null);

  async function upload(file: File) {
    try {
      await api.uploadLogo(kit.id, file);
      onChange();
    } catch (error) {
      toast.error((error as Error).message);
    }
  }

  async function remove() {
    await api.deleteLogo(kit.id);
    onChange();
  }

  return (
    <div className="flex items-center gap-3">
      <div className="grid size-16 shrink-0 place-items-center rounded-xl border border-line bg-[repeating-conic-gradient(#2a2436_0_25%,#1f1a29_0_50%)] bg-[length:12px_12px]">
        {kit.logo_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={kit.logo_url} alt="Logo" className="max-h-12 max-w-12 object-contain" />
        ) : (
          <ImageUp className="size-5 text-faint" />
        )}
      </div>
      <div className="flex gap-2">
        <Button size="sm" onClick={() => input.current?.click()}>
          {kit.logo_url ? "Replace" : "Upload logo"}
        </Button>
        {kit.logo_url && (
          <Button size="sm" variant="ghost" onClick={remove}>
            Remove
          </Button>
        )}
      </div>
      <input
        ref={input}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        className="hidden"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) void upload(file);
          event.target.value = "";
        }}
      />
    </div>
  );
}
