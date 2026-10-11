/** A swatch that opens the native color picker, plus the hex value. */
export function ColorField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="flex cursor-pointer items-center gap-2.5 rounded-[10px] border border-line bg-ink p-1.5 pr-3 hover:border-line-strong">
      <span className="relative size-7 shrink-0 overflow-hidden rounded-md border border-white/10" style={{ background: value }}>
        <input
          type="color"
          value={value}
          onChange={(event) => onChange(event.target.value.toUpperCase())}
          className="absolute inset-0 cursor-pointer opacity-0"
          aria-label={label}
        />
      </span>
      <span className="min-w-0">
        <span className="block text-[12px] leading-tight text-muted">{label}</span>
        <span className="tabular block text-[12px] leading-tight text-text">{value.toUpperCase()}</span>
      </span>
    </label>
  );
}
