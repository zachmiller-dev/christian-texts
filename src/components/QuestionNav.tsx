import Link from "next/link";
import type { Question } from "@/lib/catechism";

export function QuestionNav({ question }: { question: Question }) {
  return (
    <div className="mt-10 flex items-center justify-between gap-4 border-t border-[var(--rule)] pt-6 font-sans text-sm">
      {question.prev ? (
        <Link
          href={`/q/${question.prev}`}
          className="text-[var(--muted)] hover:text-[var(--ink)]"
        >
          ← Question {question.prev}
        </Link>
      ) : (
        <span />
      )}
      <Link href={`/#q-${question.id}`} className="text-[var(--muted)] hover:text-[var(--ink)]">
        Contents
      </Link>
      {question.next ? (
        <Link
          href={`/q/${question.next}`}
          className="text-[var(--muted)] hover:text-[var(--ink)]"
        >
          Question {question.next} →
        </Link>
      ) : (
        <span />
      )}
    </div>
  );
}
