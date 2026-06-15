# Repository Guidelines

## Project Structure & Module Organization

- `.agents/skills/auto-research/` contains the orchestration skill that routes research requests.
- `.agents/skills/research-*` contains mode-specific skills: daily, weekly, monthly, yearly hotwords, and yearly trends.
- `.agents/skills/auto-research-common/` contains shared config, assets, references, and scripts.
- `.agents/skills/auto-research-common/config/research_modes.json` registers modes, labels, nav sections, and source type labels.
- `.agents/skills/auto-research-common/assets/report_template.html` is the self-contained HTML report template.
- `.agents/skills/auto-research-common/references/` defines source policy and report JSON schema.
- `examples/` stores sample report JSON and collected-source JSONL fixtures.
- `reports/` stores generated HTML reports.
- `knowledge_base/` stores persisted sources, runs, and keyword snapshots.
- `scripts/` stores repository-level collection, validation, and scaffolding utilities.

## Build, Test, and Development Commands

- `python3 scripts/validate_skills.py` validates skill frontmatter, metadata files, sample JSON, renderer execution, and knowledge-base updates.
- `python3 scripts/collect_sources.py --topic "AI Agent 评测" --query "AI agent evaluation" --sources arxiv,openalex,github --limit-per-source 5 --output /tmp/collected_sources.jsonl` collects candidate sources from no-key public APIs.
- `python3 .agents/skills/auto-research-common/scripts/render_report.py --input examples/minimal_report.json --output reports/demo/demo_weekly.html --update-kb` renders the sample report.
- `find .agents/skills -name SKILL.md -print` lists all installed local skills.
- `python3 scripts/new_research_mode.py quarterly --label 季度调研 --window-days 90 --description "最近 90 天阶段性趋势复盘"` scaffolds and registers a new mode.

## Coding Style & Naming Conventions

Use concise Markdown in `SKILL.md`; keep instructions actionable and avoid duplicating shared policy. Skill directories use lowercase kebab-case, for example `research-yearly-trends`. Python scripts should prefer stdlib dependencies, 4-space indentation, type hints where helpful, and clear function names. JSON keys use snake_case and match `report_schema.md`. Register new modes in `research_modes.json` rather than hard-coding labels.

## Testing Guidelines

There is no formal test framework yet. Treat `scripts/validate_skills.py` as the required smoke test. Add or update fixtures in `examples/` when changing schema or renderer behavior. Generated HTML should open standalone and include navigation, metrics, findings, sources, and responsive styling.

## Commit & Pull Request Guidelines

No existing Git history is available in this checkout, so use clear imperative commit messages such as `Add weekly research skill` or `Update report renderer schema handling`. Pull requests should describe the changed workflow, list validation commands run, and include screenshots or the generated `reports/...html` path when template output changes.

## Security & Configuration Tips

Do not commit API keys, browser cookies, or private source exports. Keep generated research outputs under `reports/` and reusable metadata under `knowledge_base/`. When adding external integrations, document required environment variables without storing secrets.
