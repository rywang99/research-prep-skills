#!/usr/bin/env python3
"""Embed HTML-first paper traces into a daily/weekly report JSON."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
from pathlib import Path
from typing import Any

from paper_trace_common import (
    as_list,
    generate_trace,
    in_window,
    is_traceable_paper_source,
    parse_date,
    source_to_trace_input,
    text,
)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("report JSON must be an object")
    return data


def source_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result = {}
    for idx, source in enumerate(as_list(data.get("sources")), 1):
        if isinstance(source, dict):
            result[text(source.get("id") or f"src-{idx}")] = source
    return result


def report_window(data: dict[str, Any]) -> tuple[Any, Any]:
    window = data.get("time_window") if isinstance(data.get("time_window"), dict) else {}
    start = parse_date(window.get("start")) if isinstance(window, dict) else None
    end = parse_date(window.get("end")) if isinstance(window, dict) else None
    if end is None:
        end = parse_date(data.get("snapshot_date"))
    return start, end


def select_report_papers(data: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    sources = source_index(data)
    start, end = report_window(data)
    source_dates: dict[str, Any] = {sid: parse_date(src.get("published_at")) for sid, src in sources.items()}
    finding_rank: dict[str, int] = {}
    usage: dict[str, int] = {}
    for idx, finding in enumerate(as_list(data.get("findings")), 1):
        if not isinstance(finding, dict):
            continue
        fdate = parse_date(finding.get("date"))
        for sid in as_list(finding.get("source_ids")):
            sid_text = text(sid)
            if sid_text in sources:
                finding_rank.setdefault(sid_text, idx)
                usage[sid_text] = usage.get(sid_text, 0) + 1
                if source_dates.get(sid_text) is None:
                    source_dates[sid_text] = fdate
    selected: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for sid, source in sources.items():
        if not is_traceable_paper_source(source):
            continue
        date_value = source_dates.get(sid)
        if start or end:
            if not in_window(date_value, start, end):
                skipped.append({"source_id": sid, "reason": "date_outside_window_or_unknown", "title": text(source.get("title"))})
                continue
        selected.append(source_to_trace_input(source))
    selected.sort(key=lambda src: (finding_rank.get(text(src.get("id")), 999), text(src.get("published_at")), text(src.get("title"))))
    return selected, skipped


def upsert_metric(data: dict[str, Any], label: str, value: str, note: str) -> None:
    metrics = data.setdefault("metrics", [])
    if not isinstance(metrics, list):
        data["metrics"] = metrics = []
    for metric in metrics:
        if isinstance(metric, dict) and metric.get("label") == label:
            metric.update({"value": value, "note": note})
            return
    metrics.append({"label": label, "value": value, "note": note})


def trace_sources(selected: list[dict[str, Any]], topic: str, timeout: int, jobs: int) -> list[dict[str, Any]]:
    if jobs <= 1 or len(selected) <= 1:
        return [generate_trace(source, topic=topic, timeout=timeout) for source in selected]
    worker_count = min(jobs, len(selected))
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
        return list(executor.map(lambda source: generate_trace(source, topic=topic, timeout=timeout), selected))


def update_report(data: dict[str, Any], timeout: int, jobs: int) -> dict[str, Any]:
    selected, skipped = select_report_papers(data)
    topic = text(data.get("topic"))
    traces = trace_sources(selected, topic=topic, timeout=timeout, jobs=jobs)
    data["paper_traces"] = traces
    upsert_metric(data, "论文溯源", str(len(traces)), f"区间内文献已嵌入 HTML 展开分析；并发 jobs={max(1, jobs)}")
    if skipped:
        risks = data.setdefault("risks", [])
        if isinstance(risks, list):
            risks.append(f"{len(skipped)} 个文献型来源因日期缺失或不在报告窗口内未自动 trace。")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Trace all in-window paper sources and embed the analysis into a report JSON.")
    parser.add_argument("--report", required=True, type=Path, help="Input report JSON")
    parser.add_argument("--output", type=Path, help="Output JSON; defaults to overwriting --report")
    parser.add_argument("--timeout", type=int, default=45, help="Network/PDF extraction timeout in seconds")
    parser.add_argument("--jobs", type=int, default=8, help="Concurrent paper trace workers; default 8")
    args = parser.parse_args()

    data = update_report(load_json(args.report), timeout=args.timeout, jobs=max(1, args.jobs))
    output = args.output or args.report
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(output), "trace_count": len(data.get("paper_traces", [])), "jobs": max(1, args.jobs)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
