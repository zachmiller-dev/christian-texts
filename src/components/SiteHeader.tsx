import Link from "next/link";
import { catechism } from "@/lib/catechism";

const links = [
  { href: "/", label: "Catechism" },
  { href: "/preface", label: "Preface" },
  { href: "/creeds", label: "Creeds" },
  { href: "/appendix", label: "Appendix" },
];

export function SiteHeader({ current }: { current?: string }) {
  return (
    <header className="border-b border-[var(--rule)] bg-[var(--paper)]/90 backdrop-blur">
      <div className="mx-auto flex max-w-5xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-end sm:justify-between sm:px-6">
        <Link href="/" className="group">
          <p className="font-sans text-[11px] uppercase tracking-[0.22em] text-[var(--muted)]">
            Christian Texts
          </p>
          <h1 className="font-serif text-xl leading-tight text-[var(--ink)] group-hover:underline sm:text-2xl">
            {catechism.title}
          </h1>
        </Link>
        <nav className="flex flex-wrap gap-x-4 gap-y-1 font-sans text-sm">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={
                current === link.href
                  ? "text-[var(--ink)] underline decoration-[var(--rule)] underline-offset-4"
                  : "text-[var(--muted)] hover:text-[var(--ink)]"
              }
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
