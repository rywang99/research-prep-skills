---
name: research-monthly
description: Produce a monthly automated research report for a domain, covering the last 30 days with papers, open-source projects, product movement, ecosystem shifts, and HTML output.
---

# Research Monthly

Use this skill for 月报, 本月进展, monthly domain review, or last-30-day research scans.

## Window

- Default: rolling last 30 days.
- If the user says 本月, use the current calendar month and state the start/end dates.

## Search plan

- Search by topic aliases, subtopics, venues, benchmark/dataset names, company/lab names, and GitHub keywords.
- Use `scripts/collect_sources.py` for reusable arXiv/OpenAlex/GitHub candidates before adding web-only sources.
- Include sources from academic papers, code releases, product/technical blogs, standards/specs, datasets, benchmark leaderboards, and credible analysis.
- Use local `collected_sources.jsonl`, `sources.jsonl`, and prior runs to identify genuinely new clusters and recurring themes.

## Report content

- Summarize the month in 4-6 core judgments.
- Split findings by papers, projects/tools, product/industry, datasets/benchmarks, and risks/open questions.
- Highlight compounding signals: multiple sources pointing to the same method, evaluation bottleneck, or deployment direction.
- Include a "下月追踪清单" with concrete queries.

## Output

Build the JSON described in `../auto-research-common/references/report_schema.md` with `mode: "monthly"`, then render using `../auto-research-common/scripts/render_report.py`.
