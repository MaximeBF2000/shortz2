import { HeroHeadline } from "@/components/home/hero-headline";
import { NewProjectForm } from "@/components/home/new-project-form";
import { ProjectList } from "@/components/home/project-list";

export default function HomePage() {
  return (
    <main className="mx-auto max-w-7xl px-4 pb-24 sm:px-8">
      <section className="pt-8 pb-10 sm:pt-14">
        <HeroHeadline />
        <p className="mt-6 max-w-xl text-[17px] leading-relaxed text-muted">
          Paste a YouTube link or drop a file. Shortz finds the moments worth posting, keeps the speaker in frame and
          captions every word in your style.
        </p>
      </section>
      <NewProjectForm />
      <ProjectList />
    </main>
  );
}
