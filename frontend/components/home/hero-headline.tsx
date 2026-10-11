"use client";

import { useEffect, useState } from "react";
import clsx from "clsx";

const WORDS = ["Turn", "one", "long", "video", "into", "a", "week", "of", "shorts."];
const STEP_MS = 230;

/**
 * The headline reads itself out like an animated caption: each word lights up
 * in turn, then the highlight settles on the last word.
 */
export function HeroHeadline() {
  const [active, setActive] = useState(-1);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      const timer = setTimeout(() => setActive(WORDS.length - 1));
      return () => clearTimeout(timer);
    }
    let index = -1;
    const timer = setInterval(() => {
      index += 1;
      setActive(index);
      if (index >= WORDS.length - 1) clearInterval(timer);
    }, STEP_MS);
    return () => clearInterval(timer);
  }, []);

  return (
    <h1 className="font-display max-w-5xl text-[clamp(56px,11vw,148px)] leading-[0.86] font-black uppercase">
      {WORDS.map((word, i) => (
        <span key={word + i}>
          <span
            className={clsx(
              "inline-block rounded-[0.08em] px-[0.06em] transition-colors duration-150",
              i === active ? "bg-caption text-caption-ink" : i < active ? "text-text" : "text-line-strong",
            )}
          >
            {word}
          </span>{" "}
        </span>
      ))}
    </h1>
  );
}
