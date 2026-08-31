#!/usr/bin/env python3
"""Ingest Creeds.json subset, vault notes, Collins JSON, and Savoy TCP."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpus import (  # noqa: E402
    dump_frontmatter,
    json_to_markdown,
    md_to_json,
    strip_wiki,
    write_pair,
)

ROOT = Path("/workspace")
TEXTS = ROOT / "texts"
UPLOADS = Path("/home/ubuntu/.cursor/projects/workspace/uploads")
CREEDS = Path("/tmp/creedsjson")
SAVOY_XML = Path("/tmp/savoy.html")
RETRIEVED_CREEDS = "2026-08-31"
SOURCE_BASE = "https://github.com/NonlinearFruit/Creeds.json/blob/master/creeds"


def cut_study_notes(text: str) -> str:
    for h in ("\n## Observation", "\n## Reflection", "\n## Implications", "\n## Cross-references"):
        if h in text:
            text = text.split(h)[0]
    return text


def drop_contents(text: str) -> str:
    if "## Contents" in text and "## Text" in text:
        before = text.split("## Contents")[0]
        after = text.split("## Text", 1)[1]
        return before + after
    return text


def vault_body(raw: str) -> str:
    text = raw
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    text = drop_contents(text)
    text = cut_study_notes(text)
    text = strip_wiki(text)
    return text.strip() + "\n"


def write_readme(directory: Path, title: str, lines: list[str]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "README.md").write_text(f"# {title}\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def import_creeds_json() -> None:
    mapping = [
        ("apostles_creed.json", "apostles-creed", "Apostles' Creed"),
        ("nicene_creed.json", "nicene-creed", "Nicene Creed"),
        ("athanasian_creed.json", "athanasian-creed", "Athanasian Creed"),
        ("chalcedonian_definition.json", "chalcedonian-definition", "Chalcedonian Definition"),
        ("canons_of_dort.json", "canons-of-dort", "Canons of Dort"),
    ]
    for fname, slug, title in mapping:
        doc = json.loads((CREEDS / fname).read_text(encoding="utf-8"))
        extra = {
            "edition": "original",
            "source": f"{SOURCE_BASE}/{fname}",
            "retrieved": RETRIEVED_CREEDS,
        }
        md = json_to_markdown(doc, extra)
        d = TEXTS / slug
        write_pair(d, "original", md, doc if False else None)
        # rewrite json from md so Metadata matches frontmatter; keep Data from source
        converted = md_to_json(md)
        converted["Data"] = doc["Data"]
        converted["Metadata"]["CreedFormat"] = doc["Metadata"]["CreedFormat"]
        converted["Metadata"]["SourceUrl"] = extra["source"]
        (d / "original.json").write_text(json.dumps(converted, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_readme(
            d,
            title,
            [
                f"Markdown: `original.md`. JSON: `original.json`.",
                f"Imported from Creeds.json (`{fname}`), public domain.",
            ],
        )
        print("imported", slug)


def strip_1689_reeves(body: str) -> str:
    lines = body.splitlines()
    out: list[str] = []
    skip_intro = False
    skip_mod = False
    for line in lines:
        if line.startswith("### Modern English edition"):
            skip_intro = True
            continue
        if skip_intro:
            if line.startswith("### Chapter"):
                skip_intro = False
            else:
                continue
        if line.startswith("**Modern English.**"):
            skip_mod = True
            continue
        if skip_mod:
            if line.startswith("**Paragraph") or line.startswith("### ") or line.startswith("**Of the"):
                skip_mod = False
            else:
                continue
        if "This note keeps the original" in line and "Stan Reeves" in line:
            continue
        out.append(line)
    return "\n".join(out)


def ingest_1689() -> None:
    raw = (UPLOADS / "The_1689_Baptist_Confession_3a96.md").read_text(encoding="utf-8")
    body = vault_body(raw)
    body = strip_1689_reeves(body)
    body = re.sub(r"^### ", "## ", body, flags=re.M)
    body = body.replace(" -- ", ". ")
    body = flatten_paragraph_proofs(body)
    body = re.sub(r"\[\^[^\]]+\]", "", body)
    # drop leftover intro about mixing editions
    body = re.sub(
        r"This note keeps the original 1677/1689 wording.*?\n\n",
        "",
        body,
        flags=re.S,
    )
    front = {
        "title": "Second London Baptist Confession",
        "author": "Particular Baptist General Assembly",
        "date": 1677,
        "edition": "original",
        "source": "https://1689.com/confession",
        "retrieved": "2026-04-19",
        "format": "confession",
    }
    md = dump_frontmatter(front) + "# Second London Baptist Confession\n\n" + body.lstrip()
    if not md.endswith("\n"):
        md += "\n"
    d = TEXTS / "1689-london-baptist-confession"
    write_pair(d, "original", md)
    write_readme(
        d,
        "Second London Baptist Confession (1677/1689)",
        [
            "Original wording from 1689.com: `original.md` / `original.json`.",
            "",
            "Stan Reeves’s modern English is copyrighted and is **not** in this repository.",
            "Read it on [Founders](https://founders.org/library-book/1689-confession/) or the author’s site ([reeveshome.org/modern1689](https://reeveshome.org/modern1689/1689_modern.pdf)).",
            "Reeves grants print copies for church use and does not grant permission to post copies on the internet.",
        ],
    )
    print("1689 original", len(md))


def ingest_keach() -> None:
    raw = (UPLOADS / "The_Baptist_Catechism__Keach_1693__f400.md").read_text(encoding="utf-8")
    body = vault_body(raw)
    # flatten footnotes into proofs lists
    body = flatten_footnotes(body)
    front = {
        "title": "The Baptist Catechism",
        "author": "Benjamin Keach; William Collins",
        "date": 1693,
        "edition": "original",
        "source": "https://1689.com/catechism",
        "retrieved": "2026-04-19",
        "format": "catechism",
    }
    md = dump_frontmatter(front) + "# The Baptist Catechism\n\n" + body.lstrip()
    d = TEXTS / "1693-baptist-catechism"
    write_pair(d, "original", md)
    write_readme(
        d,
        "The Baptist Catechism (Keach / Collins, 1693)",
        [
            "114 questions from the Commonplace vault / 1689.com.",
            "`original.md` / `original.json`.",
            "Not the 1794 Reformed Reader recension in Creeds.json.",
        ],
    )
    print("keach")


FOOTNOTE_BLOCK = re.compile(
    r"(\[\^[^\]]+\]:.*?)(?=\n### |\n## |\n\[\^|\Z)",
    re.S,
)


def flatten_footnotes(text: str) -> str:
    """Turn [^id] markers and footnote defs into *Proofs:* lists per question."""
    parts = re.split(r"(?=^### Question )", text, flags=re.M)
    out = []
    for part in parts:
        if not part.startswith("### Question"):
            out.append(re.sub(r"\[\^[^\]]+\]", "", part))
            continue
        defs: dict[str, list[str]] = {}
        def_re = re.compile(r"^\[\^([^\]]+)\]:\s*(.*)$")
        body_lines = []
        cur_id = None
        cur_refs: list[str] = []
        for line in part.splitlines():
            m = def_re.match(line.strip())
            if m:
                if cur_id:
                    defs[cur_id] = cur_refs
                cur_id = m.group(1)
                first = m.group(2).strip()
                cur_refs = [first] if first else []
                continue
            if cur_id and (line.startswith("    - ") or line.strip().startswith("- ")):
                cur_refs.append(line.strip().lstrip("- ").strip())
                continue
            if cur_id and line.strip() == "":
                defs[cur_id] = cur_refs
                cur_id = None
                cur_refs = []
                continue
            if cur_id:
                defs[cur_id] = cur_refs
                cur_id = None
                cur_refs = []
            body_lines.append(line)
        if cur_id:
            defs[cur_id] = cur_refs
        body = "\n".join(body_lines)
        refs: list[str] = []
        for fid, rlist in defs.items():
            for r in rlist:
                r = r.strip()
                if r:
                    refs.append(r)
        body = re.sub(r"\[\^[^\]]+\]", "", body).rstrip()
        if refs:
            body += "\n\n*Proofs:*\n" + "\n".join(f"- {r}" for r in refs) + "\n"
        out.append(body if body.endswith("\n") else body + "\n")
    return "\n".join(out)


def ingest_1646() -> None:
    raw = (UPLOADS / "First_London_Baptist_Confession__1646__04dd.md").read_text(encoding="utf-8")
    body = vault_body(raw)
    body = flatten_article_proofs(body)
    front = {
        "title": "First London Baptist Confession",
        "author": "seven Particular Baptist congregations in London",
        "date": 1646,
        "edition": "second impression, corrected and enlarged",
        "source": "https://www.reformedreader.org/ccc/h.htm",
        "retrieved": "2026-08-17",
        "format": "confession",
    }
    md = dump_frontmatter(front) + "# First London Baptist Confession\n\n" + body.lstrip()
    d = TEXTS / "1646-first-london"
    write_pair(d, "original", md)
    write_readme(
        d,
        "First London Baptist Confession (1646)",
        [
            "Second impression, corrected and enlarged. 1644 is not included.",
            "`original.md` / `original.json`.",
        ],
    )
    print("1646")


def flatten_paragraph_proofs(text: str) -> str:
    """Fold *Scripture proofs* footnote blocks into *Proofs:* after each paragraph."""
    def_re = re.compile(r"^\[\^([^\]]+)\]:\s*(.*)$")
    chunks = re.split(r"(?=\*\*Paragraph\s+\d+\.\*\*)", text)
    out = []
    for chunk in chunks:
        refs: list[str] = []
        body_lines = []
        in_fn = False
        in_proofs = False
        for line in chunk.splitlines():
            if line.strip() == "*Scripture proofs:*":
                in_proofs = True
                continue
            m = def_re.match(line.strip())
            if m:
                in_fn = True
                if m.group(2).strip():
                    refs.append(m.group(2).strip())
                continue
            if (in_fn or in_proofs) and (line.strip().startswith("- ") or line.startswith("    - ")):
                refs.append(line.strip().lstrip("- ").strip())
                continue
            in_fn = False
            if in_proofs and not line.strip():
                in_proofs = False
                continue
            in_proofs = False
            body_lines.append(line)
        body = "\n".join(body_lines).rstrip()
        body = re.sub(r"\[\^[^\]]+\]", "", body)
        if refs:
            body += "\n\n*Proofs:*\n" + "\n".join(f"- {r}" for r in refs if r)
        out.append(body + "\n")
    return "\n".join(out)


def flatten_article_proofs(text: str) -> str:
    """Convert ### Article / *Scripture proofs* footnotes to ## Chapter + proofs list."""
    text = re.sub(r"^### Article ", "## Article ", text, flags=re.M)
    text = re.sub(r"^### Conclusion", "## Conclusion", text, flags=re.M)
    parts = re.split(r"(?=^## )", text, flags=re.M)
    out = []
    def_re = re.compile(r"^\[\^([^\]]+)\]:\s*(.*)$")
    for part in parts:
        defs: list[str] = []
        body_lines = []
        in_fn = False
        for line in part.splitlines():
            m = def_re.match(line.strip())
            if m:
                in_fn = True
                if m.group(2).strip():
                    defs.append(m.group(2).strip())
                continue
            if in_fn and (line.strip().startswith("- ") or line.startswith("    - ")):
                defs.append(line.strip().lstrip("- ").strip())
                continue
            in_fn = False
            if line.strip() == "*Scripture proofs:*":
                continue
            body_lines.append(re.sub(r"\[\^[^\]]+\]", "", line))
        body = "\n".join(body_lines).rstrip()
        if defs:
            body += "\n\n*Proofs:*\n" + "\n".join(f"- {d}" for d in defs if d)
        out.append(body + "\n")
    return "\n".join(out)


