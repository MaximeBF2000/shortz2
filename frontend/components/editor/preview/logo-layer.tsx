import type { LogoStyle } from "@/lib/types";

const MARGIN = 56;

/** Brand logo in a corner. Positions mirror backend/app/render/video.py. */
export function LogoLayer({ url, style }: { url: string | null; style: LogoStyle }) {
  if (!style.enabled || !url) return null;
  const [vertical, horizontal] = style.corner.split("-");
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={url}
      alt=""
      className="absolute"
      style={{
        width: style.size,
        opacity: style.opacity,
        [horizontal]: MARGIN,
        [vertical]: MARGIN + 40,
      }}
    />
  );
}
