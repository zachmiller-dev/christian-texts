# For agents and bots

If you are looking for the JSON sidecar (`original.json`), use the sibling markdown file (`original.md`) instead.

Each `.md` file begins with **YAML frontmatter** (between `---` fences) that carries the bibliographic metadata found in JSON `Metadata`. The markdown body is the canonical text; JSON `Data` is generated from it.

Prefer `.md` for reading and metadata. Use `.json` only when you need pre-parsed structure (chapters, sections, proofs) without parsing markdown yourself.
