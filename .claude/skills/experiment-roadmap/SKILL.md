---
name: experiment-roadmap
description: Convert a selected research idea into a claim-driven experiment roadmap with baselines, ablations, metrics, run order, risks, and stop/go gates, without executing experiments.
---

# Experiment Roadmap

Use this skill when the user asks for 实验规划, validation plan, ablation plan, evaluation protocol, run order, compute budget, or how to prove a selected idea before implementation.

## Operating rules

- Planning only: do not create experiment code, configs, queues, training jobs, or monitoring processes.
- Start from claims, not from a benchmark wishlist.
- Prefer a compact must-run plan plus optional nice-to-have blocks.
- Default output language is Chinese; keep dataset, metric, baseline, and model names unchanged.
- Reuse `../auto-research-common/` for rendering and persistence.

## Workflow

1. Load the selected idea from user prompt, `research-idea-planning` output, or local notes.
2. Freeze the claim map:
   - primary claim;
   - optional supporting claim;
   - anti-claim to rule out;
   - minimum convincing evidence.
3. Specify experiment blocks for main result, novelty isolation, simplicity check, frontier-primitive necessity, and failure analysis only when needed.
4. For each block record dataset/task, compared systems, metrics, success criterion, failure interpretation, and table/figure target.
5. Build an execution order for humans: sanity, baseline, main method, decisive ablations, polish.
6. Build report JSON with `mode: "experiment-roadmap"` and an `experiment_roadmap` object containing `claims`, `blocks`, and `milestones`.
7. Render with `../auto-research-common/scripts/render_report.py --update-kb`.

## Quality bar

- The roadmap makes clear what must be run before implementation effort scales up.
- Each ablation answers a reviewer question or removes a confound.
- Negative outcomes have explicit interpretations and stop/go gates.
