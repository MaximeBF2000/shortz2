"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Download, Trash2 } from "lucide-react";
import { toast } from "sonner";
import type { KeyedMutator } from "swr";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { formatDuration } from "@/lib/format";
import type { Project } from "@/lib/types";

export function ProjectHeader({ project, onChange }: { project: Project; onChange: KeyedMutator<Project> }) {
  const router = useRouter();
  const ready = project.status === "ready";
  const allExported = project.clips.length > 0 && project.clips.every((c) => c.render_status === "done");

  async function remove() {
    if (!confirm(`Delete “${project.title}” and all its clips? This can't be undone.`)) return;
    await api.deleteProject(project.id);
    toast.success("Video deleted");
    router.push("/");
  }

  async function exportAll() {
    await onChange(await api.renderAll(project.id), { revalidate: false });
    toast.success("Exporting every clip. Downloads appear on each clip when ready.");
  }

  return (
    <header className="flex flex-col gap-5 pt-4 pb-10 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        <Link href="/" className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted hover:text-text">
          <ArrowLeft className="size-4" /> All videos
        </Link>
        <h1 className="font-display text-[clamp(36px,5vw,60px)] leading-[0.95] font-extrabold uppercase">{project.title}</h1>
        <p className="tabular mt-3 text-sm text-muted">
          {project.duration != null && <>{formatDuration(project.duration)} long</>}
          {ready && (
            <>
              {", "}
              {project.clips.length} {project.clips.length === 1 ? "clip" : "clips"} found
            </>
          )}
        </p>
      </div>
      <div className="flex shrink-0 gap-2">
        <Button variant="ghost" onClick={remove} aria-label="Delete video">
          <Trash2 className="size-4" />
        </Button>
        {ready && (
          <Button variant="primary" onClick={exportAll} disabled={allExported}>
            <Download className="size-4" /> {allExported ? "All clips exported" : "Export all clips"}
          </Button>
        )}
      </div>
    </header>
  );
}
