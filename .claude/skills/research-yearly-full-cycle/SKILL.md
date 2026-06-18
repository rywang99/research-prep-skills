---
name: research-yearly-full-cycle
description: "Orchestrate a year-long full-cycle research workflow for one domain: monthly evidence slices, yearly hotwords/trends, gap analysis, idea planning, experiment roadmap or formula-derivation preparation, independent evaluation, iteration logs, optional long-task tracking when explicitly requested, and Chinese HTML outputs. Use when users ask for 全年全流程, 一整年技能调研, 长时自动化调研, 迭代优化, independent scoring, or end-to-end research preparation across a full year."
---

# Research Yearly Full Cycle

Use this skill for long-running, full-year research preparation before humans run experiments. It composes the existing auto-research skill family and adds stage tracking, independent evaluation, and targeted iteration.

## Boundaries

- Keep the repository boundary: prepare research, do not run experiments, train models, write submissions, or claim empirical results.
- Generate Chinese reports; preserve English method names, datasets, benchmarks, venues, repositories, and product names.
- Treat freshness as critical. Use explicit dates for the rolling 365-day window and every monthly slice.
- Save stage outputs under `reports/<topic_slug>/` and update `knowledge_base/<topic_slug>/` unless the user asks not to persist.
- Use platform goal/status tracking only when the user explicitly requests it and the current environment provides a goal tool; otherwise record progress in `stage_artifacts`, `evaluation_scorecards`, and `iteration_log`.

## Default yearly workflow

1. Define the annual window as the 365 days ending at `snapshot_date`; split it into 12 continuous monthly slices.
2. Build a shared topic profile with aliases, subtopics, broader terms, exclusions, and likely sources.
3. Produce or summarize monthly evidence slices using `research-monthly`; each slice records sources, findings, queries, and limitations.
4. Run long-range synthesis from the same evidence base:
   - `research-yearly-hotwords` for keywords, aliases, growth signal, and reusable queries.
   - `research-yearly-trends` for 4-8 trend clusters, maturity, risks, and watchpoints.
5. Run preparation stages:
   - `research-gap-analysis` from trend, monthly, and paper evidence.
   - `research-idea-planning` to generate and rank 3-7 evidence-anchored ideas.
   - `experiment-roadmap` for empirical ideas, or `formula-derivation` before roadmap for theory-heavy ideas.
6. Run `research-independent-evaluator` after each major stage and after any required iteration.
7. Build a final `yearly-full-cycle` report with `cycle_plan`, `stage_artifacts`, `evaluation_scorecards`, `iteration_log`, sources, risks, and next queries.

## Long-task tracking

If the user explicitly requested long-task tracking:

1. If the environment provides a goal tool, create one objective such as `完成 <topic> 的全年全流程调研、独立评分和至少一轮必要迭代`.
2. Use external goal/status tools as status tracking only; keep durable data in reports and the knowledge base.
3. If no goal tool is available, treat `stage_artifacts`, `evaluation_scorecards`, and `iteration_log` as the tracking source of truth.
4. Mark external tracking complete only after all required stage outputs and required re-evaluations are finished.
5. Mark external tracking blocked only when the same blocker repeats and no meaningful progress remains.

## Stage artifacts

Record every stage in `stage_artifacts`:

- `stage_id`: stable id such as `M01`, `hotwords`, `trends`, `gaps`, `ideas`, `roadmap`, or `evaluation-ideas`.
- `mode`: registered mode id.
- `status`: planned, running, complete, needs_iteration, blocked, or skipped.
- `input_artifacts`: report or knowledge-base paths used as inputs.
- `json_path` and `html_path`: output paths when generated.
- `depends_on`: prior stage ids.
- `notes`: concise caveats, missing evidence, or scope decisions.

## Iteration rules

- Treat the independent evaluator as separate from generation. Do not ask it to improve the report while scoring it.
- Default score gates: `>=80` pass; `70-79` pass with required improvements recorded; `<70` requires one targeted iteration before continuing.
- A severe citation or unsupported-claim issue blocks the stage even when the numeric score is high.
- Targeted iterations should change only the weakest stage: add queries, replace weak sources, narrow claims, revise idea ranking, or clarify roadmap gates.
- Record every iteration in `iteration_log` with trigger scorecard, action, changed artifact, and re-evaluation result.

## Final report quality bar

- Includes annual window, 12 monthly slices, stage dependency map, source count, and query list.
- Shows independent scorecards separately from generated content.
- Explains skipped stages and blockers explicitly.
- Uses `--update-kb` so future weekly/monthly/idea workflows can reuse the yearly artifacts.