def ingest_abstract() -> None:
    raw = (UPLOADS / "Abstract_of_Principles__1859__76ad.md").read_text(encoding="utf-8")
    body = vault_body(raw)
    # drop vault study paragraphs before Contents/Text already handled; also drop 1689 ch. notes? keep them as they are text of the note - plan said official SBTS text. Drop "1689 ch. N." lines as commentary.
    body = re.sub(r"^1689 ch\. .+\n?", "", body, flags=re.M)
    # drop long study intro before ### Charter if present
    if "### Charter" in body:
        pre, rest = body.split("### Charter", 1)
        # keep a short intro from ## Text only
        intro = ""
        for line in pre.splitlines():
            if line.startswith("Faculty oath") or line.startswith("This is the 1689"):
                continue
            intro += line + "\n"
        body = intro + "### Charter" + rest
    body = re.sub(r"^### ", "## ", body, flags=re.M)
    front = {
        "title": "Abstract of Principles",
        "author": "Basil Manly Jr.; James P. Boyce; John A. Broadus; E. T. Winkler; William Williams",
        "date": 1858,
        "edition": "official SBTS text",
        "source": "https://www.sbts.edu/about/abstract/",
        "retrieved": "2026-08-23",
        "format": "confession",
    }
    md = dump_frontmatter(front) + "# Abstract of Principles\n\n" + body.lstrip()
    d = TEXTS / "abstract-of-principles"
    write_pair(d, "original", md)
    write_readme(
        d,
        "Abstract of Principles (1858)",
        [
            "SBTS faculty oath. Public domain (US, published 1858).",
            "`original.md` / `original.json`.",
        ],
    )
    print("abstract")


