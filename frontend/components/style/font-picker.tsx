"use client";

import clsx from "clsx";

import { useFonts } from "@/lib/hooks/use-catalog";

/** Each font shown in itself. */
export function FontPicker({ value, onChange }: { value: string; onChange: (family: string) => void }) {
  const fonts = useFonts();
  return (
    <div role="radiogroup" aria-label="Font" className="grid grid-cols-3 gap-1.5">
      {fonts.map((font) => (
        <button
          key={font.family}
          type="button"
          role="radio"
          aria-checked={value === font.family}
          onClick={() => onChange(font.family)}
          title={font.family}
          className={clsx(
            "h-11 truncate rounded-lg border px-2 text-[17px] transition-colors",
            value === font.family ? "border-caption bg-caption/10 text-text" : "border-line bg-ink text-muted hover:text-text",
          )}
          style={{ fontFamily: `"${font.family}"`, fontWeight: font.weight }}
        >
          {font.family}
        </button>
      ))}
    </div>
  );
}
