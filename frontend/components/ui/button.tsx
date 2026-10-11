import clsx from "clsx";
import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";

const VARIANTS: Record<Variant, string> = {
  primary: "bg-caption text-caption-ink hover:brightness-105 font-semibold",
  secondary: "bg-raise text-text hover:bg-line border border-line",
  ghost: "text-muted hover:text-text hover:bg-raise",
  danger: "text-danger hover:bg-danger/10",
};

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: "sm" | "md" | "lg";
}

export function Button({ variant = "secondary", size = "md", className, ...props }: Props) {
  return (
    <button
      className={clsx(
        "inline-flex items-center justify-center gap-2 rounded-[10px] whitespace-nowrap transition disabled:pointer-events-none disabled:opacity-40",
        size === "sm" && "h-8 px-3 text-[13px]",
        size === "md" && "h-10 px-4 text-sm",
        size === "lg" && "h-12 px-6 text-[15px]",
        VARIANTS[variant],
        className,
      )}
      {...props}
    />
  );
}
