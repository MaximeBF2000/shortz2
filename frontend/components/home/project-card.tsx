import Link from "next/link";
import { AlertCircle, Link2, Upload } from "lucide-react";

import { ProgressBar } from "@/components/ui/progress-bar";
import { STAGE_LABELS, overallProgress } from "@/components/project/stages";
import { formatDuration, timeAgo } from "@/lib/format";
import type { ProjectSummary } from "@/lib/types";

export function ProjectCard({ project }: { project: ProjectSummary }) {
  const working = !["ready", "failed"].includes(project.status);

  return (
    <Link href={`/projects/${project.id}`} className="group block">
      <div className="relative aspect-video overflow-hidden rounded-2xl bg-raise">
        {project.poster_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={project.poster_url}
            alt=""
            className="size-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
          />
        )}
        {project.duration != null && (
          <span className="tabular absolute right-2.5 bottom-2.5 rounded-md bg-black/70 px-1.5 py-0.5 text-[12px]">
            {formatDuration(project.duration)}
          </span>
        )}
        {project.status === "ready" && (
          <span className="absolute top-2.5 left-2.5 rounded-md bg-caption px-2 py-1 text-[12px] font-semibold text-caption-ink">
            {project.clip_count} {project.clip_count === 1 ? "clip" : "clips"}
          </span>
        )}
      </div>
      <div className="mt-3 flex gap-2">
        {project.source_type === "youtube" ? (
          <Link2 className="mt-0.5 size-4 shrink-0 text-faint" aria-label="From a link" />
        ) : (
          <Upload className="mt-0.5 size-4 shrink-0 text-faint" aria-label="Uploaded" />
        )}
        <div className="min-w-0 flex-1">
          <h3 className="line-clamp-2 text-[15px] leading-snug group-hover:text-caption">{project.title}</h3>
          {working ? (
            <div className="mt-2">
              <p className="text-[13px] text-muted">{STAGE_LABELS[project.status]}…</p>
              <ProgressBar value={overallProgress(project.status, project.progress)} className="mt-2" />
            </div>
          ) : project.status === "failed" ? (
            <p className="mt-1 flex items-center gap-1.5 text-[13px] text-danger">
              <AlertCircle className="size-3.5" /> Couldn&apos;t process this video
            </p>
          ) : (
            <p className="mt-1 text-[13px] text-faint">{timeAgo(project.created_at)}</p>
          )}
        </div>
      </div>
    </Link>
  );
}
