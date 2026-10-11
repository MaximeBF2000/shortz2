import { Field } from "./field";

interface Props {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  format?: (value: number) => string;
  onChange: (value: number) => void;
}

export function SliderField({ label, value, min, max, step = 1, format = String, onChange }: Props) {
  return (
    <Field label={label} hint={format(value)}>
      <input
        type="range"
        className="w-full"
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </Field>
  );
}
