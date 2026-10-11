"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import useSWR from "swr";
import { toast } from "sonner";

import { api, fetcher } from "../api";
import { useLatest } from "./use-latest";
import type { Clip, ClipChanges } from "../types";

const SAVE_DELAY = 500;

/**
 * Loads a clip and lets the editor change it.
 *
 * Changes are applied locally right away (`clip` already includes them) and
 * saved to the API shortly after the user stops editing.
 */
export function useClipEditor(clipId: string) {
  const { data: saved, mutate } = useSWR<Clip>(`/api/clips/${clipId}`, fetcher, {
    // Keep polling while the server is working on the clip.
    refreshInterval: (clip) => (clip && ["queued", "rendering"].includes(clip.render_status) ? 1500 : 4000),
  });
  const [pending, setPending] = useState<ClipChanges>({});
  const [saving, setSaving] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);
  const pendingRef = useLatest(pending);

  const save = useCallback(async () => {
    const changes = pendingRef.current;
    if (!Object.keys(changes).length) return;
    setSaving(true);
    try {
      const updated = await api.updateClip(clipId, changes);
      await mutate(updated, { revalidate: false });
      // Drop the changes that were saved, unless the user changed them again meanwhile.
      setPending((current) => {
        const next = { ...current };
        for (const key of Object.keys(changes) as (keyof ClipChanges)[]) {
          if (next[key] === changes[key]) delete next[key];
        }
        return next;
      });
    } catch (error) {
      toast.error((error as Error).message);
      setPending({});
    } finally {
      setSaving(false);
    }
  }, [clipId, mutate, pendingRef]);

  const update = useCallback(
    (changes: ClipChanges) => {
      setPending((current) => ({ ...current, ...changes }));
      clearTimeout(timer.current);
      timer.current = setTimeout(save, SAVE_DELAY);
    },
    [save],
  );

  // Save on leave.
  useEffect(() => () => {
    clearTimeout(timer.current);
    void save();
  }, [save]);

  const exportClip = useCallback(async () => {
    clearTimeout(timer.current);
    await save();
    try {
      await mutate(await api.renderClip(clipId), { revalidate: false });
    } catch (error) {
      toast.error((error as Error).message);
    }
  }, [clipId, mutate, save]);

  const clip = saved ? applyChanges(saved, pending) : undefined;
  const dirty = Object.keys(pending).length > 0;
  return { clip, update, exportClip, saving: saving || dirty };
}

function applyChanges(clip: Clip, changes: ClipChanges): Clip {
  const { framing_mode, manual_x, ...rest } = changes;
  return {
    ...clip,
    ...rest,
    framing: {
      ...clip.framing,
      ...(framing_mode !== undefined && { mode: framing_mode }),
      ...(manual_x !== undefined && { manual_x }),
    },
  };
}
