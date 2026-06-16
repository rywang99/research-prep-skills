#!/usr/bin/env python3
"""Query local auto-research knowledge-base graph artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


DEFAULT_KB_ROOT = Path("knowledge_base")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at {path}:{line_no}: {exc}") from exc
        if isinstance(value, dict):
            rows.append(value)
    return rows


def topic_dirs(kb_root: Path, topic: str | None) -> list[Path]:
    if topic:
        direct = kb_root / topic
        nested = kb_root / "paper-trace" / topic
        return [p for p in (direct, nested) if p.exists()]
    return [p for p in kb_root.glob("**") if p.is_dir() and ((p / "entities.jsonl").exists() or (p / "graph_latest.json").exists())]


def text(value: Any) -> str:
    return "" if value is None else str(value)


def matches(row: dict[str, Any], query: str) -> bool:
    if not query:
        return True
    needle = query.lower()
    haystack = " ".join(text(v) for v in row.values() if not isinstance(v, (dict, list))).lower()
    return needle in haystack


def filter_rows(rows: Iterable[dict[str, Any]], row_type: str | None, relation: str | None, query: str) -> list[dict[str, Any]]:
    result = []
    for row in rows:
        if row_type and row.get("type") != row_type:
            continue
        if relation and row.get("relation") != relation:
            continue
        if not matches(row, query):
            continue
        result.append(row)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Query local auto-research knowledge-base graph rows.")
    parser.add_argument("--kb-root", default=DEFAULT_KB_ROOT, type=Path, help="Knowledge-base root directory")
    parser.add_argument("--topic", help="Topic slug, e.g. spatial-audio-llm")
    parser.add_argument("--type", dest="entity_type", help="Entity type to show, e.g. source|gap|idea|claim")
    parser.add_argument("--relation", help="Link relation to show, e.g. supports|addresses|derived_from")
    parser.add_argument("--query", default="", help="Case-insensitive substring filter")
    parser.add_argument("--links", action="store_true", help="Query links instead of entities")
    parser.add_argument("--limit", type=int, default=20, help="Maximum rows to print")
    args = parser.parse_args()

    paths = topic_dirs(args.kb_root, args.topic)
    if not paths:
        print(json.dumps({"rows": [], "count": 0}, ensure_ascii=False, indent=2))
        return 0

    filename = "links.jsonl" if args.links or args.relation else "entities.jsonl"
    rows: list[dict[str, Any]] = []
    for path in paths:
        for row in load_jsonl(path / filename):
            row.setdefault("topic_dir", str(path))
            rows.append(row)

    filtered = filter_rows(rows, args.entity_type, args.relation, args.query)
    filtered = filtered[-args.limit:] if args.limit > 0 else filtered
    print(json.dumps({"count": len(filtered), "rows": filtered}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
