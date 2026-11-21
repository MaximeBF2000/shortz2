"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { mutate } from "swr";

import { Button } from "@/components/ui/button";
import { ProgressBar } from "@/components/ui/progress-bar";
import { api, uploadVideo } from "@/lib/api";
import type { ProjectSettings } from "@/lib/types";

import { ProjectOptions } from "./project-options";
import { SourceInput } from "./source-input";

const DEFAULT_SETTINGS: ProjectSettings = {
  clip_length: "auto",
  max_clips: 8,
  language: null,
  focus: "",
  brand_kit_id: null,
  smart_crop: true,
};

export function NewProjectForm() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const ready = file !== null || url.trim().length > 0;

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!ready) return;
    setSubmitting(true);
    try {
      const project = file
        ? await uploadVideo(file, settings, setUploadProgress)
        : await api.createFromUrl(url.trim(), settings);
      await mutate("/api/projects");
      router.push(`/projects/${project.id}`);
    } catch (error) {
      toast.error((error as Error).message);
      setSubmitting(false);
      setUploadProgress(null);
    }
  }

  return (
    <form onSubmit={submit} className="rounded-3xl border border-line bg-panel p-3 sm:p-4">
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="flex-1">
          <SourceInput url={url} file={file} onUrlChange={setUrl} onFileChange={setFile} />
        </div>
        <Button type="submit" variant="primary" size="lg" disabled={!ready || submitting} className="h-16 rounded-2xl px-8 text-base">
          {submitting ? (uploadProgress !== null ? `Uploading ${Math.round(uploadProgress * 100)}%` : "Starting…") : "Find clips"}
        </Button>
      </div>
      {uploadProgress !== null && <ProgressBar value={uploadProgress} className="mx-1 mt-3" />}
      <div className="px-1 pt-5 pb-1">
        <ProjectOptions settings={settings} onChange={setSettings} />
      </div>
    </form>
  );
}
