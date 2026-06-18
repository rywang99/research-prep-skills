#!/usr/bin/env python3
"""Lightweight validation for the local auto-research skills library."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
REQUIRED_BASE = {
    "auto-research",
    "auto-research-common",
}
CONFIG_PATH = SKILLS / "auto-research-common" / "config" / "research_modes.json"
COLLECTED_FIXTURE = ROOT / "examples" / "collected_sources.jsonl"
COLLECTOR_PATH = ROOT / "scripts" / "collect_sources.py"
TRACE_REPORT_PATH = ROOT / "scripts" / "trace_report_papers.py"
TRACE_SINGLE_PATH = ROOT / "scripts" / "trace_single_paper.py"
QUERY_KB_PATH = ROOT / "scripts" / "query_knowledge_base.py"
SCHEMA_VERSION = "1.0"
PREPARATION_FIXTURES = [
    (ROOT / "examples" / "gap_analysis_report.json", "gaps", 'id="gaps"'),
    (ROOT / "examples" / "idea_planning_report.json", "ideas", 'id="ideas"'),
    (ROOT / "examples" / "experiment_roadmap_report.json", "experiment_roadmap", 'id="roadmap"'),
    (ROOT / "examples" / "formula_derivation_report.json", "formula_derivation", 'id="derivation"'),
    (ROOT / "examples" / "yearly_full_cycle_report.json", "stage_artifacts", 'id="cycle"'),
    (ROOT / "examples" / "independent_evaluation_report.json", "evaluation_scorecards", 'id="evaluation"'),
]
REQUIRED_SOURCE_FIELDS = {
    "id",
    "title",
    "url",
    "source_type",
    "published_at",
    "accessed_at",
    "summary",
    "confidence",
    "provider",
    "query",
    "external_id",
    "collected_at",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_frontmatter(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        fail(f"missing YAML frontmatter: {path}")
    frontmatter = match.group(1)
    if not re.search(r"^name:\s*\S+", frontmatter, re.M):
        fail(f"missing name in frontmatter: {path}")
    if not re.search(r"^description:\s*\S+", frontmatter, re.M):
        fail(f"missing description in frontmatter: {path}")


def load_collector_module():
    spec = importlib.util.spec_from_file_location("collect_sources", COLLECTOR_PATH)
    if spec is None or spec.loader is None:
        fail(f"cannot load collector module: {COLLECTOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_paper_trace_module():
    path = ROOT / "scripts" / "paper_trace_common.py"
    spec = importlib.util.spec_from_file_location("paper_trace_common", path)
    if spec is None or spec.loader is None:
        fail(f"cannot load paper trace module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_trace_single_module():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("trace_single_paper", TRACE_SINGLE_PATH)
    if spec is None or spec.loader is None:
        fail(f"cannot load trace single module: {TRACE_SINGLE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_collected_sources_fixture() -> None:
    if not COLLECTOR_PATH.exists():
        fail(f"missing {COLLECTOR_PATH}")
    if not COLLECTED_FIXTURE.exists():
        fail(f"missing {COLLECTED_FIXTURE}")
    rows = []
    for line_no, line in enumerate(COLLECTED_FIXTURE.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSONL at {COLLECTED_FIXTURE}:{line_no}: {exc}")
        missing = REQUIRED_SOURCE_FIELDS - set(row)
        if missing:
            fail(f"source fixture missing fields at line {line_no}: {sorted(missing)}")
        rows.append(row)
    if len(rows) < 3:
        fail("source fixture should include at least 3 rows, including a duplicate")
    collector = load_collector_module()
    unique = collector.deduplicate(rows)
    if len(unique) != 2:
        fail(f"collector dedup expected 2 unique fixture rows, got {len(unique)}")
    canonical = collector.canonical_url("https://example.com/path/?utm_source=x&keep=1")
    if canonical != "https://example.com/path?keep=1":
        fail(f"unexpected canonical URL: {canonical}")
    sid_a = collector.stable_source_id("arxiv", "2601.00001", "", "Example")
    sid_b = collector.stable_source_id("arxiv", "2601.00001", "https://arxiv.org/abs/2601.00001", "Other")
    if sid_a != sid_b:
        fail("stable source IDs differ for same provider/external_id")


def validate_paper_trace_naming() -> None:
    trace = load_paper_trace_module()
    spatial = {
        "title": "Spatial-Omni: Spatial Audio Understanding Integration in Multimodal LLMs via FOA Encoding",
        "summary": "First-Order Ambisonics FOA spatial audio for Omni LLMs.",
        "tags": ["arxiv", "eess.AS"],
    }
    if trace.infer_method_slug(spatial) != "spatial-omni":
        fail("Spatial-Omni method slug inference failed")
    if trace.infer_paper_category(spatial, "")["slug"] != "spatial-audio-llm":
        fail("spatial audio category inference failed")
    diarization = {
        "title": "Tight Boundary Prediction in Speaker Diarization Using Causal-Anticausal Consistency",
        "summary": "speaker diarization with tight speech intervals",
        "tags": ["arxiv", "eess.AS"],
    }
    if trace.infer_method_slug(diarization) != "tight-boundary-prediction":
        fail("Tight Boundary method slug inference failed")
    if trace.infer_paper_category(diarization, "")["slug"] != "speaker-diarization":
        fail("speaker diarization category inference failed")
    if trace.infer_paper_category(spatial, "空间音频大模型")["slug"] != "spatial-audio-llm":
        fail("topic-priority category alias failed")
    trace_single = load_trace_single_module()
    output_json, output_html = trace_single.default_output_paths(spatial, "validation-category", "spatial-omni")
    if output_json.name != "spatial-omni.json" or output_html.name != "spatial-omni.html":
        fail("paper-trace default output should use method slug without date prefix")


def main() -> int:
    if not SKILLS.is_dir():
        fail(f"skills dir missing: {SKILLS}")
    present = {p.name for p in SKILLS.iterdir() if p.is_dir()}
    if not CONFIG_PATH.exists():
        fail(f"missing {CONFIG_PATH}")
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    modes = config.get("modes")
    if not isinstance(modes, dict) or not modes:
        fail("config must define at least one mode")
    registered_skills = set()
    for mode, spec in modes.items():
        if not isinstance(spec, dict):
            fail(f"mode spec must be an object: {mode}")
        skill = spec.get("skill")
        if not skill:
            fail(f"mode missing skill: {mode}")
        registered_skills.add(str(skill))
        if not spec.get("label"):
            fail(f"mode missing label: {mode}")
    required = REQUIRED_BASE | registered_skills
    missing = required - present
    if missing:
        fail(f"missing skills: {sorted(missing)}")
    for name in sorted(required):
        skill_md = SKILLS / name / "SKILL.md"
        if not skill_md.exists():
            fail(f"missing {skill_md}")
        validate_frontmatter(skill_md)
        openai_yaml = SKILLS / name / "agents" / "openai.yaml"
        if not openai_yaml.exists():
            fail(f"missing {openai_yaml}")
    nav_anchors = {str(item.get("anchor")) for item in config.get("nav_sections", []) if isinstance(item, dict)}
    for anchor in {"overview", "findings", "refs", "gaps", "ideas", "roadmap", "derivation", "cycle", "evaluation", "iterations"}:
        if anchor not in nav_anchors:
            fail(f"config nav_sections missing anchor: {anchor}")
    minimal = json.loads((ROOT / "examples" / "minimal_report.json").read_text(encoding="utf-8"))
    if minimal.get("schema_version") != SCHEMA_VERSION:
        fail("minimal report fixture missing current schema_version")
    for fixture, field, _ in PREPARATION_FIXTURES:
        data = json.loads(fixture.read_text(encoding="utf-8"))
        if data.get("schema_version") != SCHEMA_VERSION:
            fail(f"preparation fixture missing current schema_version: {fixture}")
        if data.get("mode") not in modes:
            fail(f"preparation fixture mode is not registered: {fixture}")
        if not data.get(field):
            fail(f"preparation fixture missing {field}: {fixture}")
        if field == "ideas" and not any(isinstance(item, dict) and item.get("novelty_verdict") for item in data.get("ideas", [])):
            fail(f"idea fixture missing novelty_verdict: {fixture}")
    validate_collected_sources_fixture()
    validate_paper_trace_naming()
    for path in (TRACE_REPORT_PATH, TRACE_SINGLE_PATH, QUERY_KB_PATH):
        if not path.exists():
            fail(f"missing {path}")
    with tempfile.TemporaryDirectory(prefix="auto-research-validate-") as tmp:
        tmpdir = Path(tmp)
        traced_report = tmpdir / "traced_report.json"
        subprocess.run(
            [
                sys.executable,
                str(TRACE_REPORT_PATH),
                "--report",
                str(ROOT / "examples" / "minimal_report.json"),
                "--output",
                str(traced_report),
            ],
            cwd=ROOT,
            check=True,
        )
        traced_data = json.loads(traced_report.read_text(encoding="utf-8"))
        if not traced_data.get("paper_traces"):
            fail("trace_report_papers did not embed paper_traces")
        subprocess.run(
            [
                sys.executable,
                str(SKILLS / "auto-research-common" / "scripts" / "render_report.py"),
                "--input",
                str(traced_report),
                "--output",
                str(tmpdir / "demo_weekly.html"),
                "--update-kb",
                "--kb-root",
                str(tmpdir / "knowledge_base"),
            ],
            cwd=ROOT,
            check=True,
        )
        if not (tmpdir / "demo_weekly.html").exists():
            fail("renderer did not create HTML output")
        html_text = (tmpdir / "demo_weekly.html").read_text(encoding="utf-8")
        if 'id="paper-traces"' not in html_text or '<section class="trace-card">' not in html_text:
            fail("renderer did not create expanded paper trace section")
        if '<details class="trace-card">' in html_text or '<summary>' in html_text:
            fail("renderer should not create collapsible paper trace sections")
        if not any((tmpdir / "knowledge_base").rglob("runs.jsonl")):
            fail("renderer did not create temporary knowledge-base run records")
        if not any((tmpdir / "knowledge_base").rglob("entities.jsonl")):
            fail("renderer did not create temporary knowledge-base graph entities")
        if not any((tmpdir / "knowledge_base").rglob("links.jsonl")):
            fail("renderer did not create temporary knowledge-base graph links")
        if not any((tmpdir / "knowledge_base").rglob("graph_latest.json")):
            fail("renderer did not create temporary knowledge-base graph snapshot")
        run_rows = [
            json.loads(line)
            for path in (tmpdir / "knowledge_base").rglob("runs.jsonl")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if not run_rows or run_rows[-1].get("schema_version") != SCHEMA_VERSION:
            fail("knowledge-base run record missing current schema_version")
        graph_docs = [json.loads(path.read_text(encoding="utf-8")) for path in (tmpdir / "knowledge_base").rglob("graph_latest.json")]
        if not graph_docs or graph_docs[-1].get("schema_version") != SCHEMA_VERSION:
            fail("knowledge-base graph snapshot missing current schema_version")
        subprocess.run(
            [
                sys.executable,
                str(TRACE_SINGLE_PATH),
                "--paper",
                "Validation Paper Title",
                "--output-json",
                str(tmpdir / "single_trace.json"),
                "--output-html",
                str(tmpdir / "single_trace.html"),
                "--kb-root",
                str(tmpdir / "paper_trace_kb"),
            ],
            cwd=ROOT,
            check=True,
        )
        if not (tmpdir / "single_trace.html").exists():
            fail("trace_single_paper did not create HTML output")
        if not any((tmpdir / "paper_trace_kb").rglob("runs.jsonl")):
            fail("trace_single_paper did not update temporary knowledge base")
        renderer = SKILLS / "auto-research-common" / "scripts" / "render_report.py"
        for fixture, _, expected_anchor in PREPARATION_FIXTURES:
            output = tmpdir / f"{fixture.stem}.html"
            subprocess.run(
                [
                    sys.executable,
                    str(renderer),
                    "--input",
                    str(fixture),
                    "--output",
                    str(output),
                    "--update-kb",
                    "--kb-root",
                    str(tmpdir / "preparation_kb"),
                ],
                cwd=ROOT,
                check=True,
            )
            rendered = output.read_text(encoding="utf-8")
            if expected_anchor not in rendered:
                fail(f"renderer did not create expected preparation section {expected_anchor} for {fixture.name}")
        if not any((tmpdir / "preparation_kb").rglob("graph_latest.json")):
            fail("preparation fixture rendering did not create graph snapshots")
        query_result = subprocess.run(
            [
                sys.executable,
                str(QUERY_KB_PATH),
                "--kb-root",
                str(tmpdir / "preparation_kb"),
                "--type",
                "idea",
                "--limit",
                "5",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        query_data = json.loads(query_result.stdout)
        if query_data.get("count", 0) < 1:
            fail("knowledge-base query did not return idea entities")
        for entity_type in ("cycle_stage", "evaluation"):
            result = subprocess.run(
                [
                    sys.executable,
                    str(QUERY_KB_PATH),
                    "--kb-root",
                    str(tmpdir / "preparation_kb"),
                    "--type",
                    entity_type,
                    "--limit",
                    "5",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            data = json.loads(result.stdout)
            if data.get("count", 0) < 1:
                fail(f"knowledge-base query did not return {entity_type} entities")
    print("skills validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
