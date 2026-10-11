"use client";

import { Download, LoaderCircle, RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import type { Clip } from "@/lib/types";

/** Export, follow progress, then download. */
export function ExportButton({ clip, onExport }: { clip: Clip; onExport: () => void }) {
  const status = clip.render_status;

  if (status === "queued" || status === "rendering") {
    const progress = Math.round(clip.render_progress * 100);
    return (
      <Button variant="secondary" disabled className="relative overflow-hidden !opacity-100">
        <span className="absolute inset-y-0 left-0 bg-caption/20 transition-[width]" style={{ width: `${progress}%` }} />
        <LoaderCircle className="relative size-4 animate-spin" />
        <span className="tabular relative">{status === "queued" ? "Queued" : `Exporting ${progress}%`}</span>
      </Button>
    );
  }

  if (status === "done" && clip.output_url) {
    return (
      <a href={api.downloadUrl(clip.id)}>
        <Button variant="primary" tabIndex={-1}>
          <Download className="size-4" /> Download
        </Button>
      </a>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {status === "failed" && (
        <span className="hidden max-w-48 truncate text-[13px] text-danger md:block" title={clip.render_error ?? ""}>
          Export failed
        </span>
      )}
      <Button variant="primary" onClick={onExport}>
        {clip.output_url || status === "failed" ? <RotateCcw className="size-4" /> : <Download className="size-4" />}
        {status === "failed" ? "Try again" : clip.output_url ? "Export changes" : "Export"}
      </Button>
    </div>
  );
}
