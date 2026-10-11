"use client";

import { useState } from "react";
import { EyeOff, Play, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { inputClass } from "@/components/ui/field";
import { Toggle } from "@/components/ui/toggle";
import { formatTimecode } from "@/lib/format";
import type { CaptionWord, TranscriptWord } from "@/lib/types";

interface Props {
  word: CaptionWord | TranscriptWord;
  inClip: boolean;
  onClose: () => void;
  onPlay: () => void;
  onEdit: (changes: Partial<CaptionWord>) => void;
  onStartHere: () => void;
  onEndHere: () => void;
}

/** Actions for one word. Sticks to the bottom of the panel so it never covers the text being read. */
export function WordPopover({ word, inClip, onClose, onPlay, onEdit, onStartHere, onEndHere }: Props) {
  const [text, setText] = useState(word.text);
  const emphasis = "emphasis" in word && word.emphasis;
  const hidden = "hidden" in word && Boolean(word.hidden);

  return (
    <div className="sticky bottom-0 -mx-5 -mb-5 space-y-3 border-t border-line bg-raise p-4 shadow-[0_-12px_24px_rgba(0,0,0,0.35)]">
      <div className="flex items-center justify-between">
        <p className="tabular text-[12px] text-muted">
          {inClip ? "In the clip" : "Outside the clip"}, at {formatTimecode(word.start)}
        </p>
        <button type="button" onClick={onClose} className="rounded p-1 text-muted hover:text-text" aria-label="Close">
          <X className="size-4" />
        </button>
      </div>

      {inClip && (
        <>
          <form
            className="flex gap-2"
            onSubmit={(event) => {
              event.preventDefault();
              if (text.trim()) onEdit({ text: text.trim() });
            }}
          >
            <input value={text} onChange={(e) => setText(e.target.value)} className={inputClass} aria-label="Word text" autoFocus />
            <Button type="submit" disabled={!text.trim() || text.trim() === word.text}>
              Save
            </Button>
          </form>
          <Toggle label="Keyword" checked={emphasis} onChange={(value) => onEdit({ emphasis: value })} />
        </>
      )}

      <div className="flex flex-wrap gap-2">
        <Button size="sm" onClick={onPlay} disabled={!inClip}>
          <Play className="size-3.5" /> Play from here
        </Button>
        <Button size="sm" onClick={onStartHere}>
          Start clip here
        </Button>
        <Button size="sm" onClick={onEndHere}>
          End clip here
        </Button>
        {inClip && (
          <Button size="sm" variant="ghost" onClick={() => onEdit({ hidden: !hidden })}>
            <EyeOff className="size-3.5" /> {hidden ? "Show in captions" : "Hide from captions"}
          </Button>
        )}
      </div>
    </div>
  );
}
