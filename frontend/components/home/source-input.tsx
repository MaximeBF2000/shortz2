"use client";

import { useRef, useState } from "react";
import clsx from "clsx";
import { Film, Link2, X } from "lucide-react";

import { formatBytes } from "./format-bytes";

interface Props {
  url: string;
  file: File | null;
  onUrlChange: (url: string) => void;
  onFileChange: (file: File | null) => void;
}

/** One field for both ways in: paste a link, or drop / pick a video file. */
export function SourceInput({ url, file, onUrlChange, onFileChange }: Props) {
  const fileInput = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setDragging(false);
        const dropped = event.dataTransfer.files[0];
        if (dropped) onFileChange(dropped);
      }}
      className={clsx(
        "flex min-h-16 items-center gap-3 rounded-2xl border-2 border-dashed bg-ink px-4 transition-colors",
        dragging ? "border-caption" : "border-transparent",
      )}
    >
      {file ? (
        <>
          <Film className="size-5 shrink-0 text-caption" aria-hidden />
          <div className="min-w-0 flex-1 py-3">
            <p className="truncate text-[15px]">{file.name}</p>
            <p className="text-[13px] text-muted">{formatBytes(file.size)}</p>
          </div>
          <button
            type="button"
            onClick={() => onFileChange(null)}
            className="rounded-lg p-2 text-muted hover:bg-raise hover:text-text"
            aria-label="Remove file"
          >
            <X className="size-4" />
          </button>
        </>
      ) : (
        <>
          <Link2 className="size-5 shrink-0 text-muted" aria-hidden />
          <input
            value={url}
            onChange={(event) => onUrlChange(event.target.value)}
            placeholder={dragging ? "Drop the video to upload it" : "Paste a YouTube link"}
            aria-label="YouTube link"
            className="h-16 min-w-0 flex-1 bg-transparent text-[17px] placeholder:text-faint focus:outline-none"
          />
          <span className="hidden text-[13px] text-faint sm:inline">or</span>
          <button
            type="button"
            onClick={() => fileInput.current?.click()}
            className="rounded-[10px] border border-line px-3 py-2 text-[13px] text-muted hover:border-line-strong hover:text-text"
          >
            Upload a file
          </button>
          <input
            ref={fileInput}
            type="file"
            accept="video/*,.mkv"
            className="hidden"
            onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
          />
        </>
      )}
    </div>
  );
}
