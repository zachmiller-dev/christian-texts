import type { Metadata } from "next";
import { SiteHeader } from "@/components/SiteHeader";
import { catechism } from "@/lib/catechism";
import { renderMarkdown } from "@/lib/markdown";

export const metadata: Metadata = { title: "The Creeds" };

export default function CreedsPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader current="/creeds" />
      <article className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
        <h1 className="font-serif text-3xl sm:text-4xl">The Creeds</h1>
        <p className="mt-4 font-serif text-[var(--muted)]">
          Collins placed the Nicene Creed and Athanasius his Creed before the
          church, with the Apostles’ Creed opened through the body of the
          catechism.
        </p>
        <h2 className="mt-12 font-serif text-2xl">{catechism.niceneTitle}</h2>
        <div className="mt-4 font-serif text-lg leading-[1.8]">
          {renderMarkdown(catechism.nicene)}
        </div>
        <h2 className="mt-12 font-serif text-2xl">{catechism.athanasianTitle}</h2>
        <div className="mt-4 font-serif text-lg leading-[1.8]">
          {renderMarkdown(catechism.athanasian)}
        </div>
      </article>
    </div>
  );
}
