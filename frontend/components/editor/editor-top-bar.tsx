"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { Logo } from "@/components/app-header";
import type { Clip, ClipChanges, Project } from "@/lib/types";

import { ExportButton } from "./export-button";

interface Props {
  project: Project;
  clip: Clip;
  update: (changes: ClipChanges) => void;
  exportClip: () => Promise<void>;
  saving: boolean;
}

export function EditorTopBar({ project, clip, update, exportClip, saving }: Props) {
  return (
    <header className="flex h-16 shrink-0 items-center gap-4 border-b border-line px-4">
      <Link href="/" className="hidden sm:block" aria-label="Shortz home">
        <Logo />
      </Link>
      <Link
        href={`/projects/${project.id}`}
        className="flex min-w-0 items-center gap-1.5 text-sm text-muted hover:text-text sm:border-l sm:border-line sm:pl-4"
      >
        <ArrowLeft className="size-4 shrink-0" />
        <span className="hidden max-w-56 truncate md:inline">{project.title}</span>
      </Link>
      <input
        value={clip.title}
        onChange={(event) => update({ title: event.target.value })}
        aria-label="Clip title"
        className="h-9 min-w-0 flex-1 rounded-lg border border-transparent bg-transparent px-2 text-[15px] font-medium hover:border-line focus:border-lilac focus:outline-none"
      />
      <span className="hidden text-[13px] text-faint sm:block" aria-live="polite">
        {saving ? "Saving…" : "Saved"}
      </span>
      <ExportButton clip={clip} onExport={exportClip} />
    </header>
  );
}
