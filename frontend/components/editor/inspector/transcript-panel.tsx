"use client";

import { useState } from "react";
import clsx from "clsx";
import useSWR from "swr";

import { ScoreBadge } from "@/components/ui/score-badge";
import { fetcher } from "@/lib/api";
import type { CaptionWord, TranscriptWord } from "@/lib/types";

import type { PanelProps } from "./inspector";
import { WordPopover } from "./word-popover";

const CONTEXT_SECONDS = 12;

/**
 * The clip's words, plus a little of what's said before and after.
 * Click a word to fix its spelling, mark it as a keyword, remove it,
 * or move the clip's start or end to it.
 */
export function TranscriptPanel({ clip, update, player }: PanelProps) {
  const [selected, setSelected] = useState<{ word: TranscriptWord; inClip: boolean; index: number } | null>(null);
  const { data: transcript } = useSWR<{ words: TranscriptWord[] }>(`/api/projects/${clip.project_id}/transcript`, fetcher, {
    revalidateOnFocus: false,
  });
  const all = transcript?.words ?? [];
  const before = all.filter((w) => w.start >= clip.start - CONTEXT_SECONDS && w.end < clip.start - 0.05);
  const after = all.filter((w) => w.start > clip.end + 0.05 && w.start <= clip.end + CONTEXT_SECONDS);

  function editWord(index: number, changes: Partial<CaptionWord>) {
    update({ words: clip.words.map((word, i) => (i === index ? { ...word, ...changes } : word)) });
  }

  return (
    <div className="space-y-5">
      <div className="flex gap-3 rounded-xl border border-line bg-ink p-3">
        <ScoreBadge score={clip.score} />
        <p className="text-[13px] leading-relaxed text-muted">{clip.reason || "Picked by you."}</p>
      </div>
      <p className="text-[12px] text-faint">
        Click a word to edit it. Green words are keywords with their own caption color; struck-through words are
        hidden from the captions.
      </p>

      <div className="relative text-[15px] leading-[2.1]">
        <ContextWords words={before} onPick={(word, index) => setSelected({ word, inClip: false, index })} />
        {clip.words.map((word, index) => {
          const active = player.time >= word.start && player.time < word.end;
          return (
            <button
              key={`${word.start}-${index}`}
              type="button"
              onClick={() => setSelected({ word, inClip: true, index })}
              className={clsx(
                "mr-1 rounded px-0.5 transition-colors hover:bg-raise",
                active && "bg-caption text-caption-ink hover:bg-caption",
                !active && word.emphasis && "text-ok",
                word.hidden && "text-faint line-through",
              )}
            >
              {word.text}
            </button>
          );
        })}
        <ContextWords words={after} onPick={(word, index) => setSelected({ word, inClip: false, index })} />
      </div>

      {selected && (
        <WordPopover
          key={`${selected.word.start}-${selected.inClip}`}
          word={selected.inClip ? clip.words[selected.index] ?? selected.word : selected.word}
          inClip={selected.inClip}
          onClose={() => setSelected(null)}
          onPlay={() => player.seek(selected.word.start)}
          onEdit={(changes) => editWord(selected.index, changes)}
          onStartHere={() => {
            if (clip.end - selected.word.start >= 3) update({ start: selected.word.start });
            setSelected(null);
          }}
          onEndHere={() => {
            if (selected.word.end - clip.start >= 3) update({ end: selected.word.end });
            setSelected(null);
          }}
        />
      )}
    </div>
  );
}

function ContextWords({ words, onPick }: { words: TranscriptWord[]; onPick: (word: TranscriptWord, index: number) => void }) {
  return (
    <>
      {words.map((word, index) => (
        <button
          key={word.start}
          type="button"
          onClick={() => onPick(word, index)}
          className="mr-1 rounded px-0.5 text-faint hover:bg-raise hover:text-muted"
          title="Outside the clip"
        >
          {word.text}
        </button>
      ))}
    </>
  );
}
