---
name: research-idea-expansion
description: Expand one selected idea from a saved research report, idea-planning output, yearly full-cycle report, gap report, or user-provided idea into multiple executable research routes with source-backed paper/repository investigation, static open-source code/framework reading, feasibility assessment, recommended route, and Chinese HTML output. Use when asked to 深挖某个 idea, 扩充 idea, 路线扩展, 开源代码框架调研, 静态代码阅读, 可行性评估, or turn a report idea into actionable routes before experiment-roadmap.
---

# Research Idea Expansion

Use this skill to expand exactly one selected research idea into several implementable routes before committing to an `experiment-roadmap`.

## Operating rules

- Expand one idea at a time. If the report contains multiple plausible matches and the user did not identify one by name, index, or unique keyword, list candidates and ask for selection.
- Treat the source report as the baseline context, not as proof that the idea is novel or feasible.
- Perform static investigation only: read papers, project pages, README files, licenses, configs, scripts, model/data entrypoints, and key modules. Do not train, run benchmarks, launch jobs, modify external code, or claim empirical results.
- Prefer public, citable sources. Mark abandoned repositories, unclear licenses, missing data, and non-reproducible claims as feasibility risks.
- Default output language is Chinese; keep original method, dataset, repository, metric, and file/module names in English.
- Reuse `../auto-research-common/` for source policy, schema, rendering, archiving, and knowledge-base updates.

## Inputs

Collect the minimum context needed:

- `report_path`: saved JSON/HTML report when available; prefer JSON because it preserves structured `ideas`, `gaps`, `trend_clusters`, `sources`, and `stage_artifacts`.
- `idea_selector`: idea name, ranking/index, stable ID, quote, or distinctive keyword.
- Optional constraints: target venue, compute budget, available datasets, timeline, engineering stack, and whether routes should emphasize method, data, evaluation, deployment, or theory.

If only HTML is available, extract the visible idea text and nearby headings, then recover source links from the page. If the report path is absent, use the user-provided idea as the baseline and state the missing-context limitation.

## Workflow

1. Load the selected idea and nearby context:
   - topic, topic profile, time window, summary judgments;
   - relevant gaps, trend clusters, paper traces, prior ideas, and experiment roadmap if present;
   - source IDs and URLs that directly support the selected idea.
2. Freeze the idea baseline in the report:
   - original wording;
   - problem anchor;
   - proposed mechanism;
   - closest prior work from the source report;
   - novelty/feasibility uncertainties that must be checked.
3. Build an investigation plan:
   - 3-8 paper/product/repository queries;
   - repository search terms and likely frameworks;
   - code-reading targets such as `README`, `LICENSE`, `requirements`, configs, training/inference entrypoints, dataset loaders, model modules, evaluation scripts, checkpoints, and examples.
4. Gather and verify evidence:
   - use web search and public APIs when current information matters;
   - inspect candidate repositories statically with `git clone` or source browsing when useful;
   - record repository activity, license, install friction, data/checkpoint availability, key modules, extensibility seams, and incompatibilities.
5. Generate 3-6 executable routes. Each route should include:
   - route name and research thesis;
   - implementation sketch with concrete modules or framework hooks;
   - required datasets/checkpoints/baselines;
   - expected novelty delta against closest work;
   - minimum validation plan for humans;
   - compute/time rough order, not a job launch;
   - main failure modes and stop/go gate;
   - source IDs.
6. Build a feasibility matrix across routes:
   - novelty potential;
   - implementation effort;
   - data availability;
   - evaluation clarity;
   - reproducibility risk;
   - likely paper story strength;
   - overall recommendation.
7. Recommend an execution order:
   - safest baseline reconstruction;
   - shortest decisive prototype;
   - stretch route;
   - fallback if the strongest route is blocked.
8. Build report JSON with `mode: "idea-expansion"`:
   - `summary_judgments`: 2-4 top-level decisions;
   - `findings`: source-backed paper/repo/framework observations;
   - `sections`: include at least `原始 idea 基准`, `可执行路线`, `开源代码框架静态调研`, `可行性矩阵`, and `推荐推进顺序`;
   - optionally include one `ideas` card for the refined selected idea, but do not create a broad idea list;
   - `risks`, `next_queries`, and `sources`.
9. Render with `../auto-research-common/scripts/render_report.py --update-kb`; add `--archive-output` for repeated topic work or if the report directory already contains multiple dated artifacts.

## Quality bar

- The selected idea is identifiable and anchored to the source report or explicitly marked as user-provided.
- Routes are concrete enough for a human to choose the next engineering step, but do not pretend experiments were already run.
- Repository feasibility is based on static evidence: files, modules, examples, releases, issues, license, and data/checkpoint availability.
- Claims distinguish facts, inferences, and speculative route design.
- The output can feed `experiment-roadmap`, which should then plan claims, ablations, metrics, and run order for one chosen route.
