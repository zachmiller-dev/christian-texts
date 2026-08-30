#!/usr/bin/env python3
"""Compile SVRBC aoc1680 YAML/markdown into the christian-texts corpus."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

SRC = Path("/tmp/symbolics-data")
OUT = Path("/workspace/texts/1680-an-orthodox-catechism")
DATA = Path("/workspace/src/data")

SECTIONS = {
    1: "Introduction",
    2: "Of the Holy Ghost",
    3: "Of the Sacraments",
    4: "Of the Lord’s Supper",
    5: "The third Part is of Man’s Thankfulness",
    6: "Of Prayer",
}


def load_yml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^# yaml-language-server:.*\n", "", text)
    return yaml.safe_load(text)


def strip_frontmatter(md: str) -> tuple[str, str]:
    if md.startswith("---"):
        parts = md.split("---", 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1]) or {}
            return meta.get("title", ""), parts[2].strip()
    return "", md.strip()


def superscript(n: int) -> str:
    table = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(n).translate(table)


def render_answer(segments: list[dict]) -> tuple[str, list[str]]:
    proofs: list[str] = []
    parts: list[str] = []
    for seg in segments:
        text = (seg.get("text") or "").strip()
        proof = seg.get("proofs")
        if proof:
            proofs.append(str(proof).strip())
            n = len(proofs)
            marker = superscript(n)
            if text:
                parts.append(f"{text}{marker}")
            else:
                parts.append(marker)
        elif text:
            parts.append(text)
    answer = " ".join(parts)
    answer = re.sub(r" +", " ", answer).strip()
    return answer, proofs


def question_markdown(q: dict, answer: str, proofs: list[str], section: str) -> str:
    hid = ""
    rel = q.get("relations") or {}
    heid = rel.get("heidelberg") or []
    if heid:
        hid = ", ".join(str(x) for x in heid)
    lines = [
        "---",
        f'id: "{q["id"]}"',
        f"section: {json.dumps(section, ensure_ascii=False)}",
        f"prev: {json.dumps(str(q['prev']) if q.get('prev') else None)}",
        f"next: {json.dumps(str(q['next']) if q.get('next') else None)}",
        f"heidelberg: {json.dumps(hid)}",
        "---",
        "",
        f"# Question {q['id']}",
        "",
        f"**{q['question']}**",
        "",
        answer,
        "",
    ]
    if proofs:
        lines.append("## Scripture proofs")
        lines.append("")
        for i, p in enumerate(proofs, 1):
            lines.append(f"{i}. {p}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "questions").mkdir(exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    preface_title, preface_body = strip_frontmatter(
        (SRC / "catechisms/aoc1680/prose/preface.md").read_text(encoding="utf-8")
    )
    appendix_title, appendix_body = strip_frontmatter(
        (SRC / "catechisms/aoc1680/prose/appendix_singing.md").read_text(
            encoding="utf-8"
        )
    )
    nicene_title, nicene_body = strip_frontmatter(
        (SRC / "creeds/nicene/nicene.md").read_text(encoding="utf-8")
    )
    ath_title, ath_body = strip_frontmatter(
        (SRC / "creeds/athanasian/athanasian.md").read_text(encoding="utf-8")
    )

    (OUT / "preface.md").write_text(
        f"# {preface_title}\n\n{preface_body}\n", encoding="utf-8"
    )
    (OUT / "appendix-singing.md").write_text(
        f"# {appendix_title}\n\n{appendix_body}\n", encoding="utf-8"
    )
    (OUT / "nicene-creed.md").write_text(
        f"# {nicene_title}\n\n{nicene_body}\n", encoding="utf-8"
    )
    (OUT / "athanasian-creed.md").write_text(
        f"# {ath_title}\n\n{ath_body}\n", encoding="utf-8"
    )

    qdir = SRC / "catechisms/aoc1680/questions"
    questions = []
    for path in sorted(qdir.glob("*.yml"), key=lambda p: int(p.stem)):
        q = load_yml(path)
        section = SECTIONS.get(int(q.get("parent") or 1), "Introduction")
        answer, proofs = render_answer(q.get("segments") or [])
        (OUT / "questions" / f"{int(q['id']):03d}.md").write_text(
            question_markdown(q, answer, proofs, section), encoding="utf-8"
        )
        questions.append(
            {
                "id": str(q["id"]),
                "section": section,
                "question": q["question"],
                "answer": answer,
                "proofs": proofs,
                "prev": str(q["prev"]) if q.get("prev") else None,
                "next": str(q["next"]) if q.get("next") else None,
                "heidelberg": [str(x) for x in (q.get("relations") or {}).get("heidelberg") or []],
            }
        )

    book_parts = [
        "# An Orthodox Catechism",
        "",
        "Being the Sum of Christian Religion, Contained in the Law and Gospel.",
        "",
        "By Hercules Collins. London, 1680.",
        "",
        f"# {preface_title}",
        "",
        preface_body,
        "",
    ]
    current_section = None
    for q in questions:
        if q["section"] != current_section:
            current_section = q["section"]
            book_parts.extend([f"## {current_section}", ""])
        book_parts.extend(
            [
                f"### Question {q['id']}",
                "",
                f"**{q['question']}**",
                "",
                q["answer"],
                "",
            ]
        )
        if q["proofs"]:
            book_parts.append("**Scripture proofs**")
            book_parts.append("")
            for i, p in enumerate(q["proofs"], 1):
                book_parts.append(f"{i}. {p}")
            book_parts.append("")
    book_parts.extend(
        [
            f"# {nicene_title}",
            "",
            nicene_body,
            "",
            f"# {ath_title}",
            "",
            ath_body,
            "",
            f"# {appendix_title}",
            "",
            appendix_body,
            "",
        ]
    )
    (OUT / "BOOK.md").write_text("\n".join(book_parts), encoding="utf-8")

    catalog = {
        "title": "An Orthodox Catechism",
        "subtitle": "Being the Sum of Christian Religion, Contained in the Law and Gospel",
        "author": "Hercules Collins",
        "year": 1680,
        "place": "London",
        "sections": [{"id": k, "title": v} for k, v in SECTIONS.items()],
        "questions": questions,
        "preface": preface_body,
        "prefaceTitle": preface_title,
        "niceneTitle": nicene_title,
        "nicene": nicene_body,
        "athanasianTitle": ath_title,
        "athanasian": ath_body,
        "appendixTitle": appendix_title,
        "appendix": appendix_body,
    }
    (DATA / "catechism.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(questions)} questions")


if __name__ == "__main__":
    main()
