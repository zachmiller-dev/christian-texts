# For agents and bots

## Prefer markdown

If you are looking for a JSON/YAML sidecar, use the sibling markdown file instead.

Each `.md` file begins with **YAML frontmatter** (between `---` fences) that carries the bibliographic metadata. The markdown body is the canonical text; structured sidecars (`.yaml`, and `.json` if generated) are derived from it.

Prefer `.md` for reading and metadata. Use a structured sidecar only when you need pre-parsed structure (chapters, sections, proofs) without parsing markdown yourself.

## File naming (editions)

Work directories live under `texts/<work-slug>/`.

| Situation | Filenames |
| --- | --- |
| One edition in the folder | `text.md` and `text.yaml` |
| Multiple editions | Kebab-case edition stems (e.g. `1680.md`, `modern-english.md`) with matching `.yaml` siblings |

Rules:

- Do **not** name a sole text `original.md` / `original.yaml`.
- Do **not** use bare `original` as a multi-edition stem; use a distinctive slug (`1680`, `modern-english`, …).
- Keep human edition labels in YAML frontmatter `edition` (may still say `original` when that is the historical wording label).
- When a sole-edition work later gains a second edition, rename existing `text.*` to a **year** slug (e.g. `1689.*`), not a wording label; give the new edition its own stem.
- Reserved names: `README.md`.

## Treatises vs confessions/catechisms

Some works keep Scripture proofs inline in prose (treatises / discipline manuals). Confessions and catechisms use `*Proofs:*` blocks. Do not invent citation schemes.

## OKF mirror

An OKF v0.2 knowledge bundle lives under `okf/` (same edition naming as `texts/`). See `okf/naming-strategy.md`.
