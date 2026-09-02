# Christian Texts

Markdown and YAML sources for public-domain Christian texts. This repository is a corpus, not an app.

- **Markdown** is for reading (agents and people).
- **YAML** uses the Creeds.json shape (`Metadata` + `Data`) for structured lookup.

> **Agents/bots:** looking for the JSON? Use the YAML frontmatter in the `.md` file instead — see [`AGENTS.md`](AGENTS.md).

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

## Queryable YAML

Structured siblings use literal block scalars (`|-`) for long prose so paragraph breaks are preserved. Proofs are sibling sections under each content block, not nested keys.

```bash
# Catechism question 1 (Question, Answer, Proofs as sections)
yq '.Data[] | select(.Number == 1) | .Sections[]' texts/1693-baptist-catechism/original.yaml

# Confession section 1 content and its proofs block
yq '.Data[] | select(.Title == "Of the Holy Scriptures") | .Sections[] | select(.Section == "1" or .Section == "Proofs")' \
  texts/1689-london-baptist-confession/original.yaml
```

To export Creeds.json-compatible JSON on demand:

```bash
pip install -r requirements.txt
python scripts/export_json.py
```

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

- Numbered section heads from the original (`1.`, `2.`, …) become `**1.**`, `**2.**`, … so YAML sections split correctly.
- Duty and case enumerations (`(1) … (2) …`) become markdown ordered lists when they enumerate distinct items.
- Gill quotations and similar attributions stay in `"` with attribution.

## Texts

| Work | Files |
| --- | --- |
| [Apostles' Creed](texts/apostles-creed/) | [md](texts/apostles-creed/original.md) · [yaml](texts/apostles-creed/original.yaml) |
| [Nicene Creed](texts/nicene-creed/) | [md](texts/nicene-creed/original.md) · [yaml](texts/nicene-creed/original.yaml) |
| [Athanasian Creed](texts/athanasian-creed/) | [md](texts/athanasian-creed/original.md) · [yaml](texts/athanasian-creed/original.yaml) |
| [Chalcedonian Definition](texts/chalcedonian-definition/) | [md](texts/chalcedonian-definition/original.md) · [yaml](texts/chalcedonian-definition/original.yaml) |
| [Canons of Dort](texts/canons-of-dort/) (1619) | [md](texts/canons-of-dort/original.md) · [yaml](texts/canons-of-dort/original.yaml) |
| [Savoy Declaration](texts/1658-savoy-declaration/) (1658) | [md](texts/1658-savoy-declaration/original.md) · [yaml](texts/1658-savoy-declaration/original.yaml) |
| [First London Confession](texts/1646-first-london/) (1646) | [md](texts/1646-first-london/original.md) · [yaml](texts/1646-first-london/original.yaml) |
| [Second London Confession](texts/1689-london-baptist-confession/) (1677/1689) | [md](texts/1689-london-baptist-confession/original.md) · [yaml](texts/1689-london-baptist-confession/original.yaml) |
| [An Orthodox Catechism](texts/1680-an-orthodox-catechism/) (Collins, 1680) | [original md](texts/1680-an-orthodox-catechism/original-1680.md) · [original yaml](texts/1680-an-orthodox-catechism/original-1680.yaml) · [modern md](texts/1680-an-orthodox-catechism/modern-english.md) · [modern yaml](texts/1680-an-orthodox-catechism/modern-english.yaml) |
| [Baptist Catechism](texts/1693-baptist-catechism/) (Keach / Collins, 1693) | [md](texts/1693-baptist-catechism/original.md) · [yaml](texts/1693-baptist-catechism/original.yaml) |
| [Catechism for Boys and Girls](texts/catechism-for-boys-and-girls/) (Hulse / Chapel Library) | [md](texts/catechism-for-boys-and-girls/original.md) · [yaml](texts/catechism-for-boys-and-girls/original.yaml) |
| [Abstract of Principles](texts/abstract-of-principles/) (1858) | [md](texts/abstract-of-principles/original.md) · [yaml](texts/abstract-of-principles/original.yaml) |
| [Charleston Summary of Church Discipline](texts/1774-charleston-church-discipline/) (1774) | [md](texts/1774-charleston-church-discipline/original.md) · [yaml](texts/1774-charleston-church-discipline/original.yaml) |

The 1644 First London Confession is not included (1646 only).

## Stan Reeves modern 1689

Not in this repo. Reeves’s modern English is copyrighted. Print copies for church use are allowed; posting on the internet is not. See [Founders](https://founders.org/library-book/1689-confession/) and [reeveshome.org/modern1689](https://reeveshome.org/modern1689/1689_modern.pdf).

## License

Historical texts here are in the public domain (or CC0 TCP for Savoy). The Catechism for Boys and Girls is the Chapel Library / Errol Hulse booklet (© 1998; reproduction allowed with their notice). Repository scaffolding is CC0 (see `LICENSE`).
