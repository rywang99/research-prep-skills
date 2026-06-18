"""Archive dated auto-research reports into a time/mode hierarchy."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

REPORT_EXTENSIONS = {"html", "json"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HASH_SUFFIX_RE = re.compile(r"^(?P<mode>.+)-(?P<suffix>[0-9a-f]{8})$")
INDEX_NAME = "index.json"
ARCHIVE_DIR_NAME = "archive"
ARCHIVE_LAYOUT = "archive/YYYY/MM/<mode>/"


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def parse_report_name(path: Path) -> dict[str, str] | None:
    """Return metadata for YYYY-MM-DD_<mode>.html/json style reports."""
    ext = path.suffix.lower().removeprefix(".")
    if ext not in REPORT_EXTENSIONS:
        return None
    if "_" not in path.stem:
        return None
    date, rest = path.stem.split("_", 1)
    if not DATE_RE.match(date) or not rest:
        return None
    variant = ""
    mode = rest
    match = HASH_SUFFIX_RE.match(rest)
    if match:
        mode = match.group("mode")
        variant = match.group("suffix")
    return {
        "date": date,
        "mode": mode,
        "variant": variant,
        "stem": path.stem,
        "extension": ext,
    }


def archive_dir_for(topic_dir: Path, date: str, mode: str) -> Path:
    year, month, _ = date.split("-", 2)
    return topic_dir / ARCHIVE_DIR_NAME / year / month / mode


def stable_suffix(parts: list[str]) -> str:
    digest = hashlib.sha1("\n".join(parts).encode("utf-8")).hexdigest()
    return digest[:8]


def relative(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def grouped_files(files: list[Path]) -> dict[str, list[Path]]:
    groups: dict[str, list[Path]] = {}
    for path in files:
        meta = parse_report_name(path)
        if not meta:
            continue
        groups.setdefault(meta["stem"], []).append(path)
    return groups


def compute_group_moves(topic_dir: Path, group: list[Path]) -> list[dict[str, Any]]:
    if not group:
        return []
    meta = parse_report_name(group[0])
    if not meta:
        return []
    target_dir = archive_dir_for(topic_dir, meta["date"], meta["mode"])
    stem = meta["stem"]
    targets = [target_dir / f"{stem}{path.suffix.lower()}" for path in group]
    if any(target.exists() for target in targets):
        suffix = stable_suffix([str(path.resolve()) for path in sorted(group)])
        stem = f"{meta['date']}_{meta['mode']}-{suffix}"
        targets = [target_dir / f"{stem}{path.suffix.lower()}" for path in group]
    return [
        {
            "source": path,
            "destination": target,
            "date": meta["date"],
            "mode": meta["mode"],
            "extension": path.suffix.lower().removeprefix("."),
        }
        for path, target in zip(group, targets)
    ]


def root_report_files(topic_dir: Path) -> list[Path]:
    if not topic_dir.is_dir():
        return []
    return [
        path
        for path in sorted(topic_dir.iterdir())
        if path.is_file() and path.name != INDEX_NAME and parse_report_name(path)
    ]


def collect_report_entries(topic_dir: Path) -> list[dict[str, Any]]:
    candidates: list[Path] = []
    candidates.extend(root_report_files(topic_dir))
    archive_dir = topic_dir / ARCHIVE_DIR_NAME
    if archive_dir.is_dir():
        candidates.extend(path for path in sorted(archive_dir.rglob("*")) if path.is_file() and parse_report_name(path))

    groups: dict[str, dict[str, Any]] = {}
    for path in candidates:
        meta = parse_report_name(path)
        if not meta:
            continue
        rel = relative(path, topic_dir)
        key = str(path.with_suffix("").relative_to(topic_dir))
        entry = groups.setdefault(
            key,
            {
                "date": meta["date"],
                "mode": meta["mode"],
                "variant": meta["variant"],
                "location": "archive" if rel.startswith(f"{ARCHIVE_DIR_NAME}/") else "root",
            },
        )
        entry[meta["extension"]] = rel
    return sorted(groups.values(), key=lambda item: (item["date"], item["mode"], item.get("variant", "")), reverse=True)


def read_existing_index(topic_dir: Path) -> dict[str, Any]:
    path = topic_dir / INDEX_NAME
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def write_index(topic_dir: Path, move_records: list[dict[str, Any]] | None = None, timestamp: str | None = None) -> Path:
    timestamp = timestamp or now_iso()
    existing = read_existing_index(topic_dir)
    archive_runs = existing.get("archive_runs")
    if not isinstance(archive_runs, list):
        archive_runs = []
    if move_records:
        archive_runs.append(
            {
                "archived_at": timestamp,
                "moved_files": len(move_records),
                "files": [
                    {
                        "source": relative(record["source"], topic_dir),
                        "destination": relative(record["destination"], topic_dir),
                        "mode": record["mode"],
                        "date": record["date"],
                        "extension": record["extension"],
                    }
                    for record in move_records
                ],
            }
        )
    index = {
        "schema_version": "1.0",
        "topic_slug": topic_dir.name,
        "updated_at": timestamp,
        "archive_layout": ARCHIVE_LAYOUT,
        "reports": collect_report_entries(topic_dir),
        "archive_runs": archive_runs[-50:],
    }
    index_path = topic_dir / INDEX_NAME
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return index_path


def archive_file_groups(topic_dir: Path, groups: dict[str, list[Path]], apply: bool = False) -> dict[str, Any]:
    moves: list[dict[str, Any]] = []
    for group in groups.values():
        moves.extend(compute_group_moves(topic_dir, sorted(group)))
    result: dict[str, Any] = {
        "topic": topic_dir.name,
        "topic_dir": str(topic_dir),
        "dry_run": not apply,
        "matched_files": sum(len(group) for group in groups.values()),
        "moved_files": 0,
        "moves": [
            {
                "source": str(record["source"]),
                "destination": str(record["destination"]),
                "mode": record["mode"],
                "date": record["date"],
                "extension": record["extension"],
            }
            for record in moves
        ],
        "index": str(topic_dir / INDEX_NAME),
    }
    if not apply:
        return result
    if not moves:
        return result

    applied: list[dict[str, Any]] = []
    for record in moves:
        source = record["source"]
        destination = record["destination"]
        if not source.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        applied.append(record)
    write_index(topic_dir, applied)
    result["moved_files"] = len(applied)
    return result


def archive_topic(topic_dir: Path, apply: bool = False) -> dict[str, Any]:
    return archive_file_groups(topic_dir, grouped_files(root_report_files(topic_dir)), apply=apply)


def archive_rendered_report(input_json: Path, output_html: Path, apply: bool = True) -> dict[str, Any]:
    """Archive one freshly rendered report pair and return the final paths."""
    topic_dir = output_html.parent
    files = [output_html]
    if (
        input_json.exists()
        and input_json.parent.resolve() == topic_dir.resolve()
        and input_json.stem == output_html.stem
    ):
        files.append(input_json)
    result = archive_file_groups(topic_dir, grouped_files(files), apply=apply)
    final_html = output_html
    final_json = input_json
    for move in result.get("moves", []):
        source = Path(move["source"])
        destination = Path(move["destination"])
        if source == output_html:
            final_html = destination
        if source == input_json:
            final_json = destination
    result["html_path"] = str(final_html)
    result["json_path"] = str(final_json)
    return result


def resolve_archived_report_path(topic_dir: Path, report_path: str) -> str | None:
    """Resolve a stale flat report path through the topic archive index."""
    path = Path(report_path)
    if path.exists():
        return report_path
    meta = parse_report_name(path)
    if not meta:
        return None
    index = read_existing_index(topic_dir)
    reports = index.get("reports")
    if not isinstance(reports, list):
        return None
    for entry in reports:
        if not isinstance(entry, dict):
            continue
        if entry.get("date") != meta["date"] or entry.get("mode") != meta["mode"]:
            continue
        if text_or_empty(entry.get("variant")) != meta["variant"]:
            continue
        rel = entry.get(meta["extension"])
        if not isinstance(rel, str) or not rel:
            continue
        candidate = topic_dir / rel
        if candidate.exists():
            return candidate.as_posix()
    return None


def text_or_empty(value: Any) -> str:
    return "" if value is None else str(value)


def repair_kb_report_paths(topic_dir: Path, kb_root: Path = Path("knowledge_base"), apply: bool = False) -> dict[str, Any]:
    """Update stale knowledge-base run report_path values using archive index paths."""
    runs_path = kb_root / topic_dir.name / "runs.jsonl"
    result: dict[str, Any] = {
        "kb_runs": str(runs_path),
        "dry_run": not apply,
        "stale_paths": 0,
        "repairable_paths": 0,
        "repaired_paths": 0,
        "unresolved_paths": [],
        "replacements": [],
    }
    if not runs_path.exists():
        result["missing"] = True
        return result

    rows: list[dict[str, Any]] = []
    changed = False
    for line_no, line in enumerate(runs_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            continue
        old_path = row.get("report_path")
        if isinstance(old_path, str) and old_path and not Path(old_path).exists():
            result["stale_paths"] += 1
            new_path = resolve_archived_report_path(topic_dir, old_path)
            if new_path and Path(new_path).exists():
                result["repairable_paths"] += 1
                result["replacements"].append(
                    {
                        "line": line_no,
                        "mode": row.get("mode"),
                        "old": old_path,
                        "new": new_path,
                    }
                )
                if apply:
                    row["report_path"] = new_path
                    changed = True
            else:
                result["unresolved_paths"].append({"line": line_no, "mode": row.get("mode"), "path": old_path})
        rows.append(row)

    if apply and changed:
        runs_path.write_text(
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )
        result["repaired_paths"] = result["repairable_paths"]
    return result
