/** Imperative helpers for the (hidden) source <video> element. */

export function seekVideo(video: HTMLVideoElement, time: number) {
  video.currentTime = time;
}

export function togglePlayback(video: HTMLVideoElement) {
  if (video.paused) void video.play();
  else video.pause();
}

export function setPlaybackRate(video: HTMLVideoElement, rate: number) {
  video.playbackRate = rate;
}

/**
 * Seeks as fast as the browser can show frames while the user drags along the
 * timeline: a new seek only starts once the previous one has landed, so frames
 * keep coming instead of a queue of seeks piling up.
 */
export function startScrubbing(video: HTMLVideoElement) {
  const wasPlaying = !video.paused;
  video.pause();
  let pending: number | null = null;

  const go = (time: number) => {
    // fastSeek (Safari, Firefox) jumps to the nearest keyframe: much quicker while dragging.
    if (typeof video.fastSeek === "function") video.fastSeek(time);
    else video.currentTime = time;
  };
  const onSeeked = () => {
    if (pending === null) return;
    const time = pending;
    pending = null;
    go(time);
  };
  video.addEventListener("seeked", onSeeked);

  return {
    to(time: number) {
      if (video.seeking) pending = time;
      else go(time);
    },
    /** Land exactly on the final frame and resume playback if it was playing. */
    end(time: number) {
      video.removeEventListener("seeked", onSeeked);
      video.currentTime = time;
      if (wasPlaying) void video.play();
    },
  };
}

export type Scrubber = ReturnType<typeof startScrubbing>;
