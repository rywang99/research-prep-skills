#!/usr/bin/env python3
"""Render an auto-research JSON report into a standalone HTML file.

The script intentionally uses only the Python standard library so the skills
library works in fresh repositories without dependency installation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any, Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
COMMON_DIR = SCRIPT_DIR.parent
DEFAULT_TEMPLATE = COMMON_DIR / "assets" / "report_template.html"
DEFAULT_CONFIG = COMMON_DIR / "config" / "research_modes.json"
DEFAULT_KB_ROOT = Path("knowledge_base")

FALLBACK_CONFIG = {
    "modes": {
        "daily": {"label": "日调研"},
        "weekly": {"label": "周调研"},
        "monthly": {"label": "月调研"},
        "yearly-hotwords": {"label": "近一年热词分析"},
        "yearly-trends": {"label": "近一年趋势分析"},
    },
    "nav_sections": [
        {"anchor": "overview", "label": "总览"},
        {"anchor": "findings", "label": "核心发现"},
        {"anchor": "keywords", "label": "研究热词"},
        {"anchor": "trends", "label": "趋势聚类"},
        {"anchor": "analysis", "label": "补充分析"},
        {"anchor": "risks", "label": "风险与限制"},
        {"anchor": "next", "label": "后续追踪"},
        {"anchor": "queries", "label": "检索式"},
        {"anchor": "refs", "label": "参考来源"},
    ],
    "source_types": {},
    "tones": ["blue", "green", "amber", "red", "purple"],
}


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def today() -> str:
    return dt.date.today().isoformat()


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def esc(value: Any) -> str:
    return html.escape(text(value), quote=True)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    if slug:
        return slug[:80]
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]
    return f"topic-{digest}"


def load_config(path: Path | None = None) -> dict[str, Any]:
    config_path = path or DEFAULT_CONFIG
    if not config_path.exists():
        return FALLBACK_CONFIG
    with config_path.open("r", encoding="utf-8") as f:
        loaded = json.load(f)
    if not isinstance(loaded, dict):
        raise ValueError("config JSON must be an object")
    config = dict(FALLBACK_CONFIG)
    config.update(loaded)
    config.setdefault("modes", FALLBACK_CONFIG["modes"])
    config.setdefault("nav_sections", FALLBACK_CONFIG["nav_sections"])
    config.setdefault("source_types", {})
    config.setdefault("tones", FALLBACK_CONFIG["tones"])
    return config


def mode_label(mode: str, config: dict[str, Any]) -> str:
    modes = config.get("modes") if isinstance(config.get("modes"), dict) else {}
    entry = modes.get(mode) if isinstance(modes.get(mode), dict) else {}
    return text(entry.get("label") or mode)


def allowed_tones(config: dict[str, Any]) -> set[str]:
    values = config.get("tones")
    return {text(v) for v in values} if isinstance(values, list) else set(FALLBACK_CONFIG["tones"])



def source_type_label(source_type: str, config: dict[str, Any]) -> str:
    labels = config.get("source_types") if isinstance(config.get("source_types"), dict) else {}
    return text(labels.get(source_type) or source_type)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("report JSON must be an object")
    for field in ("topic", "mode"):
        if not data.get(field):
            raise ValueError(f"missing required field: {field}")
    return data


def source_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for idx, src in enumerate(as_list(data.get("sources")), 1):
        if isinstance(src, dict):
            sid = text(src.get("id") or f"src-{idx}")
            result[sid] = src
    return result


def source_links(ids: Iterable[Any], sources: dict[str, dict[str, Any]]) -> str:
    links: list[str] = []
    for sid in ids:
        sid_text = text(sid)
        src = sources.get(sid_text)
        if not src:
            links.append(f"<code>{esc(sid_text)}</code>")
            continue
        title = src.get("title") or sid_text
        url = src.get("url")
        label = esc(title)
        if url:
            links.append(f'<a href="{esc(url)}" target="_blank">{label}</a>')
        else:
            links.append(label)
    return "<br>".join(links) if links else "-"


def tags_html(tags: Iterable[Any], extra_class: str = "") -> str:
    chunks = []
    for tag in tags:
        cls = f"badge {extra_class}".strip()
        chunks.append(f'<span class="{esc(cls)}">{esc(tag)}</span>')
    return " ".join(chunks)


def nav_item(anchor: str, label: str, sec: bool = True) -> str:
    cls = "sec" if sec else "sub"
    return f'<a href="#{esc(anchor)}" class="{cls}">{esc(label)}</a>'


def render_metrics(data: dict[str, Any]) -> str:
    metrics = as_list(data.get("metrics"))
    if not metrics:
        metrics = [
            {"label": "来源", "value": len(as_list(data.get("sources"))), "note": "已记录来源数"},
            {"label": "发现", "value": len(as_list(data.get("findings"))), "note": "核心动态/发现"},
            {"label": "热词", "value": len(as_list(data.get("keywords"))), "note": "候选关键词"},
            {"label": "趋势", "value": len(as_list(data.get("trend_clusters"))), "note": "趋势聚类"},
        ]
    cards = []
    for metric in metrics:
        if not isinstance(metric, dict):
            continue
        cards.append(
            '<div class="metric">'
            f'<strong>{esc(metric.get("value", "-"))}</strong>'
            f'<span>{esc(metric.get("label", "指标"))}: {esc(metric.get("note", ""))}</span>'
            '</div>'
        )
    return '<div class="metric-grid">' + "\n".join(cards) + '</div>' if cards else ""


def render_profile(profile: dict[str, Any]) -> str:
    if not profile:
        return ""
    rows = []
    labels = [
        ("aliases", "别名/英文名"),
        ("subtopics", "子方向"),
        ("broader_terms", "上位概念"),
        ("exclusions", "排除词"),
        ("likely_sources", "优先信源"),
    ]
    for key, label in labels:
        vals = as_list(profile.get(key))
        if vals:
            rows.append(f"<tr><th>{esc(label)}</th><td>{tags_html(vals)}</td></tr>")
    if not rows:
        return ""
    return '<div class="card blue"><h3>领域 Profile</h3><table><tbody>' + "\n".join(rows) + '</tbody></table></div>'


def render_summary(data: dict[str, Any], sources: dict[str, dict[str, Any]], config: dict[str, Any]) -> str:
    cards = []
    for idx, item in enumerate(as_list(data.get("summary_judgments")), 1):
        if not isinstance(item, dict):
            continue
        tone = text(item.get("tone") or "green")
        if tone not in allowed_tones(config):
            tone = "green"
        src_html = source_links(as_list(item.get("sources")), sources)
        cards.append(
            f'<div class="card {esc(tone)}">'
            f'<h3>{idx}. {esc(item.get("title", "核心判断"))}</h3>'
            f'<p>{esc(item.get("body", ""))}</p>'
            f'<p class="section-desc">证据：{src_html}</p>'
            '</div>'
        )
    return "\n".join(cards)


def render_findings(data: dict[str, Any], sources: dict[str, dict[str, Any]], config: dict[str, Any]) -> str:
    rows = []
    for item in as_list(data.get("findings")):
        if not isinstance(item, dict):
            continue
        category = text(item.get("category") or "other")
        confidence = text(item.get("confidence") or "medium")
        rows.append(
            "<tr>"
            f"<td>{esc(item.get('date', '-'))}</td>"
            f"<td>{tags_html([source_type_label(category, config)], category)} {tags_html(as_list(item.get('tags')))}</td>"
            f"<td><strong>{esc(item.get('title', ''))}</strong><br>{esc(item.get('summary', ''))}</td>"
            f"<td>{esc(item.get('importance', ''))}</td>"
            f"<td>{tags_html([confidence], confidence)}</td>"
            f"<td>{source_links(as_list(item.get('source_ids')), sources)}</td>"
            "</tr>"
        )
    if not rows:
        return ""
    return (
        '<h2 id="findings">核心发现</h2>'
        '<table><thead><tr><th>日期</th><th>类型/标签</th><th>发现</th><th>重要性</th><th>置信度</th><th>来源</th></tr></thead><tbody>'
        + "\n".join(rows)
        + '</tbody></table>'
    )


def render_keywords(data: dict[str, Any], sources: dict[str, dict[str, Any]]) -> str:
    rows = []
    for item in as_list(data.get("keywords")):
        if not isinstance(item, dict):
            continue
        rows.append(
            "<tr>"
            f"<td><strong>{esc(item.get('term', ''))}</strong><br>{tags_html(as_list(item.get('aliases')))}</td>"
            f"<td>{esc(item.get('meaning', ''))}</td>"
            f"<td>{esc(item.get('frequency_signal', ''))}</td>"
            f"<td>{esc(item.get('growth_signal', ''))}</td>"
            f"<td>{esc(item.get('source_spread', ''))}</td>"
            f"<td>{esc(item.get('evidence_count', ''))}</td>"
            f"<td>{source_links(as_list(item.get('source_ids')), sources)}</td>"
            "</tr>"
        )
    if not rows:
        return ""
    return (
        '<h2 id="keywords">研究热词</h2>'
        '<table><thead><tr><th>热词</th><th>含义</th><th>频次信号</th><th>增长信号</th><th>信源覆盖</th><th>证据数</th><th>代表来源</th></tr></thead><tbody>'
        + "\n".join(rows)
        + '</tbody></table>'
    )


def render_trends(data: dict[str, Any], sources: dict[str, dict[str, Any]]) -> str:
    cards = []
    for idx, item in enumerate(as_list(data.get("trend_clusters")), 1):
        if not isinstance(item, dict):
            continue
        strength = text(item.get("evidence_strength") or "medium")
        tone = {"strong": "green", "medium": "blue", "weak": "amber"}.get(strength, "blue")
        rows = [
            ("驱动因素", as_list(item.get("drivers"))),
            ("机会", as_list(item.get("opportunities"))),
            ("风险", as_list(item.get("risks"))),
            ("观察点", as_list(item.get("watchpoints"))),
        ]
        body = [f'<p>{esc(item.get("thesis", ""))}</p>']
        body.append(f'<p>{tags_html(["证据: " + strength, "成熟度: " + text(item.get("maturity"), "unknown")])}</p>')
        for label, values in rows:
            if values:
                body.append(f'<p><strong>{esc(label)}：</strong>{esc("；".join(map(str, values)))}</p>')
        body.append(f'<p class="section-desc">证据：{source_links(as_list(item.get("source_ids")), sources)}</p>')
        cards.append(f'<div class="card {tone}"><h3>{idx}. {esc(item.get("name", "趋势"))}</h3>' + "\n".join(body) + '</div>')
    if not cards:
        return ""
    return '<h2 id="trends">趋势聚类</h2>' + "\n".join(cards)


def render_extra_sections(data: dict[str, Any], config: dict[str, Any]) -> str:
    chunks = []
    for idx, section in enumerate(as_list(data.get("sections")), 1):
        if not isinstance(section, dict):
            continue
        tone = text(section.get("tone") or "blue")
        if tone not in allowed_tones(config):
            tone = "blue"
        body = []
        for item in as_list(section.get("items")):
            if isinstance(item, dict):
                title = item.get("title")
                content = item.get("body") or item.get("content") or ""
                body.append(f'<p><strong>{esc(title)}</strong> {esc(content)}</p>')
            else:
                body.append(f'<p>{esc(item)}</p>')
        chunks.append(f'<div class="card {tone}" id="extra-{idx}"><h3>{esc(section.get("title", "补充分析"))}</h3>' + "\n".join(body) + '</div>')
    if not chunks:
        return ""
    return '<h2 id="analysis">补充分析</h2>' + "\n".join(chunks)


def render_list_section(anchor: str, title: str, items: list[Any]) -> str:
    if not items:
        return ""
    lis = "\n".join(f"<li>{esc(item)}</li>" for item in items)
    return f'<h2 id="{esc(anchor)}">{esc(title)}</h2><ul>{lis}</ul>'


def render_queries(data: dict[str, Any]) -> str:
    rows = []
    for q in as_list(data.get("queries")):
        if isinstance(q, dict):
            rows.append(f"<tr><td><code>{esc(q.get('query', ''))}</code></td><td>{esc(q.get('purpose', ''))}</td><td>{esc(q.get('source', 'web'))}</td></tr>")
        else:
            rows.append(f"<tr><td><code>{esc(q)}</code></td><td>-</td><td>web</td></tr>")
    if not rows:
        return ""
    return '<h2 id="queries">检索式</h2><table><thead><tr><th>Query</th><th>目的</th><th>渠道</th></tr></thead><tbody>' + "\n".join(rows) + '</tbody></table>'


def render_sources(data: dict[str, Any], config: dict[str, Any]) -> str:
    lis = []
    for idx, src in enumerate(as_list(data.get("sources")), 1):
        if not isinstance(src, dict):
            continue
        stype = text(src.get("source_type") or "other")
        confidence = text(src.get("confidence") or "medium")
        url = src.get("url")
        title = esc(src.get("title") or f"Source {idx}")
        title_html = f'<a href="{esc(url)}" target="_blank">{title}</a>' if url else title
        meta = []
        for key in ("authors_or_org", "published_at", "accessed_at"):
            if src.get(key):
                meta.append(text(src.get(key)))
        lis.append(
            '<li>'
            f'{tags_html([source_type_label(stype, config)], stype)} {tags_html([confidence], confidence)} {title_html}'
            f'<br><span class="section-desc">{esc(" · ".join(meta))}</span>'
            f'<br>{esc(src.get("summary", ""))}'
            '</li>'
        )
    if not lis:
        return ""
    return '<h2 id="refs">参考来源</h2><ul class="ref-list">' + "\n".join(lis) + '</ul>'


def render_report(data: dict[str, Any], template: str, config: dict[str, Any] | None = None) -> str:
    data.setdefault("generated_at", now_iso())
    data.setdefault("snapshot_date", today())
    config = config or load_config()
    mode = text(data.get("mode"))
    label = mode_label(mode, config)
    window = data.get("time_window") if isinstance(data.get("time_window"), dict) else {}
    title = f"{data.get('topic')} - {label}"
    sources = source_map(data)

    nav_entries = config.get("nav_sections") if isinstance(config.get("nav_sections"), list) else FALLBACK_CONFIG["nav_sections"]
    nav = "\n".join(
        nav_item(text(item.get("anchor", "overview")), text(item.get("label", "Section")))
        for item in nav_entries
        if isinstance(item, dict)
    )

    meta = [
        f"模式：{label}",
        f"快照：{data.get('snapshot_date')}",
        f"窗口：{window.get('label', '-')}",
        f"来源数：{len(as_list(data.get('sources')))}",
    ]
    if window.get("start") or window.get("end"):
        meta.append(f"日期：{window.get('start', '?')} 至 {window.get('end', '?')}")
    meta_html = '<div class="meta">' + "".join(f"<span>{esc(m)}</span>" for m in meta) + '</div>'

    content_parts = [
        '<h1 id="overview">' + esc(title) + '</h1>',
        f'<p class="section-desc">自动化调研快照：{esc(data.get("snapshot_date"))}；面向研究领域：{esc(data.get("topic"))}。</p>',
        meta_html,
        render_summary(data, sources, config),
        render_metrics(data),
        render_profile(data.get("topic_profile") if isinstance(data.get("topic_profile"), dict) else {}),
        render_findings(data, sources, config),
        render_keywords(data, sources),
        render_trends(data, sources),
        render_extra_sections(data, config),
        render_list_section("risks", "风险与限制", as_list(data.get("risks"))),
        render_list_section("next", "后续追踪", as_list(data.get("next_queries"))),
        render_queries(data),
        render_sources(data, config),
    ]
    content = "\n".join(part for part in content_parts if part)
    return template.replace("{{title}}", esc(title)).replace("{{nav}}", nav).replace("{{content}}", content)


def append_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def update_kb(data: dict[str, Any], output: Path, kb_root: Path) -> None:
    topic_slug = text(data.get("topic_slug") or slugify(text(data.get("topic"))))
    run_id = hashlib.sha1(f"{topic_slug}:{data.get('mode')}:{data.get('generated_at')}".encode("utf-8")).hexdigest()[:12]
    topic_dir = kb_root / topic_slug
    topic_dir.mkdir(parents=True, exist_ok=True)

    source_rows = []
    for src in as_list(data.get("sources")):
        if isinstance(src, dict):
            row = dict(src)
            row.update({"topic": data.get("topic"), "mode": data.get("mode"), "run_id": run_id, "recorded_at": now_iso()})
            source_rows.append(row)
    append_jsonl(topic_dir / "sources.jsonl", source_rows)

    keywords_doc = {
        "topic": data.get("topic"),
        "topic_slug": topic_slug,
        "updated_at": now_iso(),
        "mode": data.get("mode"),
        "time_window": data.get("time_window"),
        "keywords": as_list(data.get("keywords")),
    }
    (topic_dir / "keywords.json").write_text(json.dumps(keywords_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    run_row = {
        "run_id": run_id,
        "topic": data.get("topic"),
        "topic_slug": topic_slug,
        "mode": data.get("mode"),
        "generated_at": data.get("generated_at"),
        "snapshot_date": data.get("snapshot_date"),
        "time_window": data.get("time_window"),
        "report_path": str(output),
        "source_count": len(as_list(data.get("sources"))),
        "finding_count": len(as_list(data.get("findings"))),
        "keyword_count": len(as_list(data.get("keywords"))),
        "trend_count": len(as_list(data.get("trend_clusters"))),
    }
    append_jsonl(topic_dir / "runs.jsonl", [run_row])


def main() -> int:
    parser = argparse.ArgumentParser(description="Render auto-research report JSON to HTML.")
    parser.add_argument("--input", required=True, type=Path, help="Input report JSON path")
    parser.add_argument("--output", required=True, type=Path, help="Output HTML path")
    parser.add_argument("--template", default=DEFAULT_TEMPLATE, type=Path, help="HTML template path")
    parser.add_argument("--config", default=DEFAULT_CONFIG, type=Path, help="Research mode/config registry path")
    parser.add_argument("--update-kb", action="store_true", help="Append sources/runs and keyword snapshot to knowledge_base")
    parser.add_argument("--kb-root", default=DEFAULT_KB_ROOT, type=Path, help="Knowledge base root")
    args = parser.parse_args()

    data = load_json(args.input)
    data.setdefault("topic_slug", slugify(text(data.get("topic"))))
    template = args.template.read_text(encoding="utf-8")
    config = load_config(args.config)
    html_text = render_report(data, template, config)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html_text, encoding="utf-8")
    if args.update_kb:
        update_kb(data, args.output, args.kb_root)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
