"use client";

import { useParams } from "next/navigation";
import useSWR from "swr";

import { Editor } from "@/components/editor/editor";
import { fetcher } from "@/lib/api";
import { useClipEditor } from "@/lib/hooks/use-clip-editor";
import type { Project } from "@/lib/types";

export default function ClipEditorPage() {
  const { projectId, clipId } = useParams<{ projectId: string; clipId: string }>();
  const { data: project } = useSWR<Project>(`/api/projects/${projectId}`, fetcher);
  const editor = useClipEditor(clipId);

  if (!project || !editor.clip) {
    return <div className="grid h-dvh place-items-center text-sm text-muted">Loading the editor…</div>;
  }
  return <Editor project={project} {...editor} clip={editor.clip} />;
}
