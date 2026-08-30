# Christian Texts

Markdown sources for public-domain Christian texts. This repository is a corpus, not an app.

Each work lives in its own directory under `texts/`. The text file itself carries YAML frontmatter:

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

- `date` is when the work was first published.
- `source` is the edition this file was taken from.
- `retrieved` is when that copy was pulled (ISO 8601).

## Texts

| Work | Author | Editions |
| --- | --- | --- |
| [An Orthodox Catechism](texts/1680-an-orthodox-catechism/) | Hercules Collins (1680) | [Original 1680](texts/1680-an-orthodox-catechism/original-1680.md) · [Modern English](texts/1680-an-orthodox-catechism/modern-english.md) |

## Layout

```
texts/
  1680-an-orthodox-catechism/
    README.md
    original-1680.md
    modern-english.md
```

## Source

Collins is present in both the 1680 wording (152 questions, plus preface, creeds, and the singing appendix) and a modern-English recension (148 questions) from the Commonplace vault / 1689.com. The 1680 scan is on [Internet Archive](https://archive.org/details/bim_early-english-books-1641-1700_an-orthodox-catechism-_collins-hercules_1680).

## License

The historical catechism is in the public domain. Repository scaffolding is dedicated to the public domain under CC0 (see `LICENSE`).
