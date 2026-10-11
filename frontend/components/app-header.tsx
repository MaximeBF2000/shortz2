"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";

const NAV = [
  { href: "/", label: "Projects" },
  { href: "/brand-kits", label: "Brand kits" },
];

export function AppHeader() {
  const pathname = usePathname();
  // The editor uses the full screen and has its own top bar.
  if (pathname.includes("/clips/")) return null;

  return (
    <header className="mx-auto flex max-w-7xl items-center justify-between px-4 py-5 sm:px-8">
      <Link href="/" className="flex items-end gap-2" aria-label="Shortz home">
        <Logo />
      </Link>
      <nav className="flex gap-1 text-sm">
        {NAV.map((item) => {
          const active = item.href === "/" ? pathname === "/" || pathname.startsWith("/projects") : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "rounded-full px-4 py-2 transition-colors",
                active ? "bg-raise text-text" : "text-muted hover:text-text",
              )}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}

/** The wordmark: a tall condensed "SHORTZ" with the Z sitting in a caption highlight. */
export function Logo() {
  return (
    <span className="font-display flex items-center text-[28px] leading-none font-black uppercase">
      Short
      <span className="ml-0.5 rounded-[5px] bg-caption px-1 text-caption-ink">z</span>
    </span>
  );
}
