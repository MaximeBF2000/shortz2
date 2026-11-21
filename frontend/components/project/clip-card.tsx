import Link from "next/link";
import { Download } from "lucide-react";

import { ScoreBadge } from "@/components/ui/score-badge";
import { api } from "@/lib/api";
import { formatDuration } from "@/lib/format";
import type { Clip } from "@/lib/types";

export function ClipCard({ clip, index }: { clip: Clip; index: number }) {
  const exporting = clip.render_status === "queued" || clip.render_status === "rendering";

  return (
    <article className="animate-rise group" style={{ animationDelay: `${index * 60}ms` }}>
      <Link
        href={`/projects/${clip.project_id}/clips/${clip.id}`}
        className="relative block aspect-[9/16] overflow-hidden rounded-[22px] bg-raise ring-caption transition group-hover:ring-2"
      >
        {clip.thumbnail_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={clip.thumbnail_url} alt="" className="size-full object-cover" />
        )}
        <ScoreBadge score={clip.score} className="absolute top-3 left-3" />
        <span className="tabular absolute top-3 right-3 rounded-md bg-black/60 px-1.5 py-0.5 text-[12px]">
          {formatDuration(clip.end - clip.start)}
        </span>
        {exporting && (
          <div className="absolute inset-x-3 top-12 rounded-lg bg-black/70 px-2.5 py-1.5 text-[12px]">
            Exporting {Math.round(clip.render_progress * 100)}%
          </div>
        )}
      </Link>
      <div className="mt-3 flex items-start gap-2">
        <div className="min-w-0 flex-1">
          <h3 className="line-clamp-2 text-[14px] leading-snug">{clip.title}</h3>
          <p className="mt-1 line-clamp-2 text-[12px] leading-snug text-faint">{clip.reason}</p>
        </div>
        {clip.output_url && clip.render_status === "done" && (
          <a
            href={api.downloadUrl(clip.id)}
            className="grid size-8 shrink-0 place-items-center rounded-lg bg-raise text-text hover:bg-caption hover:text-caption-ink"
            aria-label={`Download ${clip.title}`}
          >
            <Download className="size-4" />
          </a>
        )}
      </div>
    </article>
  );
}
