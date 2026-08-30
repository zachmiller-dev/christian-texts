import type { Metadata } from "next";
import { SiteHeader } from "@/components/SiteHeader";
import { catechism } from "@/lib/catechism";
import { renderMarkdown } from "@/lib/markdown";

export const metadata: Metadata = { title: catechism.appendixTitle };

export default function AppendixPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader current="/appendix" />
      <article className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
        <h1 className="font-serif text-3xl leading-snug sm:text-4xl">
          {catechism.appendixTitle}
        </h1>
        <div className="mt-8 font-serif text-lg leading-[1.8]">
          {renderMarkdown(catechism.appendix)}
        </div>
      </article>
    </div>
  );
}
