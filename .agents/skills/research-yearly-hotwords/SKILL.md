---
name: research-yearly-hotwords
description: Analyze research hotwords for a domain over the last year by mining source-backed keywords, aliases, frequency signals, source spread, and representative evidence into an HTML report.
---

# Research Yearly Hotwords

Use this skill for 近一年研究热词, keyword mining, hotword analysis, emerging terms, or terminology maps.

## Window

- Default: rolling last 365 days.
- State exact start and end dates.

## Search plan

- Gather enough evidence to compare term prominence across papers, repos, blogs, releases, benchmarks, and community discussions.
- Use `scripts/collect_sources.py` with broader query variants to seed arXiv/OpenAlex/GitHub evidence before manual filtering.
- Search seed terms plus "survey", "benchmark", "dataset", "leaderboard", "awesome", "roadmap", and major venue/company/lab names.
- Prefer sources with dates and stable URLs.

## Analysis method

For each candidate hotword, estimate:

- `frequency_signal`: how often it appears across independent sources.
- `growth_signal`: whether it is recent, accelerating, or sustained.
- `source_spread`: academic-only, industry-only, open-source, benchmark, or cross-domain.
- `meaning`: concise definition in this domain.
- `representative_sources`: 2-4 strongest examples where available.

Do not present generic umbrella words as hotwords unless the evidence shows a new domain-specific meaning.

## Output

Build the JSON described in `../auto-research-common/references/report_schema.md` with `mode: "yearly-hotwords"`, filling `keywords` carefully, then render using `../auto-research-common/scripts/render_report.py`.
