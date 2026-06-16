---
name: formula-derivation
description: Prepare theory-oriented research directions by structuring variables, assumptions, derivation steps, sanity checks, and validation conditions without proving final theorems or running experiments.
---

# Formula Derivation

Use this skill when the user asks for 理论推导, 公式推导, mathematical modeling, assumptions, derivation plan, or turning a research idea into a coherent theory-preparation package.

## Operating rules

- This is a preparation skill, not an experiment or proof automation pipeline.
- Do not claim a theorem is proven unless the user provides a complete proof that can be checked locally.
- Keep output in Chinese by default; preserve original names for methods, variables, metrics, and datasets.
- Reuse `../auto-research-common/` for schema, rendering, and knowledge-base updates.

## Workflow

1. Load relevant context if present: user notes, paper traces, gap reports, idea-planning reports, or `knowledge_base/<topic_slug>/` entries.
2. Identify the target claim, modeling object, measurable quantities, and non-goals.
3. Build a derivation package:
   - `problem_setup`: what the derivation tries to explain or predict.
   - `assumptions`: explicit assumptions and where they may fail.
   - `symbols`: symbol, meaning, domain, and units if useful.
   - `derivation_steps`: numbered steps with statement, justification, and dependencies.
   - `sanity_checks`: limiting cases, dimensional checks, monotonicity, or counterexamples.
   - `failure_modes`: where the derivation may become invalid.
   - `next_validation`: minimal analytical or empirical checks for humans.
4. Build report JSON with `mode: "formula-derivation"`, fill `formula_derivation`, `summary_judgments`, `risks`, `next_queries`, and `sources` when evidence is used.
5. Render with `../auto-research-common/scripts/render_report.py --update-kb`.

## Quality bar

- Every symbol is defined before use.
- Every assumption is visible and tied to at least one risk or sanity check.
- The output can feed `$research-idea-planning` or `$experiment-roadmap`, but does not execute validation.
