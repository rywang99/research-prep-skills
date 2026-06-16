#!/usr/bin/env python3
"""Generate a standalone HTML-first technical trace for one paper."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

from paper_trace_common import (
    generate_trace,
    infer_method_short_name,
    infer_method_slug,
    infer_paper_category,
    source_from_paper_input,
    stable_id,
    today,
)

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / ".agents" / "skills" / "auto-research-common" / "scripts" / "render_report.py"
TEMPLATE = ROOT / ".agents" / "skills" / "auto-research-common" / "assets" / "report_template.html"
CONFIG = ROOT / ".agents" / "skills" / "auto-research-common" / "config" / "research_modes.json"


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_report", RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load renderer: {RENDERER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def default_output_paths(source: dict, category_slug: str, method_slug: str) -> tuple[Path, Path]:
    stem = method_slug
    base_dir = ROOT / "reports" / "paper-trace" / category_slug
    output_json = base_dir / f"{stem}.json"
    output_html = base_dir / f"{stem}.html"
    if not output_json.exists() and not output_html.exists():
        return output_json, output_html
    try:
        existing = json.loads(output_json.read_text(encoding="utf-8"))
        existing_source = (existing.get("sources") or [{}])[0]
        if existing_source.get("external_id") == source.get("external_id") and existing_source.get("title") == source.get("title"):
            return output_json, output_html
    except Exception:
        pass
    suffix = stable_id("m", f"{source.get('external_id')}:{source.get('title')}").removeprefix("m-")[:8]
    stem = f"{method_slug}-{suffix}"
    return base_dir / f"{stem}.json", base_dir / f"{stem}.html"


def main() -> int:
    parser = argparse.ArgumentParser(description="Trace one paper and write standalone JSON/HTML outputs.")
    parser.add_argument("--paper", required=True, help="arXiv ID/URL, direct PDF URL, local PDF path, or paper title")
    parser.add_argument("--topic", default="", help="Optional research topic context")
    parser.add_argument("--output-json", type=Path, help="Output JSON path")
    parser.add_argument("--output-html", type=Path, help="Output HTML path")
    parser.add_argument("--kb-root", type=Path, default=Path("knowledge_base"), help="Knowledge-base root")
    parser.add_argument("--no-update-kb", action="store_true", help="Do not append trace metadata to knowledge_base")
    parser.add_argument("--timeout", type=int, default=45, help="Network/PDF extraction timeout in seconds")
    args = parser.parse_args()

    source = source_from_paper_input(args.paper, timeout=args.timeout)
    category = infer_paper_category(source, args.topic)
    method_short_name = infer_method_short_name(source)
    method_slug = infer_method_slug(source)
    trace = generate_trace(source, topic=args.topic or category["label"], timeout=args.timeout)
    trace["display_title"] = method_short_name
    default_json, default_html = default_output_paths(source, category["slug"], method_slug)
    output_json = args.output_json or default_json
    output_html = args.output_html or default_html
    report = {
        "topic": category["label"],
        "topic_slug": category["slug"],
        "mode": "paper-trace",
        "snapshot_date": today(),
        "time_window": {"label": "单篇论文技术溯源"},
        "paper_category_label": category["label"],
        "paper_category_slug": category["slug"],
        "method_short_name": method_short_name,
        "method_slug": method_slug,
        "summary_judgments": [
            {
                "title": f"{method_short_name} 技术溯源已生成",
                "body": "分析内容以内嵌折叠区块呈现；未缓存 PDF，也未写入 PDF 批注。",
                "tone": "green",
                "sources": [source.get("id")],
            }
        ],
        "metrics": [{"label": "论文溯源", "value": "1", "note": "单篇论文标准精读"}],
        "paper_traces": [trace],
        "risks": ["自动 trace 依赖可获取的摘要或临时全文抽取结果；请以原论文为准复核关键实验和结论。"],
        "next_queries": trace.get("follow_up_queries", []),
        "sources": [source],
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    renderer = load_renderer()
    config = renderer.load_config(CONFIG)
    html = renderer.render_report(report, TEMPLATE.read_text(encoding="utf-8"), config)
    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(html, encoding="utf-8")
    if not args.no_update_kb:
        renderer.update_kb(report, output_html, args.kb_root)
    print(json.dumps({"json": str(output_json), "html": str(output_html), "kb_updated": not args.no_update_kb}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
