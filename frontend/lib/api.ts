/** Thin wrappers around the Shortz API. */

import { API_URL } from "./config";
import type {
  BrandKit,
  CaptionFont,
  CaptionPreset,
  Clip,
  ClipChanges,
  ClipStyle,
  Project,
  ProjectSettings,
  ProjectSummary,
  TranscriptWord,
} from "./types";

export class ApiError extends Error {}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: init?.body instanceof FormData ? init.headers : { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new ApiError("Can't reach the Shortz server. Is the backend running?");
  }
  if (!response.ok) {
    throw new ApiError(await errorMessage(response));
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

async function errorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) return body.detail[0]?.msg ?? "Invalid request.";
  } catch {}
  return `Request failed (${response.status}).`;
}

/** SWR fetcher: keys are API paths. */
export const fetcher = <T>(path: string) => request<T>(path);

export const api = {
  listProjects: () => request<ProjectSummary[]>("/api/projects"),
  getProject: (id: string) => request<Project>(`/api/projects/${id}`),
  getTranscript: (id: string) => request<{ words: TranscriptWord[] }>(`/api/projects/${id}/transcript`),
  createFromUrl: (url: string, settings: ProjectSettings) =>
    request<Project>("/api/projects", { method: "POST", body: JSON.stringify({ url, settings }) }),
  retryProject: (id: string) => request<Project>(`/api/projects/${id}/retry`, { method: "POST" }),
  renderAll: (id: string) => request<Project>(`/api/projects/${id}/render-all`, { method: "POST" }),
  deleteProject: (id: string) => request<void>(`/api/projects/${id}`, { method: "DELETE" }),

  updateClip: (id: string, changes: ClipChanges) =>
    request<Clip>(`/api/clips/${id}`, { method: "PATCH", body: JSON.stringify(changes) }),
  renderClip: (id: string) => request<Clip>(`/api/clips/${id}/render`, { method: "POST" }),
  deleteClip: (id: string) => request<void>(`/api/clips/${id}`, { method: "DELETE" }),
  downloadUrl: (id: string) => `${API_URL}/api/clips/${id}/download`,

  listBrandKits: () => request<BrandKit[]>("/api/brand-kits"),
  createBrandKit: (name: string, style: ClipStyle) =>
    request<BrandKit>("/api/brand-kits", { method: "POST", body: JSON.stringify({ name, style }) }),
  updateBrandKit: (id: string, changes: { name?: string; style?: ClipStyle; is_default?: boolean }) =>
    request<BrandKit>(`/api/brand-kits/${id}`, { method: "PATCH", body: JSON.stringify(changes) }),
  deleteBrandKit: (id: string) => request<void>(`/api/brand-kits/${id}`, { method: "DELETE" }),
  uploadLogo: (id: string, file: File) => {
    const body = new FormData();
    body.append("file", file);
    return request<BrandKit>(`/api/brand-kits/${id}/logo`, { method: "POST", body });
  },
  deleteLogo: (id: string) => request<BrandKit>(`/api/brand-kits/${id}/logo`, { method: "DELETE" }),

  listFonts: () => request<CaptionFont[]>("/api/fonts"),
  listPresets: () => request<CaptionPreset[]>("/api/presets"),
};

/** Upload a video with progress (fetch can't report upload progress, XHR can). */
export function uploadVideo(
  file: File,
  settings: ProjectSettings,
  onProgress: (fraction: number) => void,
): Promise<Project> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const body = new FormData();
    body.append("file", file);
    body.append("settings", JSON.stringify(settings));
    xhr.open("POST", `${API_URL}/api/projects/upload`);
    xhr.upload.onprogress = (event) => event.lengthComputable && onProgress(event.loaded / event.total);
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) return resolve(JSON.parse(xhr.responseText));
      let message = `Upload failed (${xhr.status}).`;
      try {
        message = JSON.parse(xhr.responseText).detail ?? message;
      } catch {}
      reject(new ApiError(message));
    };
    xhr.onerror = () => reject(new ApiError("Can't reach the Shortz server. Is the backend running?"));
    xhr.send(body);
  });
}
