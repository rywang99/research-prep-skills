# Architecture Notes

This repository is designed as a small, config-driven skills library rather than a single hard-coded research script.

## Current extensibility status

The design is now extensible for common research workflow changes:

- New modes are registered in `.agents/skills/auto-research-common/config/research_modes.json`.
- Each mode owns its instructions in `.agents/skills/research-<mode>/SKILL.md`.
- Shared policy, schema, renderer, and template live in `.agents/skills/auto-research-common/`.
- Candidate source collection starts with `scripts/collect_sources.py`, which queries no-key public APIs and emits normalized JSONL.
- Report content uses a generic JSON schema, with a dedicated `paper_traces` field for collapsible paper lineage analysis; daily/weekly modes suppress hotword and trend sections by default.
- Knowledge-base storage is append-oriented, which keeps old run data readable as the schema evolves.
- Paper trace is HTML-first: helpers may use temporary PDF extraction, but do not create persistent PDF caches or PDF annotations.

## Extension points

- Add a mode: run `python3 scripts/new_research_mode.py quarterly --label 季度调研 --window-days 90 --description "最近 90 天阶段性趋势复盘"`.
- Add a prompt: update `PROMPTS.md` with one or two user-facing examples.
- Add a source category: update `source_types` in `research_modes.json`; unknown types still render safely.
- Add a source provider: add a collector function in `scripts/collect_sources.py`, map it to the report source fields, and add an offline fixture row.
- Add a paper trace field: extend `paper_traces` only when the renderer can still show old trace records safely.
- Add a custom layout: add a new `render_<section>()` function only when generic `sections` cannot express the report.

## Data flow

1. Build topic profile and search queries from a user request.
2. Collect candidate sources with `scripts/collect_sources.py`.
3. Review, cluster, and convert the strongest evidence into the report JSON schema.
4. For daily/weekly reports, embed all in-window paper traces with `scripts/trace_report_papers.py`; default concurrency is `--jobs 8`.
5. Render HTML with `.agents/skills/auto-research-common/scripts/render_report.py`.
6. Append source/run/keyword records into `knowledge_base/<topic_slug>/` when `--update-kb` is used.

## Constraints

- Keep scripts dependency-free unless the benefit clearly outweighs installation friction.
- Preserve backward compatibility for `knowledge_base/*/*.jsonl`.
- Do not make network access part of the default validation path; use fixtures for deterministic checks.
- Prefer configuration and schema additions over branching logic in `render_report.py`.
- Do not introduce persistent `paper_cache/` outputs unless the privacy model is revisited.
- Validate after changes with `python3 scripts/validate_skills.py`.
