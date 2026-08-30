"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { Question } from "@/lib/catechism";

export function SearchBox({ questions }: { questions: Question[] }) {
  const [q, setQ] = useState("");

  const hits = useMemo(() => {
    const needle = q.trim().toLowerCase();
    if (!needle) return [];
    return questions
      .filter((item) => {
        const hay = `${item.id} ${item.question} ${item.answer} ${item.section}`.toLowerCase();
        return hay.includes(needle);
      })
      .slice(0, 12);
  }, [q, questions]);

  return (
    <div className="relative">
      <label className="sr-only" htmlFor="search">
        Search the catechism
      </label>
      <input
        id="search"
        type="search"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search questions, answers, or a number…"
        className="w-full rounded-md border border-[var(--rule)] bg-[var(--paper-2)] px-3 py-2 font-sans text-sm text-[var(--ink)] outline-none ring-[var(--ink)] placeholder:text-[var(--muted)] focus:ring-2"
      />
      {q.trim() && hits.length === 0 ? (
        <p className="mt-2 font-sans text-sm text-[var(--muted)]">
          No questions match “{q.trim()}”.
        </p>
      ) : null}
      {hits.length > 0 ? (
        <ul className="absolute z-10 mt-1 max-h-80 w-full overflow-auto rounded-md border border-[var(--rule)] bg-[var(--paper)] shadow-sm">
          {hits.map((item) => (
            <li key={item.id} className="border-b border-[var(--rule)] last:border-0">
              <Link
                href={`/q/${item.id}`}
                className="block px-3 py-2 hover:bg-[var(--paper-2)]"
                onClick={() => setQ("")}
              >
                <span className="font-sans text-xs text-[var(--muted)]">Q. {item.id}</span>
                <span className="ml-2 font-serif">{item.question}</span>
              </Link>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
