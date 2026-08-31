#!/usr/bin/env python3
"""Scripture citation parsing and validation for treatise formatting."""

from __future__ import annotations

import re
from typing import Iterable

# Longest aliases first when expanding.
BOOK_ALIASES: list[tuple[str, str]] = [
    ("Song of Sol.", "Song of Solomon"),
    ("Song of Solomon", "Song of Solomon"),
    ("1 Corinthians", "1 Corinthians"),
    ("2 Corinthians", "2 Corinthians"),
    ("1 Thessalonians", "1 Thessalonians"),
    ("2 Thessalonians", "2 Thessalonians"),
    ("1 Timothy", "1 Timothy"),
    ("2 Timothy", "2 Timothy"),
    ("1 Peter", "1 Peter"),
    ("2 Peter", "2 Peter"),
    ("1 John", "1 John"),
    ("2 John", "2 John"),
    ("3 John", "3 John"),
    ("I Cor.", "1 Corinthians"),
    ("l Cor.", "1 Corinthians"),
    ("1 Cor.", "1 Corinthians"),
    ("2 Cor.", "2 Corinthians"),
    ("1 Thess.", "1 Thessalonians"),
    ("2 Thess.", "2 Thessalonians"),
    ("1 Tim.", "1 Timothy"),
    ("l Tim.", "1 Timothy"),
    ("2 Tim.", "2 Timothy"),
    ("1 Pet.", "1 Peter"),
    ("2 Pet.", "2 Peter"),
    ("Matt.", "Matthew"),
    ("Phil.", "Philippians"),
    ("Col.", "Colossians"),
    ("Gal.", "Galatians"),
    ("Eph.", "Ephesians"),
    ("Rom.", "Romans"),
    ("Heb.", "Hebrews"),
    ("Rev.", "Revelation"),
    ("Acts", "Acts"),
    ("Isa.", "Isaiah"),
    ("Jer.", "Jeremiah"),
    ("Ezek.", "Ezekiel"),
    ("Zech.", "Zechariah"),
    ("Mal.", "Malachi"),
    ("Lev.", "Leviticus"),
    ("Deut.", "Deuteronomy"),
    ("Prov.", "Proverbs"),
    ("Psalm", "Psalms"),
    ("Ps.", "Psalms"),
    ("John", "John"),
    ("Jude", "Jude"),
    ("James", "James"),
    ("Job", "Job"),
    ("Amos", "Amos"),
    ("Titus", "Titus"),
    ("Philemon", "Philemon"),
]

CANONICAL_BOOKS = {
    "Acts",
    "Amos",
    "Colossians",
    "Deuteronomy",
    "Ephesians",
    "Galatians",
    "Hebrews",
    "James",
    "Job",
    "John",
    "Jude",
    "Leviticus",
    "Malachi",
    "Matthew",
    "Philippians",
    "Proverbs",
    "Psalms",
    "Revelation",
    "Romans",
    "Song of Solomon",
    "1 Corinthians",
    "1 John",
    "1 Peter",
    "1 Thessalonians",
    "1 Timothy",
    "2 Corinthians",
    "2 John",
    "2 Peter",
    "2 Thessalonians",
    "2 Timothy",
    "3 John",
    "Ezekiel",
    "Isaiah",
    "Zechariah",
    "Titus",
}

GLUED_REF = re.compile(r"\d(?:[A-Za-z]|[¹²³⁴⁵⁶⁷⁸⁹⁰])")
ABBREV_LEFT = re.compile(
    r"\b(?:"
    r"Matt\.|Phil\.|Col\.|Gal\.|Eph\.|Rom\.|Heb\.|Rev\.|Isa\.|Jer\.|Ezek\.|Mal\.|"
    r"Lev\.|Deut\.|Prov\.|Ps\.|"
    r"[12I]\s*Cor\.|[12]\s*Tim\.|[12]\s*Thess\.|[12]\s*Pet\.|"
    r"Song of Sol\.|l\s+Tim\.|l\s+Cor\.|I\s+Cor\."
    r")\b",
    re.I,
)
# Book + chapter:verse, optional continuation and cross refs.
NUMBERED_BOOKS = (
    r"(?:1|2|3)\s+(?:Corinthians|Thessalonians|Timothy|Peter|John)"
)
UNNUMBERED_BOOKS = (
    r"(?:Acts|Amos|Colossians|Deuteronomy|Ephesians|Galatians|Hebrews|James|Job|Jude|"
    r"Leviticus|Malachi|Matthew|Philippians|Proverbs|Psalms|Revelation|Romans|"
    r"Song of Solomon|Ezekiel|Isaiah|Titus|Zechariah)"
)
BOOK_PATTERN = rf"(?P<book>{NUMBERED_BOOKS}|{UNNUMBERED_BOOKS})"
CITATION_PATTERN = re.compile(
    rf"{BOOK_PATTERN}\s+"
    r"(?P<ref>"
    r"(?:\d+\s*(?:[:–\-]\s*\d+(?:\s*[,–\-]\s*\d+)?|\s+and\s+\d+))"
    r"(?:\s*,\s*(?:\d+\s*[,–\-]\s*\d+|\d+\s+and\s+\d+))*"
    r")",
    re.I,
)


def normalize_dashes(text: str) -> str:
    return (
        text.replace("\u0096", "–")
        .replace("\u0097", "–")
        .replace("\u2013", "–")
        .replace("\u2014", "–")
        .replace(" - ", "–")
    )


