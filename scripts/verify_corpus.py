#!/usr/bin/env python3
"""Verify markdown and YAML corpus siblings stay equivalent."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from corpus import dump_doc, load_doc, md_to_json, normalize_doc

TEXTS = Path(__file__).resolve().parent.parent / "texts"


def _docs_equal(a: dict, b: dict) -> bool:
    return normalize_doc(a) == normalize_doc(b)


def _validate_metadata(doc: dict) -> list[str]:
    errors: list[str] = []
    meta = doc.get("Metadata")
    if not isinstance(meta, dict):
        return ["missing Metadata mapping"]
    for key in ("Title", "CreedFormat"):
        if not meta.get(key):
            errors.append(f"Metadata.{key} is empty")
    data = doc.get("Data")
    if data is None or data == "" or data == [] or data == {}:
        errors.append("Data is empty")
    return errors


def verify_md(md_path: Path) -> list[str]:
    errors: list[str] = []
    md_text = md_path.read_text(encoding="utf-8")
    md_doc = md_to_json(md_text)
    errors.extend(_validate_metadata(md_doc))

    yaml_path = md_path.with_suffix(".yaml")
    json_path = md_path.with_suffix(".json")

    if yaml_path.exists():
        yaml_doc = load_doc(yaml_path.read_text(encoding="utf-8"))
        errors.extend(_validate_metadata(yaml_doc))
        if not _docs_equal(md_doc, yaml_doc):
            errors.append("yaml sibling differs from md_to_json output")
    elif json_path.exists():
        json_doc = json.loads(json_path.read_text(encoding="utf-8"))
        errors.extend(_validate_metadata(json_doc))
        if not _docs_equal(md_doc, json_doc):
            errors.append("json sibling differs from md_to_json output")
        roundtrip = load_doc(dump_doc(json_doc))
        if not _docs_equal(json_doc, roundtrip):
            errors.append("dump_doc/load_doc round-trip differs from json sibling")
    else:
        errors.append("no .yaml or .json sibling found")

    return errors


def main() -> int:
    md_files = sorted(p for p in TEXTS.glob("*/*.md") if p.name != "README.md")
    if not md_files:
        print("no corpus markdown files found", file=sys.stderr)
        return 1

    failed = False
    for md_path in md_files:
        rel = md_path.relative_to(TEXTS.parent)
        errors = verify_md(md_path)
        if errors:
            failed = True
            print(f"FAIL {rel}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"ok   {rel}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
