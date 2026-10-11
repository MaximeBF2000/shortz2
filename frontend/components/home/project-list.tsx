"use client";

import useSWR from "swr";

import { fetcher } from "@/lib/api";
import type { ProjectSummary } from "@/lib/types";

import { ProjectCard } from "./project-card";

const WORKING = new Set(["queued", "downloading", "transcribing", "finding_clips", "framing"]);

export function ProjectList() {
  const { data: projects, error } = useSWR<ProjectSummary[]>("/api/projects", fetcher, {
    refreshInterval: (data) => (data?.some((p) => WORKING.has(p.status)) ? 2000 : 0),
  });

  if (error) {
    return (
      <p className="mt-16 rounded-2xl border border-danger/30 bg-danger/5 p-5 text-sm text-danger">
        {(error as Error).message}
      </p>
    );
  }
  if (!projects?.length) return null;

  return (
    <section className="mt-16">
      <h2 className="font-display mb-5 text-4xl font-extrabold uppercase">Your videos</h2>
      <div className="grid gap-x-5 gap-y-8 sm:grid-cols-2 lg:grid-cols-3">
        {projects.map((project) => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </div>
    </section>
  );
}
