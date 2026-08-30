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

| Work | Author | Edition |
| --- | --- | --- |
| [An Orthodox Catechism](texts/1680-an-orthodox-catechism/) | Hercules Collins (1680) | Modern English (1689.com), from the Commonplace vault |

## Layout

```
texts/
  1680-an-orthodox-catechism/
    README.md
    BOOK.md
```

## Source

The Collins note in Commonplace (`An Orthodox Catechism (Collins 1680).md`) is a modern-English recension, 148 questions, ingested from 1689.com. The 1680 original (152 questions) is on [Internet Archive](https://archive.org/details/bim_early-english-books-1641-1700_an-orthodox-catechism-_collins-hercules_1680).

## License

The historical catechism is in the public domain. Repository scaffolding is dedicated to the public domain under CC0 (see `LICENSE`).
