"use client";

import { RotateCcw } from "lucide-react";
import { toast } from "sonner";
import type { KeyedMutator } from "swr";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import type { Project } from "@/lib/types";

export function ProjectFailed({ project, onRetry }: { project: Project; onRetry: KeyedMutator<Project> }) {
  async function retry() {
    try {
      await onRetry(await api.retryProject(project.id), { revalidate: false });
    } catch (error) {
      toast.error((error as Error).message);
    }
  }

  return (
    <section className="rounded-3xl border border-danger/30 bg-danger/5 p-6 sm:p-10">
      <h2 className="font-display text-3xl font-extrabold uppercase text-danger">This video couldn&apos;t be processed</h2>
      <p className="mt-3 max-w-2xl text-sm leading-relaxed text-text">{project.error ?? "Something went wrong."}</p>
      <p className="mt-2 max-w-2xl text-sm text-muted">
        Retrying picks up where it stopped, so finished steps aren&apos;t repeated.
      </p>
      <Button variant="primary" className="mt-6" onClick={retry}>
        <RotateCcw className="size-4" /> Try again
      </Button>
    </section>
  );
}
