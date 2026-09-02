#!/usr/bin/env python3
"""Export corpus YAML files to Creeds.json-compatible JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from corpus import load_doc

TEXTS = Path(__file__).resolve().parent.parent / "texts"


def export_yaml(yaml_path: Path, out_dir: Path | None = None) -> Path:
    doc = load_doc(yaml_path.read_text(encoding="utf-8"))
    if out_dir is None:
        out_path = yaml_path.with_suffix(".json")
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / yaml_path.with_suffix(".json").name
    out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Export corpus YAML to JSON")
    parser.add_argument(
        "paths",
        nargs="*",
        help="YAML files to export (default: all texts/*/*.yaml)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        help="Write JSON files to this directory instead of beside each YAML file",
    )
    args = parser.parse_args()

    if args.paths:
        yaml_files = [Path(p) for p in args.paths]
    else:
        yaml_files = sorted(TEXTS.glob("*/*.yaml"))

    if not yaml_files:
        print("no YAML files found", file=sys.stderr)
        return 1

    for yaml_path in yaml_files:
        if not yaml_path.exists():
            print(f"missing: {yaml_path}", file=sys.stderr)
            return 1
        out_path = export_yaml(yaml_path, args.out_dir)
        print(out_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
