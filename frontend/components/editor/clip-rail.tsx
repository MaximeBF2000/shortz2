import Link from "next/link";
import clsx from "clsx";

import { ScoreBadge } from "@/components/ui/score-badge";
import { formatDuration } from "@/lib/format";
import type { Project } from "@/lib/types";

/** All clips of the project, to hop between them without leaving the editor. */
export function ClipRail({ project, activeId }: { project: Project; activeId: string }) {
  return (
    <nav aria-label="Clips" className="hidden min-h-0 overflow-y-auto border-r border-line p-3 lg:block">
      <ul className="space-y-2">
        {project.clips.map((clip) => (
          <li key={clip.id}>
            <Link
              href={`/projects/${project.id}/clips/${clip.id}`}
              aria-current={clip.id === activeId ? "page" : undefined}
              className={clsx(
                "flex gap-3 rounded-xl p-2 transition-colors",
                clip.id === activeId ? "bg-raise" : "hover:bg-panel",
              )}
            >
              <div className="relative aspect-[9/16] w-12 shrink-0 overflow-hidden rounded-lg bg-raise">
                {clip.thumbnail_url && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={clip.thumbnail_url} alt="" className="size-full object-cover" />
                )}
              </div>
              <div className="min-w-0 py-0.5">
                <ScoreBadge score={clip.score} className="!h-5 !min-w-7 !text-[15px]" />
                <p className="mt-1.5 line-clamp-2 text-[12px] leading-snug">{clip.title}</p>
                <p className="tabular mt-0.5 text-[11px] text-faint">{formatDuration(clip.end - clip.start)}</p>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
