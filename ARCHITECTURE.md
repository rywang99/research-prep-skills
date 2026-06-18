# Architecture Notes

This repository is a config-driven Codex skills library for research preparation before humans run experiments. It is not an autonomous training, experiment execution, paper-writing, or submission system.

## Current extensibility status

The design is extensible for common research workflow changes:

- New modes are registered in `.agents/skills/auto-research-common/config/research_modes.json`.
- Each mode owns concise instructions in `.agents/skills/<skill-name>/SKILL.md`; shared behavior stays in `auto-research-common`.
- Shared policy, report schema, knowledge-base schema, renderer, and HTML template live in `.agents/skills/auto-research-common/`.
- Candidate source collection starts with `scripts/collect_sources.py`, which queries no-key public APIs and emits normalized JSONL.
- Report content uses a generic JSON schema with `schema_version: "1.0"`; missing versions remain readable for older local artifacts.
- Daily/weekly reports can embed expanded `paper_traces`; lightweight update modes suppress hotword and trend sections by default.
- Preparation modes cover `gap-analysis`, `idea-planning`, `experiment-roadmap`, and optional `formula-derivation`.
- Long-running orchestration uses `research-yearly-full-cycle`, which composes monthly slices, yearly synthesis, preparation stages, independent evaluation, and iteration logs without expanding into experiment execution.
- Independent scoring uses `research-independent-evaluator` as a separate mode so generated reports and rubric judgments remain distinct artifacts.
- Novelty checking is an evaluation dimension inside `research-idea-planning`, not a parallel skill.
- Research-wiki/wiki-enrich style persistence is folded into `knowledge_base/` as lightweight graph files.
- Paper trace is HTML-first: helpers may use temporary PDF extraction, but do not create persistent PDF caches or PDF annotations.

## Extension points

- Add a mode: run `python3 scripts/new_research_mode.py quarterly --label 季度调研 --window-days 90 --description "最近 90 天阶段性趋势复盘"`.
- Add a prompt: update `PROMPTS.md` with one or two user-facing examples.
- Add a source category: update `source_types` in `research_modes.json`; unknown types still render safely.
- Add a source provider: add a collector function in `scripts/collect_sources.py`, map it to the report source fields, and add an offline fixture row.
- Add a report section: extend `report_schema.md`, add a focused `render_<section>()`, add a fixture, and update `scripts/validate_skills.py`.
- Add knowledge-base fields: update `references/knowledge_base_schema.md`, keep JSONL append-only, and make readers tolerate absent fields.
- Add a paper trace field: extend `paper_traces` only when the renderer can still show old trace records safely.

## Data flow

1. Build a topic profile and bilingual search queries from a user request.
2. Collect candidate sources with `scripts/collect_sources.py` when useful.
3. Review, cluster, and convert the strongest evidence into the report JSON schema.
4. For daily/weekly reports, embed in-window paper traces with `scripts/trace_report_papers.py`; default concurrency is `--jobs 8`.
5. Render HTML with `.agents/skills/auto-research-common/scripts/render_report.py`.
6. When `--update-kb` is used, append sources, runs, keywords, and graph rows under `knowledge_base/<topic_slug>/`.
7. Query local graph snapshots with `scripts/query_knowledge_base.py` when a future workflow needs prior context.
8. For yearly full-cycle runs, append stage artifacts, scorecards, and iteration logs as normal report fields and graph entities.

## Knowledge-base compatibility

- Current schema version is `1.0`.
- `sources.jsonl`, `runs.jsonl`, `entities.jsonl`, and `links.jsonl` are append-oriented; do not rewrite historical rows for routine migrations.
- `keywords.json` and `graph_latest.json` are latest snapshots for quick reuse.
- Full-cycle runs may add `cycle_stage` and `evaluation` entities plus `evaluates`, `improves`, and `blocks` links; readers must ignore these fields when unsupported.
- Readers must tolerate missing `schema_version` and unknown extra fields.
- Generated knowledge-base data remains local and ignored by Git except for `.gitkeep`.

## Constraints

- Keep scripts dependency-free unless the benefit clearly outweighs installation friction.
- Preserve backward compatibility for `knowledge_base/*/*.jsonl` and older report JSON fixtures.
- Do not make network access part of the default validation path; use fixtures for deterministic checks.
- Prefer configuration and schema additions over broad branching logic in `render_report.py`.
- Do not introduce persistent `paper_cache/` outputs unless the privacy model is revisited.
- Validate after changes with `python3 scripts/validate_skills.py`.
