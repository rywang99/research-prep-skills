---
name: research-yearly-trends
description: Analyze research trends for a domain over the last year by clustering source-backed evidence, identifying drivers, maturity, risks, opportunities, and generating an HTML trend report.
---

# Research Yearly Trends

Use this skill for 近一年趋势, trend analysis, future direction, research roadmap, opportunity mapping, or annual strategic review.

## Window

- Default: rolling last 365 days.
- State exact start and end dates.

## Search plan

- Combine broad survey-style queries with targeted subtopic and source queries.
- Use `scripts/collect_sources.py` to seed academic and repository evidence, then add product, standard, and community sources manually.
- Cover papers, projects, datasets, benchmarks, product announcements, standards, and prominent community discussions.
- Use historical `collected_sources.jsonl`, `sources.jsonl`, and run entries when available to compare recurrence and novelty.

## Analysis method

Group evidence into 4-8 trend clusters. For each cluster, include:

- Trend name and concise thesis.
- Evidence timeline and representative sources.
- Drivers: technical, data, compute, product, regulation, or ecosystem.
- Evidence strength: strong, medium, weak, with reason.
- Maturity: exploratory, fast-growing, consolidating, or deployed.
- Opportunities, risks, and falsifiable watchpoints.

Separate "real trend" from "temporary hype" when evidence is thin.

## Output

Build the JSON described in `../auto-research-common/references/report_schema.md` with `mode: "yearly-trends"`, filling `trend_clusters`, then render using `../auto-research-common/scripts/render_report.py`.
