# Christian Texts

Markdown sources for public-domain Christian texts. This repository is a corpus, not an app.

Each work lives in its own directory under `texts/`. Add another text by creating a folder and a short `README.md` that names the author, title, date, and edition used.

## Texts

| Work | Author | Year |
| --- | --- | --- |
| [An Orthodox Catechism](texts/1680-an-orthodox-catechism/) | Hercules Collins | 1680 |

## Layout

```
texts/
  1680-an-orthodox-catechism/
    README.md
    BOOK.md
    preface.md
    questions/
    …
```

`BOOK.md` is the whole work in one file. Longer works may also split into parts.

## Source

Collins (1680) is public domain. The files here follow the original London edition (spelling and proofs of 1680, not the 2014 modernization), compiled from the SVRBC `aoc1680` transcription of that edition.

The Obsidian Commonplace vault at `/Users/zachmiller/Library/Mobile Documents/iCloud~md~obsidian/Documents/Commonplace` is the intended local source for further texts. That path is not available in this cloud environment. When a vault note should replace a file here, copy it into the matching `texts/` directory.

## License

The historical texts are in the public domain. Repository scaffolding is dedicated to the public domain under CC0 (see `LICENSE`).
