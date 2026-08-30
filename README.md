# Christian Texts

Public-domain Christian texts in markdown, with a small reader for the first text in the collection: **An Orthodox Catechism** (London, 1680) by Hercules Collins.

Collins, pastor of the baptized congregation in Old Gravel Lane, London, recast the Heidelberg Catechism for Particular Baptists after the Second London Confession. This repo carries the 1680 wording: 152 questions and answers with Collins’s original scripture proofs, his preface, the Nicene and Athanasian creeds as he printed them, and the appendix on singing.

## Texts

Canonical files live under `texts/1680-an-orthodox-catechism/`:

- `BOOK.md` — the whole work in one file
- `preface.md`, `nicene-creed.md`, `athanasian-creed.md`, `appendix-singing.md`
- `questions/001.md` … `152.md` — one file per question, with proofs

`src/data/catechism.json` is compiled from those sources for the reader. Rebuild it with:

```bash
python3 scripts/build-catechism.py
```

(The script expects a checkout of [SVRBC symbolics-data](https://gitlab.com/svrbc/symbolics-data) at `/tmp/symbolics-data` unless you edit the path.)

## Run locally

```bash
npm install
npm run dev
```

Open [http://127.0.0.1:43211](http://127.0.0.1:43211).

## Source

The 1680 catechism is in the public domain. This transcription follows the original London edition (the spelling and proofs of 1680, not the 2014 modernization). Structured source used to compile the markdown: Silicon Valley Reformed Baptist Church’s [symbolics-data](https://gitlab.com/svrbc/symbolics-data) `aoc1680` corpus, which tracks that edition. Their site [anorthodoxcatechism.org](https://anorthodoxcatechism.org/) publishes the same text under a copyright waiver.

A personal Commonplace vault was named as the intended source for this repo; that vault was not available in this environment (Google Drive was not authenticated). If your vault differs from this transcription, drop the markdown into `texts/1680-an-orthodox-catechism/` and rebuild.

## License

- Collins (1680): public domain
- Site code: MIT (see `LICENSE`)
