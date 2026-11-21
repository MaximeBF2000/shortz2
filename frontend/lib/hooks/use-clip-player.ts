"use client";

import { useCallback, useEffect, useState } from "react";

import { seekVideo, setPlaybackRate, togglePlayback } from "../video";

/**
 * Plays the source video only between `start` and `end`, looping.
 * Exposes the current time at animation-frame rate, for captions.
 */
export function useClipPlayer(video: HTMLVideoElement | null, start: number, end: number) {
  const [time, setTime] = useState(start);
  const [playing, setPlaying] = useState(false);
  const [rate, setRate] = useState(1);

  useEffect(() => {
    if (video) setPlaybackRate(video, rate);
  }, [video, rate]);

  // Jump to the clip when it (or its trim) changes.
  useEffect(() => {
    if (!video) return;
    const jump = () => {
      if (video.currentTime < start || video.currentTime > end) seekVideo(video, start);
      setTime(video.currentTime);
    };
    if (video.readyState >= 1) jump();
    else video.addEventListener("loadedmetadata", jump, { once: true });
  }, [video, start, end]);

  useEffect(() => {
    if (!video) return;
    let frame = 0;
    const tick = () => {
      if (!video.paused && video.currentTime >= end) {
        seekVideo(video, start); // loop
      }
      setTime(video.currentTime);
      frame = requestAnimationFrame(tick);
    };
    const onPlay = () => setPlaying(true);
    const onPause = () => setPlaying(false);
    video.addEventListener("play", onPlay);
    video.addEventListener("pause", onPause);
    frame = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(frame);
      video.removeEventListener("play", onPlay);
      video.removeEventListener("pause", onPause);
    };
  }, [video, start, end]);

  // Stop audio when leaving the page.
  useEffect(() => () => video?.pause(), [video]);

  const toggle = useCallback(() => {
    if (video) togglePlayback(video);
  }, [video]);

  const seek = useCallback(
    (t: number) => {
      if (!video) return;
      seekVideo(video, Math.min(Math.max(t, start), end - 0.05));
      setTime(video.currentTime);
    },
    [video, start, end],
  );

  return { time, playing, toggle, seek, rate, setRate };
}

export type ClipPlayer = ReturnType<typeof useClipPlayer>;
