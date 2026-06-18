# Claude Code Project Guide

This repository is an automated research-preparation skill library. It turns a research topic into sourced Chinese HTML/JSON reports for daily, weekly, monthly, yearly hotwords/trends, gap analysis, idea planning, experiment roadmap, formula-derivation preparation, paper trace, yearly full-cycle orchestration, and independent evaluation.

## Claude Code Usage

- Invoke project skills with slash commands, for example `/auto-research`, `/research-weekly`, `/research-yearly-full-cycle`, `/paper-trace`, or `/research-independent-evaluator`.
- `.agents/skills/` is the source of truth for skill content.
- `.claude/skills/` is a generated Claude Code mirror. Do not edit generated files by hand.
- After changing any skill under `.agents/skills/`, run `python3 scripts/sync_claude_skills.py` and then `python3 scripts/validate_skills.py`.

## Important Commands

- Validate everything: `python3 scripts/validate_skills.py`
- Sync Claude Code skills: `python3 scripts/sync_claude_skills.py`
- Check Claude Code sync only: `python3 scripts/sync_claude_skills.py --check`
- Collect candidates: `python3 scripts/collect_sources.py --topic "AI Agent 评测" --query "AI agent evaluation" --sources arxiv,openalex,github --limit-per-source 5 --output /tmp/collected_sources.jsonl`
- Render a report: `python3 .agents/skills/auto-research-common/scripts/render_report.py --input examples/minimal_report.json --output reports/demo/demo_weekly.html --update-kb`
- Trace one paper: `python3 scripts/trace_single_paper.py --paper "2606.13095" --topic "多说话人语音识别"`

## Repository Rules

- Keep reports and reusable metadata under `reports/` and `knowledge_base/`; these are local generated outputs and are ignored except `.gitkeep` placeholders.
- Do not commit API keys, cookies, private source exports, private PDFs, or personal report data.
- Use concise Markdown in `SKILL.md`; keep shared policy in `auto-research-common` instead of duplicating it across skills.
- Register new modes in `.agents/skills/auto-research-common/config/research_modes.json`.
- Keep Python scripts dependency-light and prefer the standard library.
- This repository prepares research and reports only; do not run experiments, train models, submit papers, or claim empirical results unless the user supplies verified evidence.
