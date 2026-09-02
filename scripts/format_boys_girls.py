#!/usr/bin/env python3
"""Format Errol Hulse, A Catechism for Boys and Girls (Chapel Library)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpus import dump_frontmatter, md_to_json, write_pair  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "texts" / "catechism-for-boys-and-girls"
SOURCE = Path(
    "/Users/zachmiller/.cursor/projects/Users-zachmiller-christian-texts"
    "/uploads/cfba.pdf-0.md"
)
PDF = "https://www.chapellibrary.org/pdf/books/cfba.pdf"
RETRIEVED = "2026-08-30"

PARTS = [
    (1, "God, Man, and Sin"),
    (37, "Salvation"),
    (64, "The Ten Commandments"),
    (97, "Prayer"),
    (114, "The Word, the Church, and the Ordinances"),
    (127, "Last Things"),
]

ABBREV = [
    ("1Ch", "1 Chronicles"),
    ("2Ch", "2 Chronicles"),
    ("1Co", "1 Corinthians"),
    ("2Co", "2 Corinthians"),
    ("1Ki", "1 Kings"),
    ("1Pe", "1 Peter"),
    ("2Pe", "2 Peter"),
    ("1Sa", "1 Samuel"),
    ("1Th", "1 Thessalonians"),
    ("2Th", "2 Thessalonians"),
    ("1Ti", "1 Timothy"),
    ("2Ti", "2 Timothy"),
    ("1Jo", "1 John"),
    ("2Jo", "2 John"),
    ("Act", "Acts"),
    ("Col", "Colossians"),
    ("Dan", "Daniel"),
    ("Deu", "Deuteronomy"),
    ("Ecc", "Ecclesiastes"),
    ("Eph", "Ephesians"),
    ("Exo", "Exodus"),
    ("Eze", "Ezekiel"),
    ("Gal", "Galatians"),
    ("Gen", "Genesis"),
    ("Heb", "Hebrews"),
    ("Hos", "Hosea"),
    ("Isa", "Isaiah"),
    ("Jam", "James"),
    ("Jer", "Jeremiah"),
    ("Job", "Job"),
    ("Joh", "John"),
    ("Jude", "Jude"),
    ("Lev", "Leviticus"),
    ("Luk", "Luke"),
    ("Mal", "Malachi"),
    ("Mar", "Mark"),
    ("Mat", "Matthew"),
    ("Mic", "Micah"),
    ("Neh", "Nehemiah"),
    ("Phi", "Philippians"),
    ("Pro", "Proverbs"),
    ("Psa", "Psalms"),
    ("Rev", "Revelation"),
    ("Rom", "Romans"),
    ("Zec", "Zechariah"),
    ("Ti", "Titus"),
]


def strip_chrome(text: str) -> str:
    text = re.sub(r"^Source URL:.*\n", "", text)
    text = re.sub(r"^Title:.*\n", "", text)
    text = re.sub(r"^---\s*$", "", text, flags=re.M)
    text = re.sub(r"^\d{1,2}\s*$", "", text, flags=re.M)
    text = re.sub(r"^بسم.*$", "", text, flags=re.M)
    return text


def expand_refs(raw: str) -> str:
    raw = raw.replace("*", "")
    raw = re.sub(r"\s+", " ", raw).strip()
    raw = raw.replace("-", "–")
    for abbr, full in sorted(ABBREV, key=lambda x: len(x[0]), reverse=True):
        raw = re.sub(rf"\b{abbr}\b", full, raw)
    return raw


def split_proofs(raw: str) -> list[str]:
    raw = expand_refs(raw)
    if not raw:
        return []
    if raw.lower().startswith("see references"):
        return [raw.rstrip(".") + "."]
    raw = re.sub(
        r",\s+(?=(?:compare |for example )?(?:[123]\s+)?[A-Z][a-z]{2,})",
        "; ",
        raw,
    )
    parts = [p.strip(" .") for p in re.split(r";", raw) if p.strip()]
    last_book = None
    book_re = re.compile(
        r"^((?:compare |for example )?(?:[123]\s+)?[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)\b"
    )
    out: list[str] = []
    for part in parts:
        if not part:
            continue
        m = book_re.match(part)
        if m and m.group(1) not in {"Gospel", "the Gospel"}:
            last_book = re.sub(r"^(?:compare |for example )", "", m.group(1))
            out.append(part)
        elif last_book and (
            re.match(r"^\d", part)
            or part.lower().startswith("esp.")
            or part.lower().startswith("vv.")
            or part.lower().startswith("compare")
        ):
            if part.lower().startswith("compare") or part.lower().startswith("esp"):
                out.append(f"{last_book} {part}" if not part[0].isdigit() else f"{last_book} {part}")
            else:
                out.append(f"{last_book} {part}")
        else:
            out.append(part)
    return out


def parse_questions(text: str) -> dict[int, dict]:
    start = text.find("Q.1. Who made you?")
    end = text.find("## 7. Bible References")
    body = text[start:end]
    body = re.sub(r"^#{1,3} .+$", "", body, flags=re.M)
    chunks = re.split(r"(?=Q\.\d+\.)", body)
    items: dict[int, dict] = {}
    for chunk in chunks:
        m = re.match(r"Q\.(\d+)\.\s*(.*)", chunk.strip(), re.S)
        if not m:
            continue
        n = int(m.group(1))
        rest = m.group(2)
        rest = re.sub(r"\n+", " ", rest)
        rest = re.sub(r"\s+", " ", rest).strip()
        if " A. " in rest or rest.startswith("A."):
            if rest.startswith("A."):
                q, a = items.get(n, {}).get("q", ""), rest[2:].strip()
                # question was on previous chunk — handled by Q.57/Q.123 page splits
            q, _, a = rest.partition(" A. ")
            if not a and rest.startswith("A."):
                a = rest[2:].strip()
                q = ""
        else:
            q, a = rest, ""
        q = q.strip()
        a = a.strip()
        a = a.replace("thou- sands", "thousands")
        if n in items:
            if q and not items[n]["q"]:
                items[n]["q"] = q
            if a:
                items[n]["a"] = (items[n]["a"] + " " + a).strip() if items[n]["a"] else a
        else:
            items[n] = {"q": q, "a": a}
    return items


def parse_proofs(text: str) -> dict[int, str]:
    start = text.find("## 7. Bible References")
    block = text[start:]
    block = re.sub(r"(?<!for )(Q\.\d+\.)", r"\n\1", block)
    proofs: dict[int, str] = {}
    current = None
    acc: list[str] = []
    for line in block.splitlines():
        m = re.match(r"Q\.(\d+)\.\s*(.*)", line.strip())
        if m:
            if current is not None:
                proofs[current] = " ".join(acc).strip()
            current = int(m.group(1))
            acc = [m.group(2).strip()]
        elif current is not None and line.strip() and not line.startswith("#"):
            if line.strip().startswith("*The teaching"):
                continue
            acc.append(line.strip())
    if current is not None:
        proofs[current] = " ".join(acc).strip()
    return proofs


def tidy_answer(a: str) -> str:
    a = a.strip()
    a = a.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    if a and a[-1] not in ".!?\"":
        a += "."
    return a


def main() -> None:
    raw = strip_chrome(SOURCE.read_text(encoding="utf-8"))
    questions = parse_questions(raw)
    proofs = parse_proofs(raw)
    p20 = re.sub(r"[*]", "", proofs.get(20, "")).strip().lower()
    if p20.startswith("see references"):
        proofs[20] = proofs.get(19, "")
    missing = [i for i in range(1, 135) if i not in questions or not questions[i]["q"] or not questions[i]["a"]]
    if missing:
        raise SystemExit(f"incomplete questions: {missing}")

    body: list[str] = [
        "# A Catechism for Boys and Girls",
        "",
        "Errol Hulse’s children’s catechism, Chapel Library edition (1998). "
        "Questions and answers in the booklet; Scripture proofs collected in a final section.",
        "",
        "---",
        "",
    ]
    part_at = dict(PARTS)
    for n in range(1, 135):
        if n in part_at:
            body.append(f"## {part_at[n]}")
            body.append("")
        q = questions[n]["q"].rstrip("?") + "?"
        a = tidy_answer(questions[n]["a"])
        body.append(f"### Question {n} — {q}")
        body.append("")
        body.append(f"**Answer:** {a}")
        body.append("")
        refs = split_proofs(proofs.get(n, ""))
        if refs:
            body.append("*Proofs:*")
            for r in refs:
                body.append(f"- {r}")
            body.append("")

    front = {
        "title": "A Catechism for Boys and Girls",
        "author": "Errol Hulse",
        "date": 1998,
        "edition": "Chapel Library",
        "source": PDF,
        "retrieved": RETRIEVED,
        "format": "catechism",
    }
    md = dump_frontmatter(front) + "\n".join(body).rstrip() + "\n"
    doc = md_to_json(md)
    doc["Metadata"]["SourceAttribution"] = (
        "© 1998 Chapel Library; reproduction permitted with copyright notice"
    )
    write_pair(OUT_DIR, "original", md, doc)
    (OUT_DIR / "README.md").write_text(
        "# A Catechism for Boys and Girls (Errol Hulse)\n\n"
        "134 questions in six parts, Chapel Library booklet.\n"
        f"Source: [{PDF}]({PDF}).\n"
        "`original.md` / `original.yaml`.\n"
        "© 1998 Chapel Library. They grant reproduction if the copyright notice "
        "is kept and copies are not sold beyond duplication cost.\n",
        encoding="utf-8",
    )
    print("wrote", len(doc["Data"]), "questions")


if __name__ == "__main__":
    main()