def fix_mojibake(text: str) -> str:
    return (
        text.replace("\u0092", "'")
        .replace("\u0091", "'")
        .replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("", "'")
        .replace("“", '"')
        .replace("”", '"')
    )


def expand_book_abbreviations(text: str) -> str:
    out = text
    for alias, full in BOOK_ALIASES:
        if alias.lower() in {"psalm", "ps."}:
            continue
        out = re.sub(rf"\b{re.escape(alias)}", full, out, flags=re.I)
    out = re.sub(r"\bPsalm\b(?!s\b)", "Psalms", out)
    out = re.sub(r"\bPs\.\b", "Psalms", out)
    return out


def separate_glued_citations(text: str) -> str:
    simple_books = sorted(
        (b for b in CANONICAL_BOOKS if not re.match(r"^[123] ", b)),
        key=len,
        reverse=True,
    )
    book_alt = "|".join(re.escape(b) for b in simple_books)
    # Verse numbers glued to the next book: Acts 7:38Ephesians, 2 Cor. 8:5Acts.
    text = re.sub(rf"(?<=[:\d])(\d+)({book_alt})\b", r"\1, \2", text)
    return text


def strip_citations_from_italics(text: str) -> str:
    def repl(m: re.Match) -> str:
        inner = m.group(1)
        if re.search(r"\d+:\d+", inner):
            parts = re.split(r"(\s*(?:[123] )?[A-Z][A-Za-z]+(?: [A-Za-z]+)*\s+\d)", inner, maxsplit=1)
            if len(parts) > 1:
                return f"*{parts[0].rstrip(', ')}*,{parts[1]}"
        return m.group(0)

    return re.sub(r"\*([^*]+)\*", repl, text)


def normalize_citation(book: str, ref: str) -> str:
    book = re.sub(r"\s+", " ", book.strip())
    for alias, full in BOOK_ALIASES:
        if book.lower() == alias.lower().rstrip("."):
            book = full
            break
    ref = normalize_dashes(ref.strip())
    ref = re.sub(r"\s*:\s*", ":", ref)
    ref = re.sub(r"\s*,\s*", ", ", ref)
    ref = re.sub(r"\s+and\s+", " and ", ref)
    return f"{book} {ref}"


def extract_citations(text: str) -> list[str]:
    expanded = expand_book_abbreviations(fix_mojibake(normalize_dashes(text)))
    expanded = re.sub(r"John 13:3\s+4", "John 13:34", expanded)
    refs: list[str] = []
    for m in CITATION_PATTERN.finditer(expanded):
        book = m.group("book").strip()
        refs.append(normalize_citation(book, m.group("ref")))
    # Chapter-only: "Revelation 2 and 3"
    for m in re.finditer(
        r"\b((?:[123]\s+)?[A-Z][A-Za-z]+(?:\s+of\s+[A-Za-z]+)?)\s+(\d+\s+and\s+\d+)\b",
        expanded,
    ):
        refs.append(normalize_citation(m.group(1), m.group(2)))
    # Same-book continuation after semicolon: "Acts 13:2, 3; 14:23"
    for m in re.finditer(
        r"\b((?:[123]\s+)?[A-Z][A-Za-z]+(?:\s+of\s+[A-Za-z]+)?)\s+"
        r"(\d+:\d+(?:\s*[,–\-]\s*\d+)?)\s*;\s*(\d+:\d+)\b",
        expanded,
    ):
        refs.append(normalize_citation(m.group(1), m.group(2)))
        refs.append(normalize_citation(m.group(1), m.group(3)))
    return refs


def citation_fingerprint(citations: Iterable[str]) -> set[str]:
    out: set[str] = set()
    for c in citations:
        c = re.sub(r"\s+", " ", c.strip())
        c = c.replace("-", "–")
        c = re.sub(r"\bPsalm\b", "Psalms", c)
        c = re.sub(r"\s*–\s*", "–", c)
        c = re.sub(r"Acts 6:3, 13", "Acts 6:3, Acts 13", c)
        out.add(c.lower())
    return out


def validate_citations(text: str) -> list[str]:
    errors: list[str] = []
    check = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    if GLUED_REF.search(check):
        for m in GLUED_REF.finditer(check):
            start = max(0, m.start() - 20)
            end = min(len(check), m.end() + 20)
            errors.append(f"glued reference near: ...{check[start:end]}...")
    if ABBREV_LEFT.search(check):
        errors.append("leftover abbreviated book names")
    for m in re.finditer(r"(?<!\*)\*([^*]+)\*(?!\*)", check):
        inner = m.group(1)
        if re.search(r"\d+:\d+", inner):
            errors.append(f"citation inside italics: {inner[:60]}...")
    stars = re.sub(r"\*\*[^*]+\*\*", "", check).count("*")
    if stars % 2:
        errors.append("unmatched italic markers")
    expanded = expand_book_abbreviations(text)
    for m in CITATION_PATTERN.finditer(expanded):
        book = m.group("book")
        if book not in CANONICAL_BOOKS:
            errors.append(f"unknown book name: {book}")
    return errors


def compare_citation_sets(source: str, formatted: str) -> list[str]:
    src = citation_fingerprint(extract_citations(source))
    fmt = citation_fingerprint(extract_citations(formatted))
    errors: list[str] = []
    missing = src - fmt
    extra = fmt - src
    if missing:
        errors.append(f"citations missing from formatted text: {sorted(missing)[:10]}")
    if extra:
        errors.append(f"extra citations in formatted text: {sorted(extra)[:10]}")
    return errors
