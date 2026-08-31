#!/usr/bin/env python3
"""Convert between Creeds.json-shaped JSON and markdown with YAML frontmatter."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

WIKI = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")


def strip_wiki(text: str) -> str:
    def repl(m: re.Match) -> str:
        return m.group(2) or m.group(1)

    return WIKI.sub(repl, text)


def dump_frontmatter(meta: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in meta.items():
        if value is None:
            continue
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {json.dumps(str(item), ensure_ascii=False)}")
        elif isinstance(value, bool):
            lines.append(f"{key}: {str(value).lower()}")
        elif isinstance(value, (int, float)):
            lines.append(f"{key}: {value}")
        else:
            s = str(value)
            if any(c in s for c in ":#{}[]&*?|>'\"\n"):
                lines.append(f"{key}: {json.dumps(s, ensure_ascii=False)}")
            else:
                lines.append(f"{key}: {s}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def authors_str(authors: list[str] | str | None) -> str:
    if not authors:
        return ""
    if isinstance(authors, str):
        return authors
    return "; ".join(authors)


def json_to_markdown(doc: dict[str, Any], extra_front: dict[str, Any] | None = None) -> str:
    m = doc["Metadata"]
    fmt = m.get("CreedFormat") or "Creed"
    front = {
        "title": m.get("Title"),
        "author": authors_str(m.get("Authors")) or None,
        "date": m.get("Year"),
        "edition": extra_front.get("edition") if extra_front else "original",
        "source": extra_front.get("source") if extra_front else m.get("SourceUrl"),
        "retrieved": extra_front.get("retrieved") if extra_front else None,
        "location": m.get("Location"),
        "language": m.get("OriginalLanguage"),
        "format": fmt.lower(),
    }
    if extra_front:
        for k, v in extra_front.items():
            if v is not None:
                front[k] = v
    body: list[str] = [f"# {m.get('Title', '')}", ""]
    data = doc["Data"]
    if fmt == "Creed" and isinstance(data, dict):
        body.append(data.get("Content", "").strip())
        body.append("")
    elif fmt == "Catechism" and isinstance(data, list):
        for q in data:
            n = q.get("Number")
            question = q.get("Question", "").strip()
            body.append(f"### Question {n} — {question}")
            body.append("")
            body.append(f"**Answer:** {q.get('Answer', '').strip()}")
            body.append("")
            proofs = q.get("Proofs") or []
            refs: list[str] = []
            for p in proofs:
                refs.extend(p.get("References") or [])
            if refs:
                body.append("*Proofs:*")
                for r in refs:
                    body.append(f"- {r}")
                body.append("")
    elif isinstance(data, list):
        for ch in data:
            chapter = ch.get("Chapter", "")
            title = ch.get("Title", "")
            body.append(f"## Chapter {chapter}. {title}".strip())
            body.append("")
            for sec in ch.get("Sections") or []:
                sid = sec.get("Section", "")
                content = (sec.get("Content") or "").strip()
                body.append(f"**{sid}.** {content}")
                body.append("")
                proofs = sec.get("Proofs") or []
                refs = []
                for p in proofs:
                    if isinstance(p, dict):
                        refs.extend(p.get("References") or [])
                    else:
                        refs.append(str(p))
                if refs:
                    body.append("*Proofs:*")
                    for r in refs:
                        body.append(f"- {r}")
                    body.append("")
    return dump_frontmatter({k: v for k, v in front.items() if v not in (None, "")}) + "\n".join(body).rstrip() + "\n"


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta: dict[str, Any] = {}
    key = None
    acc: list[str] = []
    for line in parts[1].splitlines():
        if re.match(r"^[a-zA-Z0-9_]+:", line) and not line.startswith("  "):
            if key:
                meta[key] = _coerce("\n".join(acc))
            key, _, rest = line.partition(":")
            key = key.strip()
            acc = [rest.strip()]
        elif key:
            acc.append(line)
    if key:
        meta[key] = _coerce("\n".join(acc))
    return meta, parts[2].lstrip("\n")


def _coerce(raw: str) -> Any:
    s = raw.strip()
    if s.startswith("[") or s.startswith("{"):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            pass
    if s.startswith('"') and s.endswith('"'):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return s.strip('"')
    items = re.findall(r"^\s*-\s+(.*)$", s, re.M)
    if items and "\n" in s:
        return [i.strip().strip('"') for i in items]
    return s


def metadata_from_front(front: dict[str, Any], fmt: str) -> dict[str, Any]:
    author = front.get("author") or ""
    authors = [a.strip() for a in re.split(r";|, and | and ", str(author)) if a.strip()] if author else []
    return {
        "Title": front.get("title"),
        "AlternativeTitles": [],
        "Year": str(front.get("date", "")),
        "Authors": authors,
        "Location": front.get("location"),
        "OriginalLanguage": front.get("language") or "English",
        "OriginStory": "",
        "SourceUrl": front.get("source"),
        "SourceAttribution": "Public Domain",
        "CreedFormat": fmt,
    }


def catechism_md_to_json(front: dict[str, Any], body: str) -> dict[str, Any]:
    items = []
    chunks = re.split(r"(?=^### Question )", body, flags=re.M)
    for chunk in chunks:
        m = re.match(
            r"^### Question (\d+)(?:\s+[—-]\s+(.*))?\s*$",
            chunk.strip().split("\n", 1)[0] if chunk.strip() else "",
        )
        if not m:
            continue
        n = int(m.group(1))
        rest = chunk.split("\n", 1)[1] if "\n" in chunk else ""
        question = (m.group(2) or "").strip()
        if not question:
            qm = re.search(r"^\*\*(.+?)\*\*\s*$", rest, re.M)
            if qm:
                question = qm.group(1).strip()
                rest = rest[qm.end() :]
        ans_m = re.search(r"\*\*Answer:\*\*\s*(.*?)(?=\n\*Proofs:|\n\*\*Scripture proofs|\n### |\Z)", rest, re.S)
        if ans_m:
            answer = re.sub(r"\[\^[^\]]+\]", "", ans_m.group(1)).strip()
            after = rest[ans_m.end() :]
        else:
            # original Collins: answer is prose until Scripture proofs
            sp = re.search(r"\*\*Scripture proofs\*\*|\*Proofs:\*", rest)
            block = rest[: sp.start()] if sp else rest
            answer = re.sub(r"^\*\*.+\*\*\s*$", "", block.strip(), flags=re.M).strip()
            after = rest[sp.end() :] if sp else ""
        refs: list[str] = []
        for line in after.splitlines():
            line = line.strip()
            bm = re.match(r"^-\s+(.+)$", line)
            nm = re.match(r"^\d+\.\s+(.+)$", line)
            if bm:
                refs.append(bm.group(1).strip())
            elif nm:
                refs.extend([p.strip() for p in nm.group(1).split(";") if p.strip()])
            elif line.startswith("[^") or line.startswith("*") or line.startswith("#"):
                continue
            elif re.match(r"^[-*].+", line):
                refs.append(line.lstrip("-* ").strip())
        # footnote style leftover lines that look like Book N:n
        for line in after.splitlines():
            line = line.strip().lstrip("- ").strip()
            if re.match(r"^[1-3]?[A-Za-z].+\d", line) and ":" in line and not line.startswith("http"):
                if line not in refs and not line.startswith("["):
                    pass
        proofs = [{"Id": i + 1, "References": [r]} for i, r in enumerate(refs)]
        items.append(
            {
                "Number": n,
                "Question": question,
                "Answer": re.sub(r"[¹²³⁴⁵⁶⁷⁸⁹⁰]+", "", answer).strip(),
                "AnswerWithProofs": answer.strip(),
                "Proofs": proofs,
            }
        )
    return {"Metadata": metadata_from_front(front, "Catechism"), "Data": items}


def confession_md_to_json(front: dict[str, Any], body: str) -> dict[str, Any]:
    chapters: list[dict[str, Any]] = []
    parts = re.split(r"(?=^#{2,3} )", body, flags=re.M)
    for part in parts:
        hm = re.match(
            r"^#{2,3}\s+(?:Chapter\s+)?(.+?)\s*$",
            part.strip().split("\n", 1)[0] if part.strip() else "",
        )
        if not hm:
            continue
        heading = hm.group(1).strip()
        cm = re.match(r"^(?:Chapter\s+)?([0-9IVXLC]+)[.:]?\s*(.*)$", heading)
        if cm:
            ch_id, title = cm.group(1), cm.group(2).strip(" .")
        else:
            ch_id, title = str(len(chapters) + 1), heading
        rest = part.split("\n", 1)[1] if "\n" in part else ""
        sections: list[dict[str, Any]] = []
        # numbered **1.** or **A1.** or **Paragraph 1.**
        segs = re.split(r"(?=\*\*(?:Paragraph\s+)?[\w.-]+\.\*\*)", rest)
        for seg in segs:
            sm = re.match(r"\*\*(?:Paragraph\s+)?([\w.-]+)\.\*\*\s*(.*)", seg.strip(), re.S)
            if not sm:
                continue
            raw = sm.group(2).strip()
            bits = re.split(r"\n\*Proofs:\*|\n\*Scripture proofs\*", raw, maxsplit=1)
            content = bits[0].strip()
            sec: dict[str, Any] = {"Section": sm.group(1), "Content": content}
            if len(bits) > 1:
                refs = [re.sub(r"^-\s+", "", ln.strip()) for ln in bits[1].splitlines() if ln.strip().startswith("- ")]
                if refs:
                    sec["Proofs"] = [{"Id": i + 1, "References": [r]} for i, r in enumerate(refs)]
            sections.append(sec)
        if not sections:
            prose = rest.strip()
            if prose:
                sections.append({"Section": "1", "Content": prose})
        chapters.append({"Chapter": str(ch_id), "Title": title, "Sections": sections})
    return {"Metadata": metadata_from_front(front, "Confession"), "Data": chapters}


def creed_md_to_json(front: dict[str, Any], body: str) -> dict[str, Any]:
    # drop the H1
    text = re.sub(r"^# .+\n+", "", body.strip() + "\n")
    return {"Metadata": metadata_from_front(front, "Creed"), "Data": {"Content": text.strip()}}


def md_to_json(text: str, fmt: str | None = None) -> dict[str, Any]:
    front, body = parse_frontmatter(text)
    fmt = fmt or str(front.get("format") or "").title()
    if fmt.lower() == "catechism" or re.search(r"^### Question ", body, re.M):
        return catechism_md_to_json(front, body)
    if fmt.lower() == "creed" or (front.get("format") == "creed"):
        return creed_md_to_json(front, body)
    return confession_md_to_json(front, body)


def write_pair(directory: Path, stem: str, markdown: str, doc: dict[str, Any] | None = None) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{stem}.md").write_text(markdown, encoding="utf-8")
    if doc is None:
        doc = md_to_json(markdown)
    (directory / f"{stem}.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
