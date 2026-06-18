---
name: research-idea-planning
description: Generate, screen, and rank research ideas from domain reports, gap analyses, paper traces, or user constraints without running experiments; produce a Chinese HTML planning report.
---

# Research Idea Planning

Use this skill when the user asks for 找 idea, 课题构思, idea planning, research direction selection, or publishable ideas based on a domain, gap report, or paper trace.

## Operating rules

- This is not an autonomous experiment pipeline. Do not run pilots, create training scripts, launch jobs, or claim empirical results.
- Ideas must be anchored in sourced gaps, recent trends, or a specific paper's limitations.
- Prefer a broad but curated set over a tiny safe shortlist. Default to medium divergence unless the user asks for concise output.
- Default output language is Chinese; keep original technical names.
- Reuse `../auto-research-common/` for schema and rendering.

## Workflow

1. Read relevant local context if present: prior `reports/<topic_slug>/`, `knowledge_base/<topic_slug>/`, paper traces, or user-provided notes.
2. Identify problem anchors and constraints: target venue/audience, available data, compute, timeline, and non-goals.
3. Generate and screen ideas in two passes:
   - First create 15-30 raw candidates from gaps, trends, paper traces, cross-domain analogies, data opportunities, evaluation bottlenecks, and deployment constraints.
   - Merge duplicates, remove ideas with no validation path, and keep a final default set of 10-20 idea cards.
   - If fewer than 10 ideas survive, state why in `risks`.
4. Each final idea should include:
   - `name`: concise idea title.
   - `problem_anchor`: the gap or pain point it solves.
   - `core_mechanism`: the proposed mechanism, not just a buzzword.
   - `novelty_delta`: how it differs from closest prior work.
   - `closest_prior_work`: nearest paper, benchmark, repo, or method family.
   - `novelty_verdict`: one of `likely_new`, `incremental`, `overlap`, or `uncertain`.
   - `novelty_evidence`: short evidence bullets or source-backed reasons.
   - `novelty_risk`: what could invalidate the novelty claim.
   - `validation_path`: minimum evidence needed before implementation.
   - `priority`: high, medium, or low.
   - `risk`: main reason it may fail.
   - `tags`: use tags such as `high-priority`, `exploratory`, `long-horizon`, `theory`, `evaluation`, `data`, or `deployment`.
   - `source_ids`.
5. Rank ideas by novelty, feasibility, evidence fit, story clarity, and portfolio diversity.
6. Put cut candidates or near-misses into `sections` with short reasons when useful; do not over-expand them into full idea cards.
7. Build report JSON with `mode: "idea-planning"`, fill `ideas`, `summary_judgments`, `risks`, `next_queries`, and `sources`.
8. Render with `../auto-research-common/scripts/render_report.py --update-kb`.

## Quality bar

- Every idea has a clear problem anchor and minimum validation path.
- Treat novelty check as an evaluation dimension inside this skill; do not invoke a separate novelty-check workflow.
- Do not default to only 3-5 ideas for broad or yearly research requests; use 10-20 unless the user asks for a shortlist.
- Preserve idea diversity: include high-priority, exploratory, and long-horizon/theory-style options when evidence supports them.
- The report states which ideas are cut and why when relevant.
- Output can feed `experiment-roadmap` for one selected idea.
