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
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True

SCRIPT_DIR = Path(__file__).resolve().parent
COMMON_DIR = SCRIPT_DIR.parent
DEFAULT_TEMPLATE = COMMON_DIR / "assets" / "report_template.html"
DEFAULT_CONFIG = COMMON_DIR / "config" / "research_modes.json"
DEFAULT_KB_ROOT = Path("knowledge_base")
SCHEMA_VERSION = "1.0"
REPORT_ARCHIVE = SCRIPT_DIR / "report_archive.py"

FALLBACK_CONFIG = {
    "modes": {
        "daily": {"label": "日调研"},
        "weekly": {"label": "周调研"},
        "monthly": {"label": "月调研"},
        "yearly-hotwords": {"label": "近一年热词分析"},
        "yearly-trends": {"label": "近一年趋势分析"},
        "gap-analysis": {"label": "研究缺口分析"},
        "idea-planning": {"label": "研究 idea 规划"},
        "experiment-roadmap": {"label": "实验路线图"},
        "formula-derivation": {"label": "公式推导准备"},
        "paper-trace": {"label": "论文溯源"},
        "yearly-full-cycle": {"label": "全年全流程调研"},
        "independent-evaluation": {"label": "独立评分"},
    },
    "nav_sections": [
        {"anchor": "overview", "label": "总览"},
        {"anchor": "cycle", "label": "全年流程"},
        {"anchor": "findings", "label": "核心发现"},
        {"anchor": "paper-traces", "label": "论文溯源"},
        {"anchor": "keywords", "label": "研究热词"},
        {"anchor": "trends", "label": "趋势聚类"},
        {"anchor": "gaps", "label": "研究缺口"},
        {"anchor": "ideas", "label": "Idea 规划"},
        {"anchor": "roadmap", "label": "实验路线"},
        {"anchor": "evaluation", "label": "独立评分"},
        {"anchor": "iterations", "label": "迭代记录"},
        {"anchor": "derivation", "label": "公式推导"},
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


def light_update_mode(mode: str) -> bool:
    return mode in {"daily", "weekly"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("report JSON must be an object")
    for field in ("topic", "mode"):
        if not data.get(field):
            raise ValueError(f"missing required field: {field}")
    return data


def load_archive_module():
    spec = importlib.util.spec_from_file_location("report_archive", REPORT_ARCHIVE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load archive module: {REPORT_ARCHIVE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def render_value_list(title: str, values: list[Any]) -> str:
    if not values:
        return ""
    items = []
    for value in values:
        if isinstance(value, dict):
            label = value.get("category") or value.get("title") or "item"
            body = value.get("statement") or value.get("quote_or_signal") or value.get("body") or value.get("content") or ""
            why = value.get("why_read") or value.get("reason") or ""
            items.append(f"<li><strong>{esc(label)}：</strong>{esc(body)}<br><span class=\"section-desc\">{esc(why)}</span></li>")
        else:
            items.append(f"<li>{esc(value)}</li>")
    return f"<h4>{esc(title)}</h4><ul>" + "\n".join(items) + "</ul>"


def render_paper_traces(data: dict[str, Any], sources: dict[str, dict[str, Any]]) -> str:
    cards = []
    standalone_single = text(data.get("mode")) == "paper-trace" and len(as_list(data.get("paper_traces"))) == 1
    for idx, trace in enumerate(as_list(data.get("paper_traces")), 1):
        if not isinstance(trace, dict):
            continue
        source_id = text(trace.get("source_id"))
        source = sources.get(source_id) if source_id else None
        url = source.get("url") if isinstance(source, dict) else trace.get("url")
        src_html = f'<a href="{esc(url)}" target="_blank">查看论文来源</a>' if url else "-"
        meta = []
        if trace.get("published_at"):
            meta.append(f"发布日期：{text(trace.get('published_at'))}")
        status_label = {"ok": "已生成中文溯源", "metadata_only": "仅基于元数据", "failed": "生成失败"}.get(text(trace.get("trace_status")), text(trace.get("trace_status")))
        if status_label:
            meta.append(f"状态：{status_label}")
        extraction_label = {"pdf_temp_pdftotext": "临时全文抽取", "metadata_summary": "摘要/元数据", "other": "其他"}.get(text(trace.get("extraction_status")), text(trace.get("extraction_status")))
        if extraction_label:
            meta.append(f"依据：{extraction_label}")
        body = [
            f'<p class="section-desc">来源：{src_html}</p>',
            f'<p class="section-desc">{esc(" · ".join(meta))}</p>' if meta else "",
            f'<p><strong>一句话定位：</strong>{esc(trace.get("one_sentence_position", ""))}</p>',
            f'<p><strong>核心问题：</strong>{esc(trace.get("core_problem", ""))}</p>',
            render_value_list("方法脉络", as_list(trace.get("technical_lineage"))),
            render_value_list("方法差异", as_list(trace.get("method_delta"))),
            render_value_list("实验协议", as_list(trace.get("experiment_protocol"))),
            render_value_list("复现风险", as_list(trace.get("reproducibility_risks"))),
            render_value_list("重点阅读信号", as_list(trace.get("reading_points"))),
            render_value_list("后续追踪建议", as_list(trace.get("follow_up_queries"))),
        ]
        title = trace.get("display_title") or f"论文 {idx} 技术溯源"
        card_title = esc(title) if standalone_single else f"{idx}. {esc(title)}"
        cards.append(
            '<section class="trace-card">'
            f'<h3>{card_title}</h3>'
            + "\n".join(part for part in body if part)
            + "</section>"
        )
    if not cards:
        return ""
    return '<h2 id="paper-traces">论文溯源</h2><p class="section-desc">以下分析默认展开展示；未缓存原始文件，也未写入文件批注。</p>' + "\n".join(cards)


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


def render_gaps(data: dict[str, Any], sources: dict[str, dict[str, Any]]) -> str:
    cards = []
    for idx, item in enumerate(as_list(data.get("gaps")), 1):
        if not isinstance(item, dict):
            continue
        confidence = text(item.get("confidence") or "medium")
        tone = {"high": "red", "medium": "amber", "low": "blue"}.get(confidence, "amber")
        body = [
            f'<p>{esc(item.get("description", ""))}</p>',
            f'<p>{tags_html([text(item.get("gap_type"), "gap"), "可信度: " + confidence])} {tags_html(as_list(item.get("tags")))}</p>',
        ]
        for label, key in [
            ("为什么重要", "why_it_matters"),
            ("最接近工作", "closest_work"),
            ("可验证机会", "actionable_opportunity"),
            ("风险", "risk"),
        ]:
            if item.get(key):
                body.append(f'<p><strong>{esc(label)}：</strong>{esc(item.get(key))}</p>')
        body.append(f'<p class="section-desc">证据：{source_links(as_list(item.get("source_ids")), sources)}</p>')
        cards.append(f'<div class="card {tone}"><h3>{idx}. {esc(item.get("name", "研究缺口"))}</h3>' + "\n".join(body) + '</div>')
    if not cards:
        return ""
    return '<h2 id="gaps">研究缺口</h2>' + "\n".join(cards)


def render_ideas(data: dict[str, Any], sources: dict[str, dict[str, Any]]) -> str:
    rows = []
    for item in as_list(data.get("ideas")):
        if not isinstance(item, dict):
            continue
        novelty_parts = []
        if item.get("novelty_verdict"):
            novelty_parts.append("查新: " + text(item.get("novelty_verdict")))
        if item.get("closest_prior_work"):
            novelty_parts.append("最近工作: " + text(item.get("closest_prior_work")))
        if item.get("novelty_evidence"):
            novelty_parts.append("证据: " + "；".join(map(str, as_list(item.get("novelty_evidence")))))
        if item.get("novelty_risk"):
            novelty_parts.append("风险: " + text(item.get("novelty_risk")))
        novelty_html = "<br>".join(esc(part) for part in novelty_parts) or esc(item.get("novelty_delta", ""))
        rows.append(
            "<tr>"
            f"<td><strong>{esc(item.get('name', 'Idea'))}</strong><br>{tags_html(as_list(item.get('tags')))}</td>"
            f"<td>{esc(item.get('problem_anchor', ''))}</td>"
            f"<td>{esc(item.get('core_mechanism', ''))}</td>"
            f"<td>{novelty_html}</td>"
            f"<td>{esc(item.get('validation_path', ''))}</td>"
            f"<td>{tags_html([text(item.get('priority'), 'medium'), '风险: ' + text(item.get('risk'), 'unknown')])}</td>"
            f"<td>{source_links(as_list(item.get('source_ids')), sources)}</td>"
            "</tr>"
        )
    if not rows:
        return ""
    return (
        '<h2 id="ideas">Idea 规划</h2>'
        '<table><thead><tr><th>Idea</th><th>问题锚点</th><th>核心机制</th><th>创新差异</th><th>最小验证路径</th><th>优先级/风险</th><th>来源</th></tr></thead><tbody>'
        + "\n".join(rows)
        + '</tbody></table>'
    )


def render_formula_derivation(data: dict[str, Any]) -> str:
    derivation = data.get("formula_derivation")
    if not isinstance(derivation, dict):
        return ""
    chunks = ['<h2 id="derivation">公式推导准备</h2>']
    if derivation.get("problem_setup"):
        chunks.append(f'<p>{esc(derivation.get("problem_setup"))}</p>')
    assumptions = as_list(derivation.get("assumptions"))
    if assumptions:
        chunks.append('<h3>假设边界</h3><ul>' + "\n".join(f"<li>{esc(item)}</li>" for item in assumptions) + '</ul>')
    symbol_rows = []
    for item in as_list(derivation.get("symbols")):
        if not isinstance(item, dict):
            continue
        symbol_rows.append(
            "<tr>"
            f"<td><code>{esc(item.get('symbol', ''))}</code></td>"
            f"<td>{esc(item.get('meaning', ''))}</td>"
            f"<td>{esc(item.get('domain', ''))}</td>"
            "</tr>"
        )
    if symbol_rows:
        chunks.append('<h3>符号表</h3><table><thead><tr><th>符号</th><th>含义</th><th>定义域/约束</th></tr></thead><tbody>' + "\n".join(symbol_rows) + '</tbody></table>')
    step_rows = []
    for item in as_list(derivation.get("derivation_steps")):
        if not isinstance(item, dict):
            continue
        step_rows.append(
            "<tr>"
            f"<td><strong>{esc(item.get('id', ''))}</strong></td>"
            f"<td>{esc(item.get('statement', ''))}</td>"
            f"<td>{esc(item.get('justification', ''))}</td>"
            f"<td>{esc(item.get('depends_on', ''))}</td>"
            "</tr>"
        )
    if step_rows:
        chunks.append('<h3>推导步骤</h3><table><thead><tr><th>步骤</th><th>表达/结论</th><th>依据</th><th>依赖</th></tr></thead><tbody>' + "\n".join(step_rows) + '</tbody></table>')
    for label, key in [
        ("Sanity Checks", "sanity_checks"),
        ("失败模式", "failure_modes"),
        ("下一步验证", "next_validation"),
    ]:
        items = as_list(derivation.get(key))
        if items:
            chunks.append(f'<h3>{esc(label)}</h3><ul>' + "\n".join(f"<li>{esc(item)}</li>" for item in items) + '</ul>')
    return "\n".join(chunks)


def render_experiment_roadmap(data: dict[str, Any]) -> str:
    roadmap = data.get("experiment_roadmap")
    if not isinstance(roadmap, dict):
        return ""
    chunks = ['<h2 id="roadmap">实验路线图</h2>']
    claims = []
    for claim in as_list(roadmap.get("claims")):
        if not isinstance(claim, dict):
            continue
        claims.append(
            "<tr>"
            f"<td><strong>{esc(claim.get('id', '-'))}</strong></td>"
            f"<td>{esc(claim.get('claim', ''))}</td>"
            f"<td>{esc(claim.get('minimum_evidence', ''))}</td>"
            f"<td>{esc(', '.join(map(str, as_list(claim.get('blocks')))))}</td>"
            "</tr>"
        )
    if claims:
        chunks.append('<table><thead><tr><th>Claim</th><th>内容</th><th>最低可信证据</th><th>实验块</th></tr></thead><tbody>' + "\n".join(claims) + '</tbody></table>')
    blocks = []
    for idx, block in enumerate(as_list(roadmap.get("blocks")), 1):
        if not isinstance(block, dict):
            continue
        body = []
        for label, key in [
            ("验证问题", "question"),
            ("数据/任务", "dataset"),
            ("对比系统", "systems"),
            ("指标", "metrics"),
            ("成功标准", "success_criterion"),
            ("失败解释", "failure_interpretation"),
            ("图表目标", "figure_target"),
        ]:
            value = block.get(key)
            if value:
                rendered = "；".join(map(str, as_list(value))) if isinstance(value, list) else text(value)
                body.append(f'<p><strong>{esc(label)}：</strong>{esc(rendered)}</p>')
        blocks.append(f'<div class="card blue"><h3>{idx}. {esc(block.get("name", "实验块"))}</h3>' + "\n".join(body) + '</div>')
    if blocks:
        chunks.extend(blocks)
    milestones = []
    for item in as_list(roadmap.get("milestones")):
        if not isinstance(item, dict):
            continue
        milestones.append(
            "<tr>"
            f"<td><strong>{esc(item.get('name', ''))}</strong></td>"
            f"<td>{esc(item.get('goal', ''))}</td>"
            f"<td>{esc(item.get('estimated_cost', ''))}</td>"
            f"<td>{esc(item.get('gate', ''))}</td>"
            "</tr>"
        )
    if milestones:
        chunks.append('<table><thead><tr><th>阶段</th><th>目标</th><th>成本/时间</th><th>Stop/Go Gate</th></tr></thead><tbody>' + "\n".join(milestones) + '</tbody></table>')
    return "\n".join(chunks)


def render_cycle(data: dict[str, Any]) -> str:
    cycle_plan = data.get("cycle_plan") if isinstance(data.get("cycle_plan"), dict) else {}
    stage_artifacts = [item for item in as_list(data.get("stage_artifacts")) if isinstance(item, dict)]
    if not cycle_plan and not stage_artifacts:
        return ""
    chunks = ['<h2 id="cycle">全年流程</h2>']
    if cycle_plan:
        rows = []
        for label, key in [
            ("快照日期", "snapshot_date"),
            ("年度窗口", "annual_window_label"),
            ("追踪策略", "goal_strategy"),
            ("评分策略", "evaluation_strategy"),
        ]:
            if cycle_plan.get(key):
                rows.append(f"<tr><th>{esc(label)}</th><td>{esc(cycle_plan.get(key))}</td></tr>")
        stages = as_list(cycle_plan.get("stage_order"))
        if stages:
            rows.append(f"<tr><th>阶段顺序</th><td>{tags_html(stages)}</td></tr>")
        if rows:
            chunks.append('<div class="card blue"><h3>编排计划</h3><table><tbody>' + "\n".join(rows) + '</tbody></table></div>')
        slices = [item for item in as_list(cycle_plan.get("monthly_slices")) if isinstance(item, dict)]
        if slices:
            slice_rows = []
            for item in slices:
                slice_rows.append(
                    "<tr>"
                    f"<td><strong>{esc(item.get('slice_id', ''))}</strong></td>"
                    f"<td>{esc(item.get('label', ''))}</td>"
                    f"<td>{esc(item.get('start', ''))} 至 {esc(item.get('end', ''))}</td>"
                    f"<td>{esc(item.get('status', ''))}</td>"
                    f"<td>{esc(item.get('artifact_path', ''))}</td>"
                    "</tr>"
                )
            chunks.append(
                '<details class="cycle-collapsible"><summary>月度切片'
                f'（{len(slice_rows)} 条，点击展开）</summary>'
                '<table><thead><tr><th>ID</th><th>标签</th><th>窗口</th><th>状态</th><th>产物</th></tr></thead><tbody>'
                + "\n".join(slice_rows)
                + '</tbody></table></details>'
            )
    if stage_artifacts:
        rows = []
        for item in stage_artifacts:
            path_bits = [text(item.get("json_path")), text(item.get("html_path"))]
            paths = "<br>".join(esc(p) for p in path_bits if p)
            rows.append(
                "<tr>"
                f"<td><strong>{esc(item.get('stage_id', ''))}</strong></td>"
                f"<td>{esc(item.get('mode', ''))}</td>"
                f"<td>{tags_html([text(item.get('status'), 'planned')], text(item.get('status'), 'planned'))}</td>"
                f"<td>{esc(', '.join(map(str, as_list(item.get('depends_on')))))}</td>"
                f"<td>{paths}</td>"
                f"<td>{esc(item.get('notes', ''))}</td>"
                "</tr>"
            )
        chunks.append(
            '<details class="cycle-collapsible"><summary>阶段产物'
            f'（{len(rows)} 条，点击展开）</summary>'
            '<table><thead><tr><th>阶段</th><th>模式</th><th>状态</th><th>依赖</th><th>路径</th><th>备注</th></tr></thead><tbody>'
            + "\n".join(rows)
            + '</tbody></table></details>'
        )
    return "\n".join(chunks)


def render_evaluation_scorecards(data: dict[str, Any], sources: dict[str, dict[str, Any]]) -> str:
    scorecards = [item for item in as_list(data.get("evaluation_scorecards")) if isinstance(item, dict)]
    if not scorecards:
        return ""
    chunks = ['<h2 id="evaluation">独立评分</h2><p class="section-desc">评分结果与生成阶段分离；低分项用于触发后续定向迭代。</p>']
    tone_by_verdict = {
        "pass": "green",
        "pass_with_improvements": "amber",
        "needs_iteration": "red",
        "blocked": "red",
    }
    for idx, card in enumerate(scorecards, 1):
        verdict = text(card.get("verdict") or "needs_iteration")
        tone = tone_by_verdict.get(verdict, "blue")
        header = (
            f'<div class="card {tone}"><h3>{idx}. {esc(card.get("scorecard_id", "scorecard"))} '
            f'· {esc(card.get("total_score", "-"))}/100</h3>'
        )
        body = [
            f'<p>{tags_html([verdict, text(card.get("rubric_version"), "rubric")])}</p>',
            f'<p><strong>评估对象：</strong>{esc(card.get("artifact_id", ""))} · {esc(card.get("artifact_path", ""))}</p>',
            f'<p><strong>评审器：</strong>{esc(card.get("evaluator", "research-independent-evaluator"))}</p>',
        ]
        score_rows = []
        for score in as_list(card.get("scores")):
            if not isinstance(score, dict):
                continue
            score_rows.append(
                "<tr>"
                f"<td>{esc(score.get('dimension', ''))}</td>"
                f"<td>{esc(score.get('score', ''))}/{esc(score.get('max_score', ''))}</td>"
                f"<td>{esc(score.get('rationale', ''))}</td>"
                f"<td>{source_links(as_list(score.get('source_ids')), sources)}</td>"
                "</tr>"
            )
        if score_rows:
            body.append('<table><thead><tr><th>维度</th><th>得分</th><th>理由</th><th>来源</th></tr></thead><tbody>' + "\n".join(score_rows) + '</tbody></table>')
        for label, key in [("阻塞问题", "blocking_issues"), ("必要迭代", "required_iterations")]:
            values = as_list(card.get(key))
            if values:
                body.append(f'<p><strong>{esc(label)}：</strong>{esc("；".join(map(str, values)))}</p>')
        if card.get("evaluated_at"):
            body.append(f'<p class="section-desc">评估时间：{esc(card.get("evaluated_at"))}</p>')
        chunks.append(header + "\n".join(body) + '</div>')
    return "\n".join(chunks)


def render_iteration_log(data: dict[str, Any]) -> str:
    rows = []
    for item in as_list(data.get("iteration_log")):
        if not isinstance(item, dict):
            continue
        rows.append(
            "<tr>"
            f"<td><strong>{esc(item.get('iteration_id', ''))}</strong></td>"
            f"<td>{esc(item.get('stage_id', ''))}</td>"
            f"<td>{esc(item.get('trigger_scorecard_id', ''))}</td>"
            f"<td>{esc(item.get('trigger_reason', ''))}</td>"
            f"<td>{esc(item.get('action', ''))}</td>"
            f"<td>{esc(item.get('changed_artifact', ''))}</td>"
            f"<td>{esc(item.get('result_scorecard_id', ''))}</td>"
            "</tr>"
        )
    if not rows:
        return ""
    return (
        '<h2 id="iterations">迭代记录</h2>'
        '<table><thead><tr><th>迭代</th><th>阶段</th><th>触发评分</th><th>原因</th><th>动作</th><th>变更产物</th><th>复评</th></tr></thead><tbody>'
        + "\n".join(rows)
        + '</tbody></table>'
    )


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
    data.setdefault("schema_version", SCHEMA_VERSION)
    data.setdefault("generated_at", now_iso())
    data.setdefault("snapshot_date", today())
    config = config or load_config()
    mode = text(data.get("mode"))
    label = mode_label(mode, config)
    window = data.get("time_window") if isinstance(data.get("time_window"), dict) else {}
    title = f"{data.get('topic')} - {label}"
    sources = source_map(data)

    meta = [
        f"模式：{label}",
        f"快照：{data.get('snapshot_date')}",
        f"窗口：{window.get('label', '-')}",
        f"来源数：{len(as_list(data.get('sources')))}",
    ]
    if window.get("start") or window.get("end"):
        meta.append(f"日期：{window.get('start', '?')} 至 {window.get('end', '?')}")
    meta_html = '<div class="meta">' + "".join(f"<span>{esc(m)}</span>" for m in meta) + '</div>'

    keyword_html = "" if light_update_mode(mode) else render_keywords(data, sources)
    trend_html = "" if light_update_mode(mode) else render_trends(data, sources)
    content_parts = [
        ("overview", '<h1 id="overview">' + esc(title) + '</h1>'
         + f'<p class="section-desc">自动化调研快照：{esc(data.get("snapshot_date"))}；面向研究领域：{esc(data.get("topic"))}。</p>'
         + meta_html
         + render_summary(data, sources, config)
         + render_metrics(data)
         + render_profile(data.get("topic_profile") if isinstance(data.get("topic_profile"), dict) else {})),
        ("cycle", render_cycle(data)),
        ("findings", render_findings(data, sources, config)),
        ("paper-traces", render_paper_traces(data, sources)),
        ("keywords", keyword_html),
        ("trends", trend_html),
        ("gaps", render_gaps(data, sources)),
        ("ideas", render_ideas(data, sources)),
        ("roadmap", render_experiment_roadmap(data)),
        ("evaluation", render_evaluation_scorecards(data, sources)),
        ("iterations", render_iteration_log(data)),
        ("derivation", render_formula_derivation(data)),
        ("analysis", render_extra_sections(data, config)),
        ("risks", render_list_section("risks", "风险与限制", as_list(data.get("risks")))),
        ("next", render_list_section("next", "后续追踪", as_list(data.get("next_queries")))),
        ("queries", render_queries(data)),
        ("refs", render_sources(data, config)),
    ]
    active_anchors = {anchor for anchor, part in content_parts if part}
    nav_entries = config.get("nav_sections") if isinstance(config.get("nav_sections"), list) else FALLBACK_CONFIG["nav_sections"]
    nav = "\n".join(
        nav_item(text(item.get("anchor", "overview")), text(item.get("label", "Section")))
        for item in nav_entries
        if isinstance(item, dict) and text(item.get("anchor", "overview")) in active_anchors
    )
    content = "\n".join(part for _, part in content_parts if part)
    return template.replace("{{title}}", esc(title)).replace("{{nav}}", nav).replace("{{content}}", content)


def append_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def entity_id(entity_type: str, key: Any) -> str:
    raw = f"{entity_type}:{text(key)}"
    return f"{entity_type}:{slugify(text(key)) or hashlib.sha1(raw.encode('utf-8')).hexdigest()[:10]}"


def build_graph_rows(data: dict[str, Any], run_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    recorded_at = now_iso()
    schema_version = text(data.get("schema_version") or SCHEMA_VERSION)
    topic = data.get("topic")
    mode = data.get("mode")
    entities: dict[str, dict[str, Any]] = {}
    links: dict[str, dict[str, Any]] = {}

    def add_entity(entity_type: str, key: Any, name: Any, **extra: Any) -> str:
        eid = entity_id(entity_type, key)
        row = {
            "id": eid,
            "type": entity_type,
            "name": text(name),
            "topic": topic,
            "mode": mode,
            "run_id": run_id,
            "recorded_at": recorded_at,
            "schema_version": schema_version,
        }
        row.update({k: v for k, v in extra.items() if v not in (None, "", [])})
        entities[eid] = row
        return eid

    def add_link(src: str, relation: str, dst: str, **extra: Any) -> None:
        lid = hashlib.sha1(f"{src}:{relation}:{dst}:{run_id}".encode("utf-8")).hexdigest()[:16]
        row = {
            "id": lid,
            "source": src,
            "relation": relation,
            "target": dst,
            "topic": topic,
            "mode": mode,
            "run_id": run_id,
            "recorded_at": recorded_at,
            "schema_version": schema_version,
        }
        row.update({k: v for k, v in extra.items() if v not in (None, "", [])})
        links[lid] = row

    stage_entities: dict[str, str] = {}
    for item in as_list(data.get("stage_artifacts")):
        if not isinstance(item, dict):
            continue
        stage_id = text(item.get("stage_id"))
        if not stage_id:
            continue
        stage_entities[stage_id] = add_entity(
            "cycle_stage",
            stage_id,
            stage_id,
            stage_mode=item.get("mode"),
            status=item.get("status"),
            json_path=item.get("json_path"),
            html_path=item.get("html_path"),
        )

    source_entities: dict[str, str] = {}
    for idx, src in enumerate(as_list(data.get("sources")), 1):
        if not isinstance(src, dict):
            continue
        sid = text(src.get("id") or f"src-{idx}")
        source_entities[sid] = add_entity(
            "source",
            sid,
            src.get("title") or sid,
            url=src.get("url"),
            source_type=src.get("source_type"),
            confidence=src.get("confidence"),
        )

    keyword_entities: dict[str, str] = {}
    for item in as_list(data.get("keywords")):
        if not isinstance(item, dict):
            continue
        term = text(item.get("term"))
        if not term:
            continue
        eid = add_entity("keyword", term, term, aliases=as_list(item.get("aliases")), evidence_count=item.get("evidence_count"))
        keyword_entities[term.lower()] = eid
        for sid in as_list(item.get("source_ids")):
            if text(sid) in source_entities:
                add_link(source_entities[text(sid)], "supports", eid)

    trend_entities = []
    for item in as_list(data.get("trend_clusters")):
        if not isinstance(item, dict):
            continue
        name = text(item.get("name"))
        if not name:
            continue
        eid = add_entity("trend", name, name, evidence_strength=item.get("evidence_strength"), maturity=item.get("maturity"))
        trend_entities.append((eid, item))
        for sid in as_list(item.get("source_ids")):
            if text(sid) in source_entities:
                add_link(source_entities[text(sid)], "supports", eid)
        haystack = " ".join([name, text(item.get("thesis")), " ".join(map(str, as_list(item.get("drivers"))))]).lower()
        for term, kid in keyword_entities.items():
            if term and term in haystack:
                add_link(eid, "mentions", kid)

    gap_entities = []
    for item in as_list(data.get("gaps")):
        if not isinstance(item, dict):
            continue
        name = text(item.get("name"))
        if not name:
            continue
        eid = add_entity("gap", name, name, gap_type=item.get("gap_type"), confidence=item.get("confidence"), source_ids=as_list(item.get("source_ids")))
        gap_entities.append((eid, item))
        for sid in as_list(item.get("source_ids")):
            if text(sid) in source_entities:
                add_link(source_entities[text(sid)], "supports", eid)
        for trend_id, trend in trend_entities:
            if set(map(text, as_list(item.get("source_ids")))) & set(map(text, as_list(trend.get("source_ids")))):
                add_link(eid, "derived_from", trend_id)

    idea_entities = []
    for item in as_list(data.get("ideas")):
        if not isinstance(item, dict):
            continue
        name = text(item.get("name"))
        if not name:
            continue
        eid = add_entity(
            "idea",
            name,
            name,
            priority=item.get("priority"),
            novelty_verdict=item.get("novelty_verdict"),
            source_ids=as_list(item.get("source_ids")),
        )
        idea_entities.append((eid, item))
        for sid in as_list(item.get("source_ids")):
            if text(sid) in source_entities:
                add_link(source_entities[text(sid)], "supports", eid)
        anchor = text(item.get("problem_anchor")).lower()
        idea_sources = set(map(text, as_list(item.get("source_ids"))))
        for gap_id, gap in gap_entities:
            if text(gap.get("name")).lower() in anchor or idea_sources & set(map(text, as_list(gap.get("source_ids")))):
                add_link(eid, "addresses", gap_id)

    roadmap = data.get("experiment_roadmap") if isinstance(data.get("experiment_roadmap"), dict) else {}
    for claim in as_list(roadmap.get("claims") if roadmap else []):
        if not isinstance(claim, dict):
            continue
        key = claim.get("id") or claim.get("claim")
        if not key:
            continue
        cid = add_entity("claim", key, claim.get("claim") or key, blocks=as_list(claim.get("blocks")))
        for idea_id, _ in idea_entities:
            add_link(cid, "validates", idea_id)

    derivation = data.get("formula_derivation") if isinstance(data.get("formula_derivation"), dict) else {}
    if derivation:
        fid = add_entity("formula_derivation", topic or "formula-derivation", derivation.get("title") or topic or "formula derivation")
        for sid in as_list(derivation.get("source_ids")):
            if text(sid) in source_entities:
                add_link(fid, "derived_from", source_entities[text(sid)])
        for idea_id, _ in idea_entities:
            add_link(fid, "validates", idea_id)

    evaluation_entities: dict[str, str] = {}
    for item in as_list(data.get("evaluation_scorecards")):
        if not isinstance(item, dict):
            continue
        scorecard_id = text(item.get("scorecard_id"))
        if not scorecard_id:
            continue
        artifact_id = text(item.get("artifact_id"))
        eid = add_entity(
            "evaluation",
            scorecard_id,
            scorecard_id,
            artifact_id=artifact_id,
            total_score=item.get("total_score"),
            verdict=item.get("verdict"),
            rubric_version=item.get("rubric_version"),
        )
        evaluation_entities[scorecard_id] = eid
        if artifact_id in stage_entities:
            add_link(eid, "evaluates", stage_entities[artifact_id])
            if text(item.get("verdict")) == "blocked" or as_list(item.get("blocking_issues")):
                add_link(eid, "blocks", stage_entities[artifact_id])

    for item in as_list(data.get("iteration_log")):
        if not isinstance(item, dict):
            continue
        stage_id = text(item.get("stage_id"))
        result_scorecard = text(item.get("result_scorecard_id"))
        trigger_scorecard = text(item.get("trigger_scorecard_id"))
        if stage_id in stage_entities and result_scorecard in evaluation_entities:
            add_link(evaluation_entities[result_scorecard], "improves", stage_entities[stage_id])
        if stage_id in stage_entities and trigger_scorecard in evaluation_entities:
            add_link(evaluation_entities[trigger_scorecard], "blocks", stage_entities[stage_id])

    return list(entities.values()), list(links.values())


def update_kb(data: dict[str, Any], output: Path, kb_root: Path) -> None:
    data.setdefault("schema_version", SCHEMA_VERSION)
    schema_version = text(data.get("schema_version") or SCHEMA_VERSION)
    topic_slug = text(data.get("topic_slug") or slugify(text(data.get("topic"))))
    run_id = hashlib.sha1(f"{topic_slug}:{data.get('mode')}:{data.get('generated_at')}".encode("utf-8")).hexdigest()[:12]
    topic_dir = kb_root / "paper-trace" / topic_slug if text(data.get("mode")) == "paper-trace" else kb_root / topic_slug
    topic_dir.mkdir(parents=True, exist_ok=True)

    source_rows = []
    for src in as_list(data.get("sources")):
        if isinstance(src, dict):
            row = dict(src)
            row.update({"topic": data.get("topic"), "mode": data.get("mode"), "run_id": run_id, "recorded_at": now_iso(), "schema_version": schema_version})
            source_rows.append(row)
    append_jsonl(topic_dir / "sources.jsonl", source_rows)

    mode = text(data.get("mode"))
    effective_keywords = [] if light_update_mode(mode) else as_list(data.get("keywords"))
    effective_trends = [] if light_update_mode(mode) else as_list(data.get("trend_clusters"))
    effective_gaps = as_list(data.get("gaps"))
    effective_ideas = as_list(data.get("ideas"))
    effective_stages = as_list(data.get("stage_artifacts"))
    effective_scorecards = as_list(data.get("evaluation_scorecards"))
    keywords_doc = {
        "schema_version": schema_version,
        "topic": data.get("topic"),
        "topic_slug": topic_slug,
        "updated_at": now_iso(),
        "mode": data.get("mode"),
        "time_window": data.get("time_window"),
        "keywords": effective_keywords,
        "gaps": effective_gaps,
        "ideas": effective_ideas,
        "stage_artifacts": effective_stages,
        "evaluation_scorecards": effective_scorecards,
    }
    (topic_dir / "keywords.json").write_text(json.dumps(keywords_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    graph_entities, graph_links = build_graph_rows(data, run_id)
    run_row = {
        "run_id": run_id,
        "schema_version": schema_version,
        "topic": data.get("topic"),
        "topic_slug": topic_slug,
        "mode": data.get("mode"),
        "generated_at": data.get("generated_at"),
        "snapshot_date": data.get("snapshot_date"),
        "time_window": data.get("time_window"),
        "report_path": str(output),
        "source_count": len(as_list(data.get("sources"))),
        "finding_count": len(as_list(data.get("findings"))),
        "keyword_count": len(effective_keywords),
        "trend_count": len(effective_trends),
        "gap_count": len(effective_gaps),
        "idea_count": len(effective_ideas),
        "stage_count": len(effective_stages),
        "evaluation_scorecard_count": len(effective_scorecards),
        "graph_entity_count": len(graph_entities),
        "graph_link_count": len(graph_links),
    }
    append_jsonl(topic_dir / "runs.jsonl", [run_row])

    append_jsonl(topic_dir / "entities.jsonl", graph_entities)
    append_jsonl(topic_dir / "links.jsonl", graph_links)
    graph_doc = {
        "schema_version": schema_version,
        "topic": data.get("topic"),
        "topic_slug": topic_slug,
        "updated_at": now_iso(),
        "mode": data.get("mode"),
        "run_id": run_id,
        "entities": graph_entities,
        "links": graph_links,
    }
    (topic_dir / "graph_latest.json").write_text(json.dumps(graph_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render auto-research report JSON to HTML.")
    parser.add_argument("--input", required=True, type=Path, help="Input report JSON path")
    parser.add_argument("--output", required=True, type=Path, help="Output HTML path")
    parser.add_argument("--template", default=DEFAULT_TEMPLATE, type=Path, help="HTML template path")
    parser.add_argument("--config", default=DEFAULT_CONFIG, type=Path, help="Research mode/config registry path")
    parser.add_argument("--update-kb", action="store_true", help="Append sources/runs and keyword snapshot to knowledge_base")
    parser.add_argument("--kb-root", default=DEFAULT_KB_ROOT, type=Path, help="Knowledge base root")
    parser.add_argument("--archive-output", action="store_true", help="Move dated report outputs into archive/YYYY/MM/<mode>/ before updating knowledge_base")
    args = parser.parse_args()

    data = load_json(args.input)
    data.setdefault("topic_slug", slugify(text(data.get("topic"))))
    template = args.template.read_text(encoding="utf-8")
    config = load_config(args.config)
    html_text = render_report(data, template, config)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html_text, encoding="utf-8")
    final_output = args.output
    if args.archive_output:
        archive = load_archive_module()
        archive_result = archive.archive_rendered_report(args.input, args.output, apply=True)
        final_output = Path(archive_result.get("html_path", str(args.output)))
    if args.update_kb:
        update_kb(data, final_output, args.kb_root)
    print(f"wrote {final_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
