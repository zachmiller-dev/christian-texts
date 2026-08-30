import type { ReactNode } from "react";

export function renderMarkdown(source: string): ReactNode[] {
  return source.split(/\n\n+/).map((block, i) => {
    const trimmed = block.trim();
    if (!trimmed) return null;
    if (/^\d+\./.test(trimmed) || trimmed.startsWith("I.") || trimmed.startsWith("*Arg.")) {
      return (
        <p key={i} className="my-4">
          {inline(trimmed)}
        </p>
      );
    }
    return (
      <p key={i} className="my-4">
        {inline(trimmed)}
      </p>
    );
  });
}

function inline(text: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  const re = /(\*[^*]+\*|_[^_]+_)/g;
  let last = 0;
  let match: RegExpExecArray | null;
  let k = 0;
  while ((match = re.exec(text))) {
    if (match.index > last) {
      nodes.push(text.slice(last, match.index));
    }
    const raw = match[0];
    nodes.push(
      <em key={k++}>{raw.slice(1, -1)}</em>,
    );
    last = match.index + raw.length;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}
