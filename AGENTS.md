# Repository Guidelines

## Project Structure & Module Organization

- `.agents/skills/auto-research/` contains the orchestration skill that routes research requests.
- `.agents/skills/research-*` contains mode-specific skills: daily, weekly, monthly, yearly hotwords, and yearly trends.
- `.claude/skills/` contains the generated Claude Code project-skill mirror; do not edit it by hand.
- `.agents/skills/paper-trace/` contains the single-paper technical lineage skill.
- `.agents/skills/auto-research-common/` contains shared config, assets, references, and scripts.
- `.agents/skills/auto-research-common/config/research_modes.json` registers modes, labels, nav sections, and source type labels.
- `.agents/skills/auto-research-common/assets/report_template.html` is the self-contained HTML report template.
- `.agents/skills/auto-research-common/references/` defines source policy and report JSON schema.
- `examples/` stores sample report JSON and collected-source JSONL fixtures.
- `reports/` stores generated HTML/JSON reports, including standalone paper trace reports.
- `knowledge_base/` stores persisted sources, runs, and keyword snapshots.
- `scripts/` stores repository-level collection, paper trace, validation, and scaffolding utilities.

## Build, Test, and Development Commands

- `python3 scripts/validate_skills.py` validates skill frontmatter, metadata files, sample JSON, renderer execution, and knowledge-base updates.
- `python3 scripts/sync_claude_skills.py` regenerates `.claude/skills/` from `.agents/skills/` for Claude Code compatibility.
- `python3 scripts/sync_claude_skills.py --check` verifies the Claude Code mirror is current without writing files.
- `python3 scripts/collect_sources.py --topic "AI Agent 评测" --query "AI agent evaluation" --sources arxiv,openalex,github --limit-per-source 5 --output /tmp/collected_sources.jsonl` collects candidate sources from no-key public APIs.
- `python3 scripts/trace_single_paper.py --paper "2606.13095" --topic "多说话人语音识别"` generates a standalone paper trace HTML without caching PDFs.
- `python3 scripts/trace_report_papers.py --report reports/<topic_slug>/YYYY-MM-DD_weekly.json` embeds all in-window paper traces into a report JSON before rendering; default concurrency is `--jobs 8`.
- `python3 .agents/skills/auto-research-common/scripts/render_report.py --input examples/minimal_report.json --output reports/demo/demo_weekly.html --update-kb` renders the sample report.
- `find .agents/skills -name SKILL.md -print` lists all installed local skills.
- `python3 scripts/new_research_mode.py quarterly --label 季度调研 --window-days 90 --description "最近 90 天阶段性趋势复盘"` scaffolds and registers a new mode.

## Coding Style & Naming Conventions

Use concise Markdown in `SKILL.md`; keep instructions actionable and avoid duplicating shared policy. Skill directories use lowercase kebab-case, for example `research-yearly-trends`. Python scripts should prefer stdlib dependencies, 4-space indentation, type hints where helpful, and clear function names. JSON keys use snake_case and match `report_schema.md`. Register new modes in `research_modes.json` rather than hard-coding labels.

Treat `.agents/skills/` as the source of truth. After editing any skill, run `python3 scripts/sync_claude_skills.py` so Claude Code can discover the generated `.claude/skills/` copy.

## Testing Guidelines

There is no formal test framework yet. Treat `scripts/validate_skills.py` as the required smoke test. It also checks that `.claude/skills/` is synced. Add or update fixtures in `examples/` when changing schema, renderer behavior, or paper trace output. Generated HTML should open standalone and include navigation, metrics, findings, paper traces when present, sources, and responsive styling; daily/weekly reports should not render hotword or trend sections by default.

## Commit & Pull Request Guidelines

No existing Git history is available in this checkout, so use clear imperative commit messages such as `Add weekly research skill` or `Update report renderer schema handling`. Pull requests should describe the changed workflow, list validation commands run, and include screenshots or the generated `reports/...html` path when template output changes.

## Security & Configuration Tips

Do not commit API keys, browser cookies, private source exports, or personal PDF copies. Keep generated research outputs under `reports/` and reusable metadata under `knowledge_base/`. Paper trace is HTML-first and should not create persistent PDF caches. When adding external integrations, document required environment variables without storing secrets.
