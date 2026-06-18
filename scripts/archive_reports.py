#!/usr/bin/env python3
"""Move dated report files into archive/YYYY/MM/<mode>/ folders."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_MODULE = ROOT / ".agents" / "skills" / "auto-research-common" / "scripts" / "report_archive.py"


def load_archive_module():
    spec = importlib.util.spec_from_file_location("report_archive", ARCHIVE_MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load archive module: {ARCHIVE_MODULE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def topic_dirs(reports_root: Path, topic: str | None) -> list[Path]:
    if topic:
        return [reports_root / topic]
    if not reports_root.is_dir():
        return []
    return [
        path
        for path in sorted(reports_root.iterdir())
        if path.is_dir() and path.name != "paper-trace"
    ]


def summarize(results: list[dict]) -> str:
    lines = []
    total_matched = sum(int(item.get("matched_files", 0)) for item in results)
    total_moved = sum(int(item.get("moved_files", 0)) for item in results)
    total_stale = sum(int((item.get("kb_report_path_repair") or {}).get("stale_paths", 0)) for item in results)
    total_repaired = sum(int((item.get("kb_report_path_repair") or {}).get("repaired_paths", 0)) for item in results)
    lines.append(
        f"topics={len(results)} matched_files={total_matched} moved_files={total_moved} "
        f"kb_stale_paths={total_stale} kb_repaired_paths={total_repaired}"
    )
    for item in results:
        if item.get("error"):
            lines.append(f"- {item.get('topic')}: {item.get('error')}")
            continue
        moves = item.get("moves") or []
        example = ""
        if moves:
            example = f" example={moves[0].get('destination')}"
        repair = item.get("kb_report_path_repair") or {}
        repair_summary = ""
        if repair:
            repair_summary = (
                f" kb_stale={repair.get('stale_paths', 0)}"
                f" kb_repairable={repair.get('repairable_paths', 0)}"
                f" kb_repaired={repair.get('repaired_paths', 0)}"
                f" kb_unresolved={len(repair.get('unresolved_paths') or [])}"
            )
        lines.append(
            f"- {item.get('topic')}: matched={item.get('matched_files', 0)} "
            f"moved={item.get('moved_files', 0)}{repair_summary}{example}"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive dated auto-research report files by year/month/mode.")
    parser.add_argument("--reports-root", type=Path, default=Path("reports"), help="Reports root directory")
    parser.add_argument("--kb-root", type=Path, default=Path("knowledge_base"), help="Knowledge-base root directory")
    parser.add_argument("--topic", help="Topic slug to archive; omit to scan all non-paper-trace topics")
    parser.add_argument("--repair-kb-paths", action="store_true", help="Resolve stale knowledge_base runs.jsonl report_path values via topic index.json")
    parser.add_argument("--json", action="store_true", help="Print the full machine-readable move plan/result")
    parser.add_argument("--verbose", action="store_true", help="Alias for --json")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Print planned moves without changing files")
    mode.add_argument("--apply", action="store_true", help="Move files and update topic index.json")
    args = parser.parse_args()

    archive = load_archive_module()
    apply_changes = bool(args.apply)
    results = []
    for topic_dir in topic_dirs(args.reports_root, args.topic):
        if not topic_dir.exists():
            results.append({"topic": topic_dir.name, "topic_dir": str(topic_dir), "error": "missing topic directory"})
            continue
        result = archive.archive_topic(topic_dir, apply=apply_changes)
        if args.repair_kb_paths:
            result["kb_report_path_repair"] = archive.repair_kb_report_paths(topic_dir, args.kb_root, apply=apply_changes)
        results.append(result)
    payload = {"dry_run": not apply_changes, "topics": results}
    if args.json or args.verbose:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(summarize(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