def ingest_charleston() -> None:
    from format_charleston import main as format_charleston_main

    format_charleston_main()
    d = TEXTS / "1774-charleston-church-discipline"
    write_readme(
        d,
        "A Summary of Church Discipline (Charleston, 1774)",
        [
            "Baptist Association in Charleston, South Carolina. Public domain.",
            "Formatted from [Founders](https://founders.org/library/a-summary-of-church-discipline/).",
            "`original.md` / `original.json`.",
        ],
    )
    print("charleston")


def clean_tei_text(xml: str) -> str:
    xml = re.sub(r"<note[\s\S]*?</note>", " ", xml)
    xml = re.sub(r"<pb[^>]*/>", " ", xml)
    xml = re.sub(r"<gap[\s\S]*?</gap>", "", xml)
    xml = re.sub(r"<g[^>]*/>", "", xml)
    xml = re.sub(r"<hi[^>]*>", "", xml)
    xml = re.sub(r"</hi>", "", xml)
    xml = re.sub(r"<[^>]+>", " ", xml)
    xml = xml.replace("ſ", "s").replace("&amp;", "&")
    xml = re.sub(r"\s+", " ", xml)
    return xml.strip()


def ingest_savoy() -> None:
    xml = SAVOY_XML.read_text(encoding="utf-8")
    # isolate body
    body_xml = xml
    if "<text" in xml:
        body_xml = xml.split("<text", 1)[1]
    heads = list(re.finditer(r"<head>(CHAP\.[^<]+)</head>", body_xml))
    chapters = []
    for i, h in enumerate(heads):
        title = clean_tei_text(h.group(1))
        title = title.replace("XXs Of", "XX. Of")
        start = h.end()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body_xml)
        chunk = body_xml[start:end]
        # split numbered paragraphs <p> ...
        paras = re.findall(r"<p>([\s\S]*?)</p>", chunk)
        sections = []
        n = 0
        for p in paras:
            t = clean_tei_text(p)
            if not t or len(t) < 20:
                continue
            n += 1
            sections.append({"Section": str(n), "Content": t})
        cm = re.match(r"CHAP\.\s+([IVXLCs]+)\.?\s*(.*)", title)
        ch_id = cm.group(1).replace("s", "") if cm else str(i + 1)
        ch_title = cm.group(2).strip() if cm else title
        chapters.append({"Chapter": str(i + 1), "Title": ch_title or title, "Sections": sections})
    doc = {
        "Metadata": {
            "Title": "Savoy Declaration",
            "AlternativeTitles": [
                "A declaration of the faith and order owned and practised in the Congregational Churches in England"
            ],
            "Year": "1658",
            "Authors": ["John Owen", "Philip Nye", "Congregational elders at the Savoy"],
            "Location": "Savoy, London",
            "OriginalLanguage": "English",
            "OriginStory": "Congregational revision of the Westminster Confession, agreed 12 October 1658.",
            "SourceUrl": "https://github.com/textcreationpartnership/A89790",
            "SourceAttribution": "Public Domain (EEBO-TCP Phase 1, CC0)",
            "CreedFormat": "Confession",
        },
        "Data": chapters,
    }
    extra = {
        "edition": "original",
        "source": "https://github.com/textcreationpartnership/A89790",
        "retrieved": RETRIEVED_CREEDS,
        "author": "John Owen; Philip Nye; Congregational elders at the Savoy",
        "date": "1658",
        "location": "Savoy, London",
        "format": "confession",
    }
    md = json_to_markdown(doc, extra)
    d = TEXTS / "1658-savoy-declaration"
    write_pair(d, "original", md, None)
    # keep Data from parsed TEI
    converted = md_to_json(md)
    converted["Data"] = chapters
    converted["Metadata"] = doc["Metadata"]
    (d / "original.json").write_text(json.dumps(converted, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_readme(
        d,
        "Savoy Declaration (1658)",
        [
            "Public-domain TCP/EEBO transcription (CC0), not the copyrighted Reformed Standards JSON in Creeds.json.",
            "`original.md` / `original.json`. Long-s characters have been normalized.",
        ],
    )
    print("savoy chapters", len(chapters))


def collins_json() -> None:
    d = TEXTS / "1680-an-orthodox-catechism"
    for stem in ("original-1680", "modern-english"):
        md = (d / f"{stem}.md").read_text(encoding="utf-8")
        doc = md_to_json(md, "Catechism")
        (d / f"{stem}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("collins", stem, "qs", len(doc["Data"]))
    readme = (d / "README.md").read_text(encoding="utf-8")
    extra = "\nJSON siblings: `original-1680.json` and `modern-english.json`.\n"
    if "JSON siblings" not in readme:
        (d / "README.md").write_text(readme.rstrip() + extra, encoding="utf-8")


def write_root_readme() -> None:
    (ROOT / "README.md").write_text(
        """# Christian Texts

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
""",
        encoding="utf-8",
    )


def main() -> None:
    import_creeds_json()
    collins_json()
    ingest_1689()
    ingest_keach()
    ingest_1646()
    ingest_abstract()
    ingest_charleston()
    ingest_savoy()
    write_root_readme()
    # Rebuild JSON from markdown so parsers stay in sync
    for md in sorted(TEXTS.glob("*/*.md")):
        if md.name == "README.md":
            continue
        if md.name == "original.md" and md.parent.name in {
            "apostles-creed",
            "nicene-creed",
            "athanasian-creed",
            "chalcedonian-definition",
            "canons-of-dort",
            "1658-savoy-declaration",
        }:
            continue
        doc = md_to_json(md.read_text(encoding="utf-8"))
        md.with_suffix(".json").write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print("rebuilt", md.relative_to(TEXTS))
    print("done")


if __name__ == "__main__":
    main()
