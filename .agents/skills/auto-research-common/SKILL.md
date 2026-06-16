---
name: auto-research-common
description: Shared assets, source policy, report schema, and rendering tools for the auto-research skills library; use when generating or validating automated research HTML reports and local knowledge-base entries.
---

# Auto Research Common

This skill provides shared resources for the auto-research skill family.

## Use these files

- `config/research_modes.json`: registry for modes, labels, default windows, nav sections, and source type labels.
- `references/source_policy.md`: source priority, citation, deduplication, and confidence rules.
- `references/report_schema.md`: JSON shape expected by the renderer and knowledge-base updater.
- `references/knowledge_base_schema.md`: local persistence, graph artifacts, versioning, and compatibility rules.
- `references/extension_guide.md`: steps for adding modes, report sections, source types, and migrations.
- `assets/report_template.html`: self-contained HTML/CSS template inspired by the local spatial-audio planning document.
- `scripts/render_report.py`: render a report JSON into HTML and optionally update `knowledge_base/`.
- Repository-level `scripts/collect_sources.py`: collect candidate sources from arXiv, OpenAlex, and GitHub into normalized JSONL.
- Repository-level `scripts/trace_report_papers.py`: embed expanded HTML paper traces into daily/weekly report JSON with default `--jobs 8` concurrency.
- Repository-level `scripts/trace_single_paper.py`: generate standalone single-paper trace JSON/HTML without caching PDFs.
- Repository-level `scripts/query_knowledge_base.py`: query local `entities.jsonl` and `links.jsonl` graph artifacts.
- Preparation modes such as `gap-analysis`, `idea-planning`, and `experiment-roadmap` use the same renderer and schema but do not run experiments.
- `--update-kb` also writes lightweight graph files under `knowledge_base/<topic_slug>/` (`entities.jsonl`, `links.jsonl`, `graph_latest.json`) so research-wiki/wiki-enrich style persistence is folded into the existing knowledge base rather than exposed as a parallel skill.

## Standard command

```bash
python3 .agents/skills/auto-research-common/scripts/render_report.py \
  --input examples/minimal_report.json \
  --output reports/demo/demo_weekly.html \
  --update-kb

# Optional: use a different mode registry
python3 .agents/skills/auto-research-common/scripts/render_report.py \
  --input examples/minimal_report.json \
  --output reports/demo/demo_weekly.html \
  --config .agents/skills/auto-research-common/config/research_modes.json
```

The script uses only Python standard library modules.

## Candidate source collection

```bash
python3 scripts/collect_sources.py \
  --topic "automated research agent" \
  --query "automated research agent" \
  --sources arxiv,openalex,github \
  --window-days 30 \
  --limit-per-source 5 \
  --output /tmp/collected_sources.jsonl
```

Treat collected rows as candidates. Review the source content before citing it in a report.
