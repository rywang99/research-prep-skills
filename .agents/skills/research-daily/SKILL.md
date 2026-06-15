---
name: research-daily
description: Produce a daily automated research report for a domain, focused on current-day or last-24-hour academic and industry updates with source-backed findings and HTML output.
---

# Research Daily

Use this skill for 今日动态, daily monitoring, today/latest updates, or last-24-hour research scans.

## Window

- Default: last 24 hours from the current time.
- If the user says 今日/今天, use the user's local calendar day and state the exact date.
- Include older context only when needed to explain why a new item matters.

## Search plan

- Use the topic profile from `auto-research` or create one if invoked directly.
- Use `scripts/collect_sources.py` for a first pass over arXiv, OpenAlex, and GitHub when those sources match the topic.
- Run bilingual queries with recency filters where possible.
- Prioritize official announcements, arXiv/new preprints, GitHub releases, company/lab blogs, conference pages, and credible technical news.

## Report content

- Lead with 3-5 newest items and their importance.
- Separate "confirmed updates" from "signals to verify".
- Include a compact timeline table: time/date, source, update, impact, link.
- End with watchlist queries for tomorrow.

## Output

Build the JSON described in `../auto-research-common/references/report_schema.md` with `mode: "daily"`, then render using `../auto-research-common/scripts/render_report.py`.
