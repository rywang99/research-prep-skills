---
name: research-independent-evaluator
description: "Independently score saved auto-research artifacts, yearly full-cycle stages, reports, source sets, idea plans, gap analyses, experiment roadmaps, or formula-derivation outputs with a rubric and Chinese HTML scorecard. Use when users ask for 独立评分, independent evaluation, judge reports, rubric scoring, quality gates, re-score after iteration, or evaluation separate from content generation."
---

# Research Independent Evaluator

Use this skill to judge already-generated research artifacts. Keep evaluation independent: read saved outputs and cited sources, score them, and write a separate evaluation report without improving the original artifact in the same pass.

## Independence rules

- Do not generate, rewrite, or optimize the artifact being scored during the same evaluator pass.
- Prefer inputs from saved report JSON/HTML, `knowledge_base/<topic_slug>/`, and cited source URLs.
- State when a score depends on inaccessible, missing, or weak evidence.
- Score each stage independently; do not let a strong yearly report hide a weak idea plan or roadmap.
- Keep default output language Chinese while preserving original English technical names.

## Default rubric

Use a 100-point score unless the user supplies another rubric:

- Evidence quality: 20 points for primary sources, source credibility, claim-source alignment, and confidence labels.
- Coverage completeness: 15 points for academic, open-source, product, benchmark, dataset, and community coverage appropriate to the scope.
- Freshness and deduplication: 10 points for exact dates, window fit, duplicate clustering, and latest/current checks.
- Trend and gap judgment: 15 points for grounded synthesis, maturity assessment, bottleneck clarity, and falsifiable watchpoints.
- Idea novelty: 15 points for closest-prior-work comparison, novelty verdict, novelty risk, and evidence-backed differentiation.
- Verifiability: 15 points for validation path, metrics, baselines, ablations, stop/go gates, or analytical checks.
- Risk calibration: 10 points for failure modes, weak evidence disclosure, privacy/security limitations, and non-overclaiming.

## Verdict gates

- `pass`: total score is `>=80` and no severe blocking issue exists.
- `pass_with_improvements`: total score is `70-79` and all serious issues are actionable.
- `needs_iteration`: total score is `<70` or a key stage lacks enough credible sources.
- `blocked`: unsupported central claims, broken source links for critical claims, privacy-sensitive inputs, or missing required artifact.

## Output shape

Build a report JSON using `mode: "independent-evaluation"` and fill `evaluation_scorecards`:

- `scorecard_id`: stable id such as `eval-ideas-v1`.
- `artifact_id`: stage id or report id being evaluated.
- `artifact_path`: JSON/HTML path or KB reference.
- `evaluator`: normally `research-independent-evaluator`.
- `rubric_version`: default `research-quality-v1`.
- `scores`: list of rubric dimensions with `dimension`, `score`, `max_score`, `rationale`, and optional `source_ids`.
- `total_score`: integer 0-100.
- `verdict`: pass, pass_with_improvements, needs_iteration, or blocked.
- `blocking_issues`: unsupported claims or missing artifacts that stop progression.
- `required_iterations`: concrete changes for the generator to perform in a later pass.
- `evaluated_at`: ISO datetime.

Render with `../auto-research-common/scripts/render_report.py --update-kb` so evaluation entities are appended to the knowledge base.
