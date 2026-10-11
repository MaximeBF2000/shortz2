"use client";

import { useParams } from "next/navigation";
import useSWR from "swr";

import { ClipGrid } from "@/components/project/clip-grid";
import { ProcessingPanel } from "@/components/project/processing-panel";
import { ProjectFailed } from "@/components/project/project-failed";
import { ProjectHeader } from "@/components/project/project-header";
import { fetcher } from "@/lib/api";
import type { Project } from "@/lib/types";

export default function ProjectPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: project, error, mutate } = useSWR<Project>(`/api/projects/${projectId}`, fetcher, {
    refreshInterval: (p) => (!p || isBusy(p) ? 2000 : 0),
  });

  if (error) {
    return <p className="mx-auto max-w-7xl px-4 py-20 text-danger sm:px-8">{(error as Error).message}</p>;
  }
  if (!project) return <div className="mx-auto h-96 max-w-7xl px-4 sm:px-8" aria-busy />;

  return (
    <main className="mx-auto max-w-7xl px-4 pb-24 sm:px-8">
      <ProjectHeader project={project} onChange={mutate} />
      {project.status === "ready" ? (
        <ClipGrid project={project} />
      ) : project.status === "failed" ? (
        <ProjectFailed project={project} onRetry={mutate} />
      ) : (
        <ProcessingPanel project={project} />
      )}
    </main>
  );
}

function isBusy(project: Project) {
  return (
    !["ready", "failed"].includes(project.status) ||
    project.clips.some((clip) => clip.render_status === "queued" || clip.render_status === "rendering")
  );
}
