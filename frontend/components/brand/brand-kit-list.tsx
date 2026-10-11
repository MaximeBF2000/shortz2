import clsx from "clsx";

import type { BrandKit } from "@/lib/types";

export function BrandKitList({ kits, selectedId, onSelect }: { kits: BrandKit[]; selectedId: string; onSelect: (id: string) => void }) {
  return (
    <ul className="flex gap-2 overflow-x-auto lg:flex-col lg:overflow-visible">
      {kits.map((kit) => (
        <li key={kit.id} className="shrink-0">
          <button
            type="button"
            onClick={() => onSelect(kit.id)}
            aria-current={kit.id === selectedId}
            className={clsx(
              "flex w-full items-center gap-3 rounded-xl p-3 text-left transition-colors",
              kit.id === selectedId ? "bg-raise" : "hover:bg-panel",
            )}
          >
            <span className="flex -space-x-1.5">
              {[kit.style.captions.text_color, kit.style.captions.highlight_color, kit.style.captions.emphasis_color].map((color, i) => (
                <span key={i} className="size-5 rounded-full border-2 border-ink" style={{ background: color }} />
              ))}
            </span>
            <span className="min-w-0">
              <span className="block truncate text-sm">{kit.name}</span>
              <span className="block text-[12px] text-faint">{kit.is_default ? "Default" : kit.style.captions.font}</span>
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
}
