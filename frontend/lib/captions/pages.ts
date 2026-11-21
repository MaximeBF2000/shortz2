/**
 * Split caption words into "pages" (the words on screen at once).
 * Mirrors backend/app/captions/pages.py so the preview matches the export.
 */

import type { CaptionWord } from "../types";

const TEXT_WIDTH = 920;
const CHAR_WIDTH = 0.6;
const MAX_GAP = 0.5;
const LINGER = 0.6;

export interface Page {
  words: CaptionWord[];
  start: number;
  end: number;
  lines: number[][];
}

export function buildPages(words: CaptionWord[], maxWords: number, fontSize: number): Page[] {
  const groups: CaptionWord[][] = [];
  for (const word of words) {
    const current = groups[groups.length - 1];
    const last = current?.[current.length - 1];
    if (
      !current ||
      current.length >= maxWords ||
      word.start - last!.end > MAX_GAP ||
      /[.?!]$/.test(last!.text.trimEnd())
    ) {
      groups.push([word]);
    } else {
      current.push(word);
    }
  }

  const maxChars = Math.max(4, Math.floor(TEXT_WIDTH / (CHAR_WIDTH * fontSize)));
  return groups.map((group, i) => {
    const lastWord = group[group.length - 1];
    let end = lastWord.end + LINGER;
    if (i + 1 < groups.length) end = Math.min(end, groups[i + 1][0].start);
    end = Math.max(end, lastWord.end);
    return { words: group, start: group[0].start, end, lines: splitLines(group, maxChars) };
  });
}

function splitLines(words: CaptionWord[], maxChars: number): number[][] {
  const lengths = words.map((w) => w.text.length);
  const total = lengths.reduce((a, b) => a + b, 0) + words.length - 1;
  const all = words.map((_, i) => i);
  if (total <= maxChars || words.length === 1) return [all];

  let bestSplit = 1;
  let bestWidth = total;
  for (let split = 1; split < words.length; split++) {
    const left = lengths.slice(0, split).reduce((a, b) => a + b, 0) + split - 1;
    const right = total - left - 1;
    if (Math.max(left, right) < bestWidth) {
      bestSplit = split;
      bestWidth = Math.max(left, right);
    }
  }
  return [all.slice(0, bestSplit), all.slice(bestSplit)];
}

/** Index of the word being spoken at time t (-1 before the first word starts). */
export function activeWordIndex(page: Page, t: number): number {
  let active = -1;
  page.words.forEach((word, i) => {
    if (t >= (i === 0 ? page.start : word.start)) active = i;
  });
  return active;
}
