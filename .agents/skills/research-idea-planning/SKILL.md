---
name: research-idea-planning
description: Generate, screen, and rank research ideas from domain reports, gap analyses, paper traces, or user constraints without running experiments; produce a Chinese HTML planning report.
---

# Research Idea Planning

Use this skill when the user asks for 找 idea, 课题构思, idea planning, research direction selection, or publishable ideas based on a domain, gap report, or paper trace.

## Operating rules

- This is not an autonomous experiment pipeline. Do not run pilots, create training scripts, launch jobs, or claim empirical results.
- Ideas must be anchored in sourced gaps, recent trends, or a specific paper's limitations.
- Prefer a small ranked shortlist over many shallow ideas.
- Default output language is Chinese; keep original technical names.
- Reuse `../auto-research-common/` for schema and rendering.

## Workflow

1. Read relevant local context if present: prior `reports/<topic_slug>/`, `knowledge_base/<topic_slug>/`, paper traces, or user-provided notes.
2. Identify problem anchors and constraints: target venue/audience, available data, compute, timeline, and non-goals.
3. Generate 3-7 idea cards. Each idea should include:
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
   - `tags` and `source_ids`.
4. Rank ideas by novelty, feasibility, evidence fit, and story clarity.
5. Build report JSON with `mode: "idea-planning"`, fill `ideas`, `summary_judgments`, `risks`, `next_queries`, and `sources`.
6. Render with `../auto-research-common/scripts/render_report.py --update-kb`.

## Quality bar

- Every idea has a clear problem anchor and minimum validation path.
- Treat novelty check as an evaluation dimension inside this skill; do not invoke a separate novelty-check workflow.
- The report states which ideas are cut and why when relevant.
- Output can feed `$experiment-roadmap` for one selected idea.
