#!/usr/bin/env python3
"""Format Charleston 1774 Church Discipline from Founders source text."""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpus import dump_frontmatter, md_to_json, write_pair  # noqa: E402
from scripture_refs import (  # noqa: E402
    compare_citation_sets,
    expand_book_abbreviations,
    fix_mojibake,
    normalize_dashes,
    separate_glued_citations,
    strip_citations_from_italics,
    validate_citations,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "texts" / "1774-charleston-church-discipline"
FOUNDERS_URL = "https://founders.org/library/a-summary-of-church-discipline/"

CHAPTER_TITLES = {
    "I": "Of a True and Orderly Gospel Church",
    "II": "Of Church Officers",
    "III": "Of Receiving Persons to Church Membership",
    "IV": "Of the Duties Incumbent on Church Members",
    "V": "Of Church Censures",
    "VI": "Of the Association of Churches",
}

BROKEN_WORD_FIXES = [
    ("con sent", "consent"),
    ("p arties", "parties"),
    ("concer ns", "concerns"),
    ("busine ss", "business"),
    ("w ine", "wine"),
    ("chur ch", "church"),
    ("fait h", "faith"),
    ("ag ainst", "against"),
    ("ano ther", "another"),
    ("avoidi ng", "avoiding"),
    ("meddlers wit h", "meddlers with"),
    ("report ag ainst", "report against"),
    ("h igh", "high"),
    ("withdraw s", "withdraws"),
    ("off ended", "offended"),
    ("notorious an d", "notorious and"),
    ("att en d", "attend"),
    ("fo r ", "for "),
    (" pr ayer", " prayer"),
    ("modera tor", "moderator"),
    ("sho uld", "should"),
    ("no mean s", "no means"),
    ("ove r ", "over "),
    ("un der ", "under "),
    ("principl es", "principles"),
    ("removin g", "removing"),
    ("erron eous", "erroneous"),
    ("Le pers", "Lepers"),
    ("ult imate", "ultimate"),
    ("gospel churc h", "gospel church"),
    ("V erily", "Verily"),
    ("i.e .", "i.e.,"),
    ("Bapt ist", "Baptist"),
    ("Gal. 6 :10", "Galatians 6:10"),
    ("John 13:3 4", "John 13:34"),
    ("therefo re", "therefore"),
    ("an d therefore", "and therefore"),
    ("an d actions", "and actions"),
]

INTRO_BLURB = (
    "**A Summary of Church Discipline, shewing the qualifications and duties of the officers "
    "and members of a gospel church**, by the Baptist Association in Charleston, South Carolina "
    "(printed by David Bruce). This is the **handbook**, not the Charleston Confession "
    "(which is the 1689/Philadelphia text minus laying on of hands). "
    "From [Founders](https://founders.org/library/a-summary-of-church-discipline/)."
)

FRONTMATTER = {
    "title": "A Summary of Church Discipline",
    "author": "Charleston Baptist Association",
    "date": 1774,
    "edition": "original",
    "source": FOUNDERS_URL,
    "retrieved": "2026-08-17",
    "location": "Charleston, South Carolina",
    "format": "confession",
}


def fetch_founders_text() -> str:
    req = urllib.request.Request(FOUNDERS_URL, headers={"User-Agent": "christian-texts-corpus/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p>", "\n\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&#\d+;", "'", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_body(raw: str) -> str:
    start = re.search(r"THE following Summary of Church Discipline", raw, re.I)
    end = re.search(r"\bTHE END\b", raw, re.I)
    if not start or not end:
        raise RuntimeError("Could not locate treatise body / THE END in Founders text")
    return raw[start.start() : end.start()].strip()


def insert_structure_breaks(text: str) -> str:
    text = re.sub(r"\s+CHAPTER\s+([IVXLC]+)\s+", r"\n\nCHAPTER \1\n\n", text, flags=re.I)
    text = re.sub(r"(?<=\.)\s+(\d+\.\s+)", r"\n\n\1", text)
    text = re.sub(r"(?<=\.)\s+(The [a-z])", r"\n\n\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fix_broken_words(text: str) -> str:
    out = text
    for bad, good in BROKEN_WORD_FIXES:
        out = out.replace(bad, good)
    return out


def normalize_verse_spacing(text: str) -> str:
    out = re.sub(r"(\d)\s+([–\-]\s*\d)", r"\1\2", text)
    out = re.sub(r"(\d)\s+and\s+(\d)(?!\d)", r"\1 and \2", out)
    out = re.sub(r"(\d)\s*:\s*(\d)", r"\1:\2", out)
    out = re.sub(r"Acts\s+6:3,\s*13:2", "Acts 6:3, Acts 13:2", out)
    out = re.sub(r"1 Cor:\s*12:28", "1 Corinthians 12:28", out)
    out = re.sub(r"2 Cor\s+2:6", "2 Corinthians 2:6", out)
    out = re.sub(r"I Cor\.\s*5:13", "1 Corinthians 5:13", out)
    out = re.sub(r"Jude l9", "Jude 19", out)
    out = re.sub(r"Acts\s+9:26\s*[–\-]\s*28", "Acts 9:26–28", out)
    return out


def apply_italics(text: str) -> str:
    replacements = [
        (
            "THE following Summary of Church Discipline,",
            "THE following *Summary of Church Discipline,*",
        ),
        (
            "his Exposition and Body of Divinity.",
            "his *Exposition and Body of Divinity.*",
        ),
        (
            "Where two or three are gathered together in my name, there am I in the midst of them,",
            "*Where two or three are gathered together in my name, there am I in the midst of them,*",
        ),
        (
            "a little one shall become a thousand, and a small one a strong nation.",
            "*a little one shall become a thousand, and a small one a strong nation.*",
        ),
        (
            "submitting yourselves one to another in the fear of God;",
            "*submitting yourselves one to another in the fear of God;*",
        ),
        (
            "sufficient to such a man is this punishment, which was inflicted of many:",
            "*sufficient to such a man is this punishment, which was inflicted of many:*",
        ),
        (
            "by the more, the greater or major part.",
            "*by the more, the greater or major part.*",
        ),
        (
            "like Aaron's, buds",
            "like *Aaron's,* buds",
        ),
        (
            "honor or filthy lucre.",
            "honor or *filthy lucre.*",
        ),
        (
            "Verily I say unto you, except ye be converted, and become as little children, ye shall not enter into the kingdom of heaven.",
            "*Verily I say unto you, except ye be converted, and become as little children, ye shall not enter into the kingdom of heaven.*",
        ),
        (
            "lively stones, i.e., of living souls",
            "*lively stones, i.e.* of living souls",
        ),
        (
            "dead in trespasses and sins,",
            "*dead in trespasses and sins,*",
        ),
        (
            "the pillar and ground of truth?",
            "*the pillar and ground of truth?*",
        ),
        (
            "becometh the gospel of Christ,",
            "*becometh the gospel of Christ,*",
        ),
        (
            "gladly received the Word, were baptized;",
            "*gladly received* the Word, *were baptized;*",
        ),
        (
            "the Lord add to the church were such as should be saved,",
            "*the Lord add to the church* were *such as should be saved,*",
        ),
        (
            "It seemed good to the Holy Ghost, and to us, to lay upon you no greater burden than these necessary things,",
            "*It seemed good to the Holy Ghost, and to us, to lay upon you no greater burden than these necessary things,*",
        ),
        (
            "to do good, and to communicate forget not,",
            "*to do good, and to communicate forget not,*",
        ),
        (
            "a little leaven leavens the whole lump, and therefore the old leaven must be purged out, that the church may become a new lump; evil communications corrupt good manners,",
            "*a little leaven leavens the whole lump,* and therefore *the old leaven* must be purged out, that the church may become *a new lump*; *evil communications corrupt good manners,*",
        ),
        (
            "swallowed up with overmuch sorrow,",
            "*swallowed up with overmuch sorrow,*",
        ),
        (
            "trucebreakers and despisers of those that are good,",
            "*trucebreakers* and *despisers of those that are good,*",
        ),
        (
            "felo de se,",
            "*felo de se,*",
        ),
        (
            "defense if he has any to make.",
            "*defense* if he has any to make.",
        ),
        (
            "unto Satan for the destruction of the flesh,",
            "*unto Satan for the destruction of the flesh,*",
        ),
    ]
    out = text
    for old, new in replacements:
        out = out.replace(old, new)
    out = strip_citations_from_italics(out)
    return out


def convert_enumerations(paragraph: str) -> str:
    """Turn inline (1)...(2)... duty lists into markdown ordered lists."""
    if not re.search(r"\(\d+\)", paragraph):
        return paragraph
    parts = [p for p in re.split(r"\s*(?=\(\d+\)\s*)", paragraph.strip()) if p.strip()]
    if len(parts) < 2:
        return paragraph
    lead = re.sub(r"\s+As\s*$", "", parts[0].rstrip())
    list_items: list[str] = []
    for item in parts[1:]:
        m = re.match(r"\((\d+)\s*\)\s*(.*)", item.strip(), re.S)
        if not m:
            return paragraph
        list_items.append(m.group(2).strip())
    if len(list_items) < 2:
        return paragraph
    lines: list[str] = []
    if lead:
        lines.append(lead)
        lines.append("")
    for i, item in enumerate(list_items, 1):
        lines.append(f"{i}. {item}")
    return "\n".join(lines)


def format_section_paragraphs(content: str) -> str:
    content = re.sub(r"\((\d+)\s+\)", r"(\1)", content)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
    formatted: list[str] = []
    i = 0
    while i < len(paragraphs):
        para = paragraphs[i]
        if re.search(r"\(\d+\)", para):
            block = [para]
            j = i + 1
            while j < len(paragraphs) and re.search(r"\(\d+\)", paragraphs[j]):
                block.append(paragraphs[j])
                j += 1
            merged = " ".join(block)
            if len(re.findall(r"\(\d+\)", merged)) >= 2:
                converted = convert_enumerations(merged)
                if re.search(r"^\d+\. ", converted, re.M):
                    formatted.append(converted)
                    i = j
                    continue
        formatted.append(convert_enumerations(para))
        i += 1
    return "\n\n".join(formatted)


def split_chapters(body: str) -> list[tuple[str, str, str]]:
    """Return (roman, title, content) tuples."""
    body = insert_structure_breaks(body)
    parts = re.split(r"\bCHAPTER\s+([IVXLC]+)\b", body, flags=re.I)
    chapters: list[tuple[str, str, str]] = []
    preface = parts[0].strip()
    chapters.append(("Preface", "Preface", preface))
    i = 1
    while i < len(parts):
        roman = parts[i].strip().upper()
        rest = parts[i + 1].strip() if i + 1 < len(parts) else ""
        i += 2
        lines = rest.splitlines()
        title = ""
        content_lines: list[str] = []
        for line in lines:
            stripped = line.strip()
            if not title and stripped and not re.match(r"^\d+\.", stripped):
                title = stripped
                continue
            content_lines.append(line)
        if not title:
            title = CHAPTER_TITLES.get(roman, "")
        else:
            # Normalize title casing from founders.
            title = CHAPTER_TITLES.get(roman, title)
        chapters.append((roman, title, "\n".join(content_lines).strip()))
    return chapters


def split_sections(chapter_content: str) -> list[tuple[str, str]]:
    """Split chapter into numbered sections."""
    if not chapter_content:
        return []
    chunks = re.split(r"(?=^\d+\.\s)", chapter_content, flags=re.M)
    sections: list[tuple[str, str]] = []
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        m = re.match(r"^(\d+)\.\s*(.*)", chunk, re.S)
        if m:
            sections.append((m.group(1), m.group(2).strip()))
        else:
            sections.append(("0", chunk))
    return sections


def normalize_prose(text: str) -> str:
    text = fix_mojibake(normalize_dashes(text))
    text = fix_broken_words(text)
    text = normalize_verse_spacing(text)
    text = expand_book_abbreviations(text)
    text = separate_glued_citations(text)
    text = normalize_dashes(text)
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r",\s+", ", ", text)
    text = re.sub(r"\s+\.", ".", text)
    return text.strip()


def build_markdown(raw_body: str) -> str:
    body = normalize_prose(raw_body)
    chapters = split_chapters(body)
    lines: list[str] = [
        dump_frontmatter(FRONTMATTER).rstrip(),
        "",
        "# A Summary of Church Discipline",
        "",
        INTRO_BLURB,
        "",
    ]
    for roman, title, content in chapters:
        if roman == "Preface":
            lines.append("## Preface")
            lines.append("")
            preface = normalize_prose(content)
            preface = apply_italics(preface)
            for para in [p.strip() for p in re.split(r"\n\s*\n", preface) if p.strip()]:
                lines.append(para)
                lines.append("")
            continue
        lines.append(f"## Chapter {roman} — {title}")
        lines.append("")
        sections = split_sections(content)
        if not sections:
            lines.append(format_section_paragraphs(apply_italics(normalize_prose(content))))
            lines.append("")
            continue
        for num, sec_content in sections:
            prose = format_section_paragraphs(apply_italics(normalize_prose(sec_content)))
            if num == "0":
                lines.append(prose)
            else:
                lines.append(f"**{num}.** {prose}")
            lines.append("")
    md = "\n".join(lines).rstrip() + "\n"
    return md


def validate_output(source_body: str, md: str) -> None:
    body_only = re.sub(r"^---[\s\S]*?---\n", "", md)
    source_norm = normalize_prose(source_body)
    errors = validate_citations(body_only)
    errors.extend(compare_citation_sets(source_norm, body_only))
    if errors:
        raise RuntimeError("Citation validation failed:\n" + "\n".join(f"- {e}" for e in errors))


def main() -> None:
    raw = fetch_founders_text()
    body = extract_body(raw)
    md = build_markdown(body)
    validate_output(body, md)
    write_pair(OUT_DIR, "original", md)
    doc = md_to_json(md)
    sections = sum(len(ch.get("Sections") or []) for ch in doc.get("Data") or [])
    print(f"Wrote {OUT_DIR / 'original.md'} ({sections} JSON sections)")


if __name__ == "__main__":
    main()
