import Link from "next/link";
import { SearchBox } from "@/components/SearchBox";
import { SiteHeader } from "@/components/SiteHeader";
import { catechism, questionsBySection } from "@/lib/catechism";

export default function HomePage() {
  const groups = questionsBySection();

  return (
    <div className="min-h-screen">
      <SiteHeader current="/" />
      <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <p className="max-w-2xl font-serif text-lg leading-relaxed text-[var(--muted)] sm:text-xl">
          {catechism.subtitle}. Written by {catechism.author} for the baptized
          church meeting in Old Gravel Lane, {catechism.place}, {catechism.year}.
        </p>
        <p className="mt-4 max-w-2xl font-sans text-sm leading-relaxed text-[var(--muted)]">
          A Particular Baptist recension of the Heidelberg Catechism, published
          the year after the Second London Confession. One hundred fifty-two
          questions, with Collins’s preface, the Nicene and Athanasian creeds,
          and his appendix on singing.
        </p>
        <div className="mt-8 max-w-xl">
          <SearchBox questions={catechism.questions} />
        </div>

        <div className="mt-12 grid gap-10 lg:grid-cols-[14rem_1fr]">
          <aside className="hidden lg:block">
            <p className="font-sans text-[11px] uppercase tracking-[0.2em] text-[var(--muted)]">
              Parts
            </p>
            <ul className="mt-3 space-y-2 font-sans text-sm">
              {groups.map((group) => (
                <li key={group.title}>
                  <a
                    href={`#section-${slug(group.title)}`}
                    className="text-[var(--muted)] hover:text-[var(--ink)]"
                  >
                    {group.title}
                  </a>
                </li>
              ))}
            </ul>
          </aside>

          <div className="space-y-12">
            {groups.map((group) => (
              <section key={group.title} id={`section-${slug(group.title)}`}>
                <h2 className="font-serif text-2xl text-[var(--accent)]">
                  {group.title}
                </h2>
                <ol className="mt-4 divide-y divide-[var(--rule)] border-y border-[var(--rule)]">
                  {group.questions.map((q) => (
                    <li key={q.id} id={`q-${q.id}`}>
                      <Link
                        href={`/q/${q.id}`}
                        className="flex gap-4 py-3 hover:bg-[var(--paper-2)]"
                      >
                        <span className="w-10 shrink-0 font-sans text-sm text-[var(--muted)]">
                          {q.id}
                        </span>
                        <span className="font-serif leading-snug">{q.question}</span>
                      </Link>
                    </li>
                  ))}
                </ol>
              </section>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

function slug(title: string) {
  return title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}
