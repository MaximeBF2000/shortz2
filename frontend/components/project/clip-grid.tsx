import type { Project } from "@/lib/types";

import { ClipCard } from "./clip-card";

export function ClipGrid({ project }: { project: Project }) {
  return (
    <section>
      <div className="grid grid-cols-2 gap-x-4 gap-y-10 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        {project.clips.map((clip, index) => (
          <ClipCard key={clip.id} clip={clip} index={index} />
        ))}
      </div>
    </section>
  );
}
