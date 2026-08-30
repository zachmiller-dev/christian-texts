import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { QuestionNav } from "@/components/QuestionNav";
import { SiteHeader } from "@/components/SiteHeader";
import { catechism, getQuestion } from "@/lib/catechism";

type Props = { params: Promise<{ id: string }> };

export function generateStaticParams() {
  return catechism.questions.map((q) => ({ id: q.id }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const q = getQuestion(id);
  if (!q) return { title: "Question not found" };
  return { title: `Q. ${q.id}. ${q.question}` };
}

export default async function QuestionPage({ params }: Props) {
  const { id } = await params;
  const q = getQuestion(id);
  if (!q) notFound();

  return (
    <div className="min-h-screen">
      <SiteHeader current="/" />
      <main className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
        <p className="font-sans text-[11px] uppercase tracking-[0.2em] text-[var(--muted)]">
          {q.section}
          {q.heidelberg.length > 0
            ? ` · Heidelberg ${q.heidelberg.join(", ")}`
            : ""}
        </p>
        <p className="mt-3 font-sans text-sm text-[var(--muted)]">Question {q.id}</p>
        <h1 className="mt-1 font-serif text-3xl leading-snug sm:text-4xl">
          {q.question}
        </h1>
        <p className="mt-8 font-serif text-lg leading-[1.75]">{q.answer}</p>
        {q.proofs.length > 0 ? (
          <section className="mt-10">
            <h2 className="font-sans text-[11px] uppercase tracking-[0.2em] text-[var(--muted)]">
              Scripture proofs
            </h2>
            <ol className="mt-3 space-y-1 font-sans text-sm text-[var(--muted)]">
              {q.proofs.map((proof, i) => (
                <li key={i}>
                  <span className="mr-2 text-[var(--ink)]">{i + 1}.</span>
                  {proof}
                </li>
              ))}
            </ol>
          </section>
        ) : null}
        <QuestionNav question={q} />
      </main>
    </div>
  );
}
