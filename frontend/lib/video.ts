/** Imperative helpers for the (hidden) source <video> element. */

export function seekVideo(video: HTMLVideoElement, time: number) {
  video.currentTime = time;
}

export function togglePlayback(video: HTMLVideoElement) {
  if (video.paused) void video.play();
  else video.pause();
}
