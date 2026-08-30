import type { Metadata } from "next";
import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = { title: "Question not found" };

export default function NotFound() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h1 className="font-serif text-3xl">This question is not in the catechism.</h1>
        <p className="mt-4 font-serif text-lg text-[var(--muted)]">
          Collins numbered one hundred fifty-two questions. Return to the contents
          and choose another.
        </p>
        <Link href="/" className="mt-8 inline-block font-sans text-sm underline">
          Back to the catechism
        </Link>
      </main>
    </div>
  );
}
