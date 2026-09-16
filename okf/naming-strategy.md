---
type: Reference
title: Text file naming strategy
---

# Text file naming strategy

Survey and recommendation for edition filenames in the Christian Texts corpus (and the OKF mirror).

## Survey (before rename)

| Pattern | Works | Notes |
| --- | --- | --- |
| Sole `original.md` + `original.json` | 12 | Creeds, most confessions/catechisms, Charleston, Abstract, Hulse |
| Multi: `original-1680.*` + `modern-english.*` | 1 | Collins *An Orthodox Catechism* |

No `.yaml` siblings today. Frontmatter `edition` already carries the human label (`original`, `modern English`, `Chapel Library`, etc.).

Problem: for a sole text, the filename `original` is redundant and often inaccurate (e.g. Chapel Library booklet, SBTS official text, 1646 second impression).

## Options

### A — Always slugify `edition`

Every file named from frontmatter (`original.md`, `chapel-library.md`, …).

- Pro: Filename mirrors metadata.
- Con: Sole works with `edition: original` still get `original.md` — does not fix Zach’s complaint.

### B — `text` when sole; edition slug when multiple (recommended)

- **One edition** in the work folder → `text.md` / `text.json` (the text for that work).
- **Two or more editions** → kebab-case stems that identify the version; never bare `original`.
  - Collins: `1680.md` / `1680.json` and `modern-english.md` / `modern-english.json`.
- Frontmatter `edition` stays the human-readable label (unchanged).

- Pro: Sole texts read as “the text”; multi-edition folders stay disambiguated; drops `original` from the filename vocabulary.
- Con: Adding a second edition later requires renaming `text.*` → a year slug (one-time cost; decided).

### C — Repeat work slug as filename

e.g. `texts/apostles-creed/apostles-creed.md`.

- Pro: Globally unique stems.
- Con: Redundant with the directory; awkward once a second edition appears.

## Decision

**Use B.** Applied to the checkout and the OKF bundle in `okf/`.

**When a sole-edition work later gains a second edition:** rename existing `text.*` to a **year** slug (e.g. `1689.md` / `1689.json`), not a wording label. The new edition gets its own distinctive stem. Frontmatter `edition` remains the human-readable label.
