---
name: research-gap-analysis
description: Analyze a research domain's evidence-backed gaps, bottlenecks, missing evaluations, data limitations, and actionable opportunities before humans start experiments; generate a Chinese HTML report.
---

# Research Gap Analysis

Use this skill when the user asks for 研究缺口, 现有不足, open problems, bottlenecks, limitations, opportunity analysis, or what is missing in a research field.

## Operating rules

- Default output language is Chinese; keep original method, dataset, benchmark, venue, and model names.
- This is a preparation skill: do not run experiments, train models, write code for methods, or launch jobs.
- Ground every gap in sources from papers, benchmarks, repos, technical blogs, or prior local reports.
- Prefer gaps that can later become falsifiable research ideas; avoid generic complaints with no verification path.
- Reuse `../auto-research-common/` for source policy, schema, rendering, and knowledge-base updates.

## Workflow

1. Build or reuse a topic profile with bilingual aliases, subtopics, likely venues, datasets, and exclusion terms.
2. Search recent and representative sources; use `scripts/collect_sources.py` as an initial arXiv/OpenAlex/GitHub pass when useful.
3. Cluster evidence into 4-8 gaps. For each gap record:
   - `name`: concise gap name.
   - `gap_type`: method, data, evaluation, deployment, theory, tooling, or product.
   - `description`: what is missing or weak.
   - `why_it_matters`: why the gap blocks progress or adoption.
   - `closest_work`: the most relevant prior work or baseline.
   - `actionable_opportunity`: what a researcher could test next.
   - `confidence`: high, medium, or low.
   - `risk`: why the gap may be hard or already partially solved.
   - `source_ids`: evidence links.
4. Build report JSON with `mode: "gap-analysis"`, fill `gaps`, `summary_judgments`, `risks`, `next_queries`, `queries`, and `sources`.
5. Render with `../auto-research-common/scripts/render_report.py --update-kb`.

## Quality bar

- Report distinguishes real evidence-backed gaps from speculative opportunities.
- Each gap has at least one source and a concrete verification route.
- Output is suitable as input to `$research-idea-planning`.
