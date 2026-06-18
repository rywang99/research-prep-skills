#!/usr/bin/env python3
"""Synchronize Codex-style skills into Claude Code project skills.

The repository keeps `.agents/skills` as the source of truth. Claude Code
loads project skills from `.claude/skills`, so this script builds a generated
mirror that omits Codex/OpenAI-only UI metadata.
"""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SKILLS = ROOT / ".agents" / "skills"
CLAUDE_DIR = ROOT / ".claude"
TARGET_SKILLS = CLAUDE_DIR / "skills"
MANIFEST_NAME = ".generated-from-agents.json"
EXCLUDED_DIRS = {"agents", "__pycache__"}
EXCLUDED_FILES = {".DS_Store"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_source_files(skill_dir: Path) -> Iterable[Path]:
    for path in sorted(skill_dir.rglob("*")):
        rel = path.relative_to(skill_dir)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if path.is_file() and path.name not in EXCLUDED_FILES:
            yield path


def copy_skill(skill_dir: Path, output_dir: Path) -> dict[str, object]:
    target_dir = output_dir / skill_dir.name
    files: list[dict[str, str]] = []
    for src in iter_source_files(skill_dir):
        rel = src.relative_to(skill_dir)
        dst = target_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        files.append({"path": rel.as_posix(), "sha256": sha256_file(src)})
    return {"name": skill_dir.name, "files": files}


def build_mirror(output_dir: Path) -> dict[str, object]:
    if not SOURCE_SKILLS.is_dir():
        raise FileNotFoundError(f"missing source skills dir: {SOURCE_SKILLS}")
    output_dir.mkdir(parents=True, exist_ok=True)
    skills = []
    for skill_dir in sorted(p for p in SOURCE_SKILLS.iterdir() if p.is_dir()):
        if not (skill_dir / "SKILL.md").exists():
            continue
        skills.append(copy_skill(skill_dir, output_dir))
    manifest = {
        "source": ".agents/skills",
        "target": ".claude/skills",
        "generated_by": "scripts/sync_claude_skills.py",
        "note": "Generated mirror for Claude Code project skills. Do not edit by hand; update .agents/skills and rerun the sync script.",
        "skills": skills,
    }
    (output_dir / MANIFEST_NAME).write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def compare_dirs(expected: Path, actual: Path) -> list[str]:
    if not actual.exists():
        return [f"missing {actual.relative_to(ROOT)}"]
    problems: list[str] = []
    expected_files = {p.relative_to(expected) for p in expected.rglob("*") if p.is_file()}
    actual_files = {p.relative_to(actual) for p in actual.rglob("*") if p.is_file()}
    for rel in sorted(expected_files - actual_files):
        problems.append(f"missing .claude/skills/{rel.as_posix()}")
    for rel in sorted(actual_files - expected_files):
        problems.append(f"unexpected .claude/skills/{rel.as_posix()}")
    for rel in sorted(expected_files & actual_files):
        if not filecmp.cmp(expected / rel, actual / rel, shallow=False):
            problems.append(f"out of date .claude/skills/{rel.as_posix()}")
    return problems


def sync() -> None:
    if TARGET_SKILLS.exists():
        shutil.rmtree(TARGET_SKILLS)
    TARGET_SKILLS.mkdir(parents=True, exist_ok=True)
    build_mirror(TARGET_SKILLS)
    print(f"synced {SOURCE_SKILLS.relative_to(ROOT)} -> {TARGET_SKILLS.relative_to(ROOT)}")


def check() -> int:
    with tempfile.TemporaryDirectory(prefix="claude-skills-") as tmp:
        expected = Path(tmp) / "skills"
        build_mirror(expected)
        problems = compare_dirs(expected, TARGET_SKILLS)
    if problems:
        print("Claude skills mirror is out of sync. Run: python3 scripts/sync_claude_skills.py", file=sys.stderr)
        for problem in problems[:50]:
            print(f"ERROR: {problem}", file=sys.stderr)
        if len(problems) > 50:
            print(f"ERROR: ... and {len(problems) - 50} more", file=sys.stderr)
        return 1
    print("Claude skills mirror is in sync")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync .agents/skills into .claude/skills for Claude Code.")
    parser.add_argument("--check", action="store_true", help="Verify the generated mirror without writing files")
    args = parser.parse_args()
    if args.check:
        return check()
    sync()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
