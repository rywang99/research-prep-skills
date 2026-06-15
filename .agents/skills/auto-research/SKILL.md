---
name: auto-research
description: Orchestrate automated research for a user-provided domain by expanding the topic, choosing daily/weekly/monthly/yearly-hotword/yearly-trend workflows, collecting current web evidence, updating the local knowledge base, and producing a self-contained Chinese HTML report.
---

# Auto Research

Use this skill when the user asks for automated research, domain monitoring, literature/industry updates, hotword mining, trend analysis, or an HTML research report for a topic.

## Operating rules

- Always treat freshness as critical. For daily/weekly/monthly/yearly tasks, browse the web and use explicit date windows.
- Default output language is Chinese; keep original English titles, acronyms, model names, venues, repositories, and product names.
- Use the shared assets in `../auto-research-common/` for mode registry, source policy, report schema, rendering, and HTML style.
- Save outputs under the current repo: `reports/<topic_slug>/YYYY-MM-DD_<mode>.html` and `knowledge_base/<topic_slug>/`.
- Do not depend on any external template path; the bundled template is the only style source.
- When useful, start source discovery with `scripts/collect_sources.py` from the repository root; it collects arXiv, OpenAlex, and GitHub candidates without API keys.

## Route the task

1. Extract the topic, expected mode, audience, and any constraints from the user request.
2. Read `../auto-research-common/config/research_modes.json` for the registered modes and labels.
3. If mode is absent, infer from wording:
   - 今日/今天/最新动态 -> `research-daily`
   - 本周/周报/最近一周 -> `research-weekly`
   - 本月/月报/最近一个月 -> `research-monthly`
   - 热词/关键词/高频词/爆发词 -> `research-yearly-hotwords`
   - 趋势/方向/路线/未来机会 -> `research-yearly-trends`
4. If multiple modes are requested, run them independently but reuse the same topic profile and knowledge base.
5. If the user only gives a topic, default to `research-weekly` unless they ask for long-range strategy, then use `research-yearly-trends`.
6. For newly added modes, follow `../auto-research-common/references/extension_guide.md` and route by the registry entry.

## Build the topic profile

Create a compact topic profile before searching:

- Chinese and English topic names.
- Acronyms, aliases, translations, spelling variants, and adjacent terms.
- 3-8 narrower subtopics and 3-5 broader umbrella terms.
- Exclusion terms to avoid unrelated meanings.
- Likely sources: arXiv areas, conferences, GitHub topics, companies, labs, product categories, and community keywords.

Use the profile to generate bilingual search queries. Record the final query list in the report JSON.

## Evidence workflow

1. Read `../auto-research-common/references/source_policy.md`.
2. Generate search queries, then optionally run `python3 scripts/collect_sources.py --topic "<topic>" --query "<query>" --sources arxiv,openalex,github --window-days <days> --limit-per-source 10`.
3. Gather additional web sources across academic and industry channels unless the user narrows scope.
4. Review the collected JSONL manually; do not cite a candidate source until its content supports the claim.
5. Deduplicate source clusters: paper + project page + reposts become one finding with related links.
6. For every non-obvious claim, attach a source URL and access date.
7. Mark weak evidence explicitly instead of overstating.
8. Convert findings into the schema in `../auto-research-common/references/report_schema.md`.
9. Render with `../auto-research-common/scripts/render_report.py`.
10. Use `--update-kb` unless the user asked not to persist data.

## Report emphasis

- Daily/weekly/monthly: what changed, why it matters, affected subareas, and what to watch next.
- Hotwords: term, aliases, evidence count, growth signal, source spread, representative sources, and research implication.
- Trends: cluster, timeline signal, drivers, evidence strength, maturity, open questions, and actionable opportunities.

## Minimum quality bar

- HTML report opens standalone in a browser.
- Report includes snapshot date, time window, source count, source links, query list, and next queries.
- Knowledge base receives source, keyword, and run entries for later reuse.
- If less than 5 credible sources are found for a broad topic, state the limitation and suggest narrower follow-up queries.
