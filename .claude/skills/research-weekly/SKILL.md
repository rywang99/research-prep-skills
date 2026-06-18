---
name: research-weekly
description: Produce a weekly automated research report for a domain, covering the last 7 days of papers, projects, product updates, and technical signals with clustered analysis and HTML output.
---

# Research Weekly

Use this skill for 周报, 本周进展, weekly domain updates, or last-7-day research scans.

## Window

- Default: rolling last 7 days.
- If the user says 本周, use the current calendar week and state the start/end dates.

## Search plan

- Use bilingual topic/profile queries plus subtopic-specific queries.
- Use `scripts/collect_sources.py` for an initial arXiv/OpenAlex/GitHub candidate set before manual source review.
- Balance academic and industry sources: arXiv, proceedings pages, GitHub, official blogs, technical reports, release notes, and credible news.
- Pull in local `knowledge_base/<topic_slug>/collected_sources.jsonl` and `sources.jsonl` to avoid repeating old items unless they changed this week.

## Report content

- Group updates into 3-6 lightweight themes, but do not fill `keywords` or `trend_clusters` unless the user explicitly asks for them.
- For each theme: new evidence, why it matters, affected methods/products/datasets, confidence, and next thing to watch.
- Include a table for notable papers/projects/releases.
- Add "本周变化 vs 既有背景" so readers can distinguish new information from context.
- Automatically trace every traceable paper source in the weekly window and embed the analysis as expanded HTML.

## Output

Build the JSON described in `../auto-research-common/references/report_schema.md` with `mode: "weekly"`, run `python3 scripts/trace_report_papers.py --report <report.json>` (default `--jobs 8`), then render using `../auto-research-common/scripts/render_report.py`.
