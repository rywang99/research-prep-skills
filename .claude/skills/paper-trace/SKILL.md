---
name: paper-trace
description: Analyze one paper with AI-assisted technical lineage, reproduction risk, and reading priorities; generate HTML-first trace reports without caching or annotating PDFs.
---

# Paper Trace

Use this skill when the user asks to analyze a specific paper, trace its technical origins, compare it with prior work, identify reproduction risks, or produce AI-assisted reading notes for a paper.

## Operating rules

- Default output language is Chinese; keep original paper titles, method names, datasets, metrics, venues, model names, and code repository names.
- Do not cache PDFs or write PDF annotations. If full text is needed, use temporary extraction only and let the helper clean up after the run.
- Prefer arXiv/OpenReview/proceedings pages, official PDFs, official project pages, and official code or dataset links.
- If the user provides only a title, first locate the strongest official URL; then call the helper with the URL or arXiv ID.
- Be explicit when analysis is based only on metadata/abstract because full text extraction failed or no official PDF was available.
- Render trace analysis as Chinese narrative. Do not paste or preserve extracted English source sentences in the trace body.

## Inputs

Accept any of these inputs:

- arXiv ID, for example `2606.13095` or `arXiv:2606.13095`.
- arXiv abstract URL or direct PDF URL.
- Local PDF path; the file is read but not copied into a cache.
- Paper title; locate an official URL before running the helper when possible.

## Standard workflow

```bash
python3 scripts/trace_single_paper.py \
  --paper "<arxiv id/url/pdf/title>" \
  --topic "<optional research topic>"
```

The helper writes:

- `reports/paper-trace/<category_slug>/<method_slug>.json`
- `reports/paper-trace/<category_slug>/<method_slug>.html`
- knowledge-base entries under `knowledge_base/paper-trace/<category_slug>/` unless `--no-update-kb` is passed

Default categorization and naming:

- If `--topic` is provided, use it as the paper category first; otherwise infer the category from title, abstract, tags, and arXiv metadata.
- Use the paper's method short name for `method_slug`: prefer the title prefix before `:`/`：`, otherwise use the first method phrase before markers such as `in`, `using`, `via`, or `for`.
- Do not prefix standalone paper-trace reports with dates or arXiv IDs. If a method-name collision occurs for a different paper, append a short stable hash.
- Explicit `--output-json` or `--output-html` paths override these defaults.

## Trace content

Each trace should cover:

1. 论文一句话定位。
2. 核心问题与为什么现在重要。
3. 方法脉络：继承/组合的前置技术。
4. 与直接前作或强相关工作的差异。
5. 数据集、评测指标和实验协议的继承关系。
6. 代码、模型、数据和复现风险。
7. 中文重点阅读建议；不要展示英文原文摘句。
8. 后续追踪 query。

## Automatic daily/weekly trace

Daily and weekly research skills should run:

```bash
python3 scripts/trace_report_papers.py \
  --report reports/<topic_slug>/YYYY-MM-DD_<mode>.json
```

Defaults:

- Trace all report paper sources whose publication/finding date is inside the report `time_window`; report tracing runs concurrently with default `--jobs 8`.
- Embed results into the report JSON as `paper_traces`.
- Rendered HTML shows every trace as an expanded section, not a collapsible block.
- No `paper_cache/` directory or persistent PDF copy is created.

## Quality bar

- Standalone paper trace HTML opens locally and includes sources, reading priorities, technical lineage, experiment protocol, and reproduction risks.
- Daily/weekly reports either include `paper_traces` for every in-window traceable paper source or state why a paper was skipped.
- Every claim should be grounded in the paper metadata, extracted text, or an explicit source URL; uncertainty must be labeled.
