#!/usr/bin/env python3
"""Scaffold a new auto-research mode skill and register it in config."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
CONFIG_PATH = SKILLS / "auto-research-common" / "config" / "research_modes.json"


def slugify_mode(value: str) -> str:
    mode = re.sub(r"[^a-z0-9-]+", "-", value.strip().lower()).strip("-")
    if not mode:
        raise ValueError("mode must contain at least one ASCII letter or number")
    if mode.startswith("research-"):
        mode = mode.removeprefix("research-")
    return mode


def write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create and register a new research mode skill.")
    parser.add_argument("mode", help="Mode id, e.g. quarterly or conference-watch")
    parser.add_argument("--label", required=True, help="Chinese display label, e.g. 季度调研")
    parser.add_argument("--window-days", type=int, default=90, help="Default rolling window in days")
    parser.add_argument("--description", default="Custom automated research mode", help="Short mode description")
    parser.add_argument("--brand-color", default="#2563EB", help="Skill UI brand color")
    args = parser.parse_args()

    mode = slugify_mode(args.mode)
    skill_name = f"research-{mode}"
    skill_dir = SKILLS / skill_name
    if skill_dir.exists():
        raise FileExistsError(f"skill already exists: {skill_dir}")

    skill_md = f'''---
name: {skill_name}
description: Produce a custom automated research report for mode "{mode}" with source-backed findings, local knowledge-base updates, and HTML output.
---

# {args.label}

Use this skill for {args.description}.

## Window

- Default: rolling last {args.window_days} days.
- State exact start and end dates in the report.

## Search plan

- Reuse the topic profile from `auto-research` or create one if invoked directly.
- Follow `../auto-research-common/references/source_policy.md`.
- Save findings with the schema in `../auto-research-common/references/report_schema.md`.

## Report content

- Explain what changed, why it matters, confidence, risks, and next queries.
- Use `sections` for mode-specific analysis until a custom renderer section is needed.

## Output

Build report JSON with `mode: "{mode}"`, then render using `../auto-research-common/scripts/render_report.py`.
'''
    openai_yaml = f'''interface:
  display_name: "{args.label}"
  short_description: "{args.description[:48]}"
  brand_color: "{args.brand_color}"
  default_prompt: "Use ${skill_name} to generate a sourced {args.label} report for a research domain."
policy:
  allow_implicit_invocation: true
'''
    write_if_missing(skill_dir / "SKILL.md", skill_md)
    write_if_missing(skill_dir / "agents" / "openai.yaml", openai_yaml)

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    config.setdefault("modes", {})[mode] = {
        "label": args.label,
        "skill": skill_name,
        "default_window_days": args.window_days,
        "description": args.description,
    }
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"created {skill_dir}")
    print(f"registered mode {mode} in {CONFIG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
