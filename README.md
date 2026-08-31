# Christian Texts

Markdown and JSON sources for public-domain Christian texts. This repository is a corpus, not an app.

- **Markdown** is for reading (agents and people).
- **JSON** uses the Creeds.json shape (`Metadata` + `Data`) for structured lookup.

Each text file has YAML frontmatter:

```yaml
---
title: An Orthodox Catechism
author: Hercules Collins
date: 1680
edition: modern English
source: https://1689.com/an-orthodox-catechism
retrieved: 2026-04-19
---
```

- `date` — first publication
- `source` — edition this file was taken from
- `retrieved` — when that copy was pulled (ISO 8601)

## Treatises

Some works (handbooks, discipline manuals) keep Scripture proofs **inline** in the prose instead of in separate `*Proofs:*` lists. Confessions and catechisms use `*Proofs:*` blocks; treatises do not.

**Citations**

- Place one or more references after the clause they support, comma-separated, then the sentence period: `… in diverse circumstances, Acts 7:38, Ephesians 3:21.`
- Use canonical **full book names** (`2 Timothy`, `Song of Solomon`, `Psalms`), not abbreviations (`2 Tim.`, `Eph.`).
- Verse ranges use an en-dash: `15:1–3`.
- Same-book continuation: `Matthew 28:19, 20`.
- Cross-book: `1 Corinthians 12:28, Ephesians 4:11`.
- Chapter-only: `Revelation 2 and 3`.
- Do not italicize citations. Italicize **quotations** and titles.

**Structure**

- Numbered section heads from the original (`1.`, `2.`, …) become `**1.**`, `**2.**`, … so JSON sections split correctly.
- Duty and case enumerations (`(1) … (2) …`) become markdown ordered lists when they enumerate distinct items.
- Gill quotations and similar attributions stay in `"` with attribution.

## Texts

| Work | Files |
| --- | --- |
| [Apostles' Creed](texts/apostles-creed/) | [md](texts/apostles-creed/original.md) · [json](texts/apostles-creed/original.json) |
| [Nicene Creed](texts/nicene-creed/) | [md](texts/nicene-creed/original.md) · [json](texts/nicene-creed/original.json) |
| [Athanasian Creed](texts/athanasian-creed/) | [md](texts/athanasian-creed/original.md) · [json](texts/athanasian-creed/original.json) |
| [Chalcedonian Definition](texts/chalcedonian-definition/) | [md](texts/chalcedonian-definition/original.md) · [json](texts/chalcedonian-definition/original.json) |
| [Canons of Dort](texts/canons-of-dort/) (1619) | [md](texts/canons-of-dort/original.md) · [json](texts/canons-of-dort/original.json) |
| [Savoy Declaration](texts/1658-savoy-declaration/) (1658) | [md](texts/1658-savoy-declaration/original.md) · [json](texts/1658-savoy-declaration/original.json) |
| [First London Confession](texts/1646-first-london/) (1646) | [md](texts/1646-first-london/original.md) · [json](texts/1646-first-london/original.json) |
| [Second London Confession](texts/1689-london-baptist-confession/) (1677/1689) | [md](texts/1689-london-baptist-confession/original.md) · [json](texts/1689-london-baptist-confession/original.json) |
| [An Orthodox Catechism](texts/1680-an-orthodox-catechism/) (Collins, 1680) | [original md](texts/1680-an-orthodox-catechism/original-1680.md) · [original json](texts/1680-an-orthodox-catechism/original-1680.json) · [modern md](texts/1680-an-orthodox-catechism/modern-english.md) · [modern json](texts/1680-an-orthodox-catechism/modern-english.json) |
| [Baptist Catechism](texts/1693-baptist-catechism/) (Keach / Collins, 1693) | [md](texts/1693-baptist-catechism/original.md) · [json](texts/1693-baptist-catechism/original.json) |
| [Abstract of Principles](texts/abstract-of-principles/) (1858) | [md](texts/abstract-of-principles/original.md) · [json](texts/abstract-of-principles/original.json) |
| [Charleston Summary of Church Discipline](texts/1774-charleston-church-discipline/) (1774) | [md](texts/1774-charleston-church-discipline/original.md) · [json](texts/1774-charleston-church-discipline/original.json) |

The 1644 First London Confession is not included (1646 only).

## Stan Reeves modern 1689

Not in this repo. Reeves’s modern English is copyrighted. Print copies for church use are allowed; posting on the internet is not. See [Founders](https://founders.org/library-book/1689-confession/) and [reeveshome.org/modern1689](https://reeveshome.org/modern1689/1689_modern.pdf).

## License

Historical texts here are in the public domain (or CC0 TCP for Savoy). Repository scaffolding is CC0 (see `LICENSE`).
