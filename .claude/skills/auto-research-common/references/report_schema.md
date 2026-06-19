# Report JSON Schema

The renderer expects one JSON object. Required fields are marked with `required`.

```json
{
  "schema_version": "optional, default 1.0; emitted to knowledge-base artifacts",
  "topic": "required: human-readable topic",
  "topic_slug": "optional: filesystem-safe slug; renderer can derive one",
  "mode": "required: registered mode id from config/research_modes.json, e.g. daily | weekly | monthly | yearly-hotwords | yearly-trends | gap-analysis | idea-planning | idea-expansion | experiment-roadmap | formula-derivation | paper-trace | yearly-full-cycle | independent-evaluation",
  "generated_at": "optional ISO datetime",
  "snapshot_date": "optional YYYY-MM-DD",
  "time_window": {
    "label": "required: human-readable window",
    "start": "optional YYYY-MM-DD",
    "end": "optional YYYY-MM-DD"
  },
  "language": "optional, default zh-CN",
  "paper_category_label": "optional for standalone paper-trace",
  "paper_category_slug": "optional for standalone paper-trace storage",
  "method_short_name": "optional for standalone paper-trace report naming",
  "method_slug": "optional for standalone paper-trace report naming",
  "topic_profile": {
    "aliases": ["topic aliases"],
    "subtopics": ["narrower terms"],
    "broader_terms": ["umbrella terms"],
    "exclusions": ["ambiguous terms to avoid"],
    "likely_sources": ["venues/labs/repos/company sources"]
  },
  "queries": [
    {"query": "search query", "purpose": "why it was used", "source": "web|arxiv|openalex|github|other"}
  ],
  "summary_judgments": [
    {"title": "judgment", "body": "short explanation", "tone": "green|blue|amber|red|purple", "sources": ["source-id"]}
  ],
  "metrics": [
    {"label": "papers", "value": "12", "note": "within window"}
  ],
  "cycle_plan": {
    "snapshot_date": "YYYY-MM-DD for the full-cycle run",
    "annual_window_label": "human-readable analysis window, default 365 days unless the user requested a different range",
    "stage_order": ["monthly", "yearly-hotwords", "yearly-trends", "gap-analysis", "idea-planning", "experiment-roadmap"],
    "goal_strategy": "how platform goal/status tracking is used, only when explicitly requested and available",
    "evaluation_strategy": "score gates and independent evaluator policy",
    "monthly_slices": [
      {"slice_id": "M01", "label": "month label", "start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "status": "complete|needs_iteration|blocked|skipped", "artifact_path": "optional report path"}
    ]
  },
  "stage_artifacts": [
    {
      "stage_id": "stable stage id, e.g. M01|hotwords|trends|gaps|ideas|roadmap",
      "mode": "registered mode id",
      "status": "planned|running|complete|needs_iteration|blocked|skipped",
      "input_artifacts": ["report or knowledge-base paths used as inputs"],
      "json_path": "optional output JSON path",
      "html_path": "optional output HTML path",
      "depends_on": ["stage-id"],
      "notes": "short limitation, caveat, or scope decision"
    }
  ],
  "findings": [
    {
      "title": "finding title",
      "date": "YYYY-MM-DD or text",
      "category": "paper|repo|product|dataset|benchmark|signal|other",
      "summary": "what changed",
      "importance": "why it matters",
      "confidence": "high|medium|low",
      "source_ids": ["source-id"],
      "tags": ["tag"]
    }
  ],
  "keywords": [
    {
      "term": "hotword",
      "aliases": ["alias"],
      "meaning": "domain-specific meaning",
      "frequency_signal": "high|medium|low or free text",
      "growth_signal": "accelerating|sustained|emerging|declining|unknown",
      "source_spread": "academic|industry|open-source|cross-domain|community",
      "evidence_count": 3,
      "source_ids": ["source-id"]
    }
  ],
  "trend_clusters": [
    {
      "name": "trend name",
      "thesis": "one-sentence trend claim",
      "drivers": ["driver"],
      "evidence_strength": "strong|medium|weak",
      "maturity": "exploratory|fast-growing|consolidating|deployed",
      "opportunities": ["opportunity"],
      "risks": ["risk"],
      "watchpoints": ["falsifiable thing to monitor"],
      "source_ids": ["source-id"]
    }
  ],
  "gaps": [
    {
      "name": "gap name",
      "gap_type": "method|data|evaluation|deployment|theory|tooling|product|other",
      "description": "what is missing or weak",
      "why_it_matters": "why this blocks progress",
      "closest_work": "closest prior work or baseline",
      "actionable_opportunity": "what could be tested next",
      "confidence": "high|medium|low",
      "risk": "why this gap may be hard or already partially solved",
      "tags": ["optional role or cluster tags, e.g. core-gap|exploratory-gap|long-horizon|cross-domain"],
      "source_ids": ["source-id"]
    }
  ],
  "ideas": [
    {
      "name": "idea title",
      "problem_anchor": "gap or pain point",
      "core_mechanism": "proposed mechanism",
      "novelty_delta": "difference from closest prior work",
      "closest_prior_work": "nearest paper, benchmark, repo, or method family",
      "novelty_verdict": "likely_new|incremental|overlap|uncertain",
      "novelty_evidence": ["source-backed reason or comparison"],
      "novelty_risk": "what could invalidate the novelty claim",
      "validation_path": "minimum evidence before implementation",
      "priority": "high|medium|low",
      "risk": "main failure risk",
      "tags": ["tag"],
      "source_ids": ["source-id"]
    }
  ],
  "experiment_roadmap": {
    "claims": [
      {"id": "C1", "claim": "claim to defend", "minimum_evidence": "what would convince a reviewer", "blocks": ["B1"]}
    ],
    "blocks": [
      {
        "name": "experiment block",
        "question": "reviewer question it answers",
        "dataset": "dataset/task/split",
        "systems": ["baseline or variant"],
        "metrics": ["metric"],
        "success_criterion": "positive outcome",
        "failure_interpretation": "what a negative result means",
        "figure_target": "main paper table/figure or appendix"
      }
    ],
    "milestones": [
      {"name": "stage name", "goal": "what to finish", "estimated_cost": "compute/time estimate", "gate": "stop/go condition"}
    ]
  },
  "formula_derivation": {
    "title": "optional derivation title",
    "problem_setup": "what the derivation tries to explain or predict",
    "assumptions": ["explicit modeling assumptions and boundaries"],
    "symbols": [
      {"symbol": "x", "meaning": "what it denotes", "domain": "domain, units, or constraints"}
    ],
    "derivation_steps": [
      {"id": "D1", "statement": "equation or intermediate claim", "justification": "why this step is allowed", "depends_on": "previous steps or assumptions"}
    ],
    "sanity_checks": ["limiting case, dimensional check, monotonicity check, or counterexample"],
    "failure_modes": ["where the derivation may break"],
    "next_validation": ["minimal analytical or empirical validation for humans"],
    "source_ids": ["source-id"]
  },
  "evaluation_scorecards": [
    {
      "scorecard_id": "stable evaluation id, e.g. eval-ideas-v1",
      "artifact_id": "stage id or report id being evaluated",
      "artifact_path": "JSON/HTML path or KB reference",
      "evaluator": "normally research-independent-evaluator",
      "rubric_version": "research-quality-v1",
      "scores": [
        {"dimension": "Evidence quality", "score": 18, "max_score": 20, "rationale": "why this score was assigned", "source_ids": ["source-id"]}
      ],
      "total_score": 82,
      "verdict": "pass|pass_with_improvements|needs_iteration|blocked",
      "blocking_issues": ["issue that stops progression"],
      "required_iterations": ["concrete next improvement"],
      "evaluated_at": "ISO datetime"
    }
  ],
  "iteration_log": [
    {
      "iteration_id": "stable iteration id",
      "stage_id": "stage that was iterated",
      "trigger_scorecard_id": "scorecard that triggered the iteration",
      "trigger_reason": "why iteration was needed",
      "action": "what changed in the next generation pass",
      "changed_artifact": "path or id of updated artifact",
      "result_scorecard_id": "scorecard after re-evaluation"
    }
  ],
  "paper_traces": [
    {
      "source_id": "source-id for the traced paper",
      "title": "paper title",
      "display_title": "中文卡片标题，例如 论文技术溯源",
      "url": "paper landing page",
      "published_at": "optional date",
      "authors_or_org": "optional authors",
      "trace_status": "ok|metadata_only|failed",
      "extraction_status": "pdf_temp_pdftotext|metadata_summary|other",
      "one_sentence_position": "what this paper is about",
      "core_problem": "problem and why it matters",
      "technical_lineage": ["predecessor methods, baselines, or inherited ideas"],
      "method_delta": ["what changed versus direct predecessors"],
      "experiment_protocol": ["datasets, metrics, baselines, ablations"],
      "reproducibility_risks": ["code/data/compute/protocol risks"],
      "reading_points": [
        {"category": "方法设计", "statement": "中文阅读建议，不粘贴原文摘句", "why_read": "为什么要重点阅读"}
      ],
      "follow_up_queries": ["queries for deeper tracing"],
      "evidence_urls": ["URLs used for trace"],
      "generated_at": "ISO datetime"
    }
  ],
  "sections": [
    {"title": "extra section", "tone": "blue|green|amber|red|purple", "items": ["bullet or paragraph"]}
  ],
  "risks": ["limitations or caveats"],
  "next_queries": ["query to run next"],
  "sources": [
    {
      "id": "source-id",
      "title": "required source title",
      "url": "required URL",
      "source_type": "paper|repo|blog|news|benchmark|dataset|standard|community|product|signal|other",
      "published_at": "optional date",
      "accessed_at": "required date",
      "authors_or_org": "optional",
      "summary": "optional",
      "tags": ["tag"],
      "confidence": "high|medium|low",
      "provider": "optional collector/provider name, e.g. arxiv|openalex|github",
      "query": "optional search query that found this source",
      "external_id": "optional provider identifier, e.g. DOI, arXiv ID, GitHub full_name",
      "collected_at": "optional ISO datetime when a collector recorded this candidate"
    }
  ]
}
```

## Renderer behavior

- Missing optional arrays render as empty sections.
- For `mode: "daily"` and `mode: "weekly"`, renderers ignore `keywords` and `trend_clusters` by default because these are lightweight update reports.
- `summary_judgments`, `findings`, and `sources` should normally be non-empty for real reports.
- `paper_traces` renders as expanded HTML cards and is used by daily/weekly paper trace automation.
- `gaps`, `ideas`, and `experiment_roadmap` are preparation-stage sections; they should not claim experiments were run unless source evidence already exists.
- `cycle_plan` and `stage_artifacts` render a yearly workflow map for `yearly-full-cycle`; they are optional for all other modes.
- `evaluation_scorecards` and `iteration_log` render independent evaluation and targeted iteration sections; scorecards should be generated separately from the artifact being scored.
- `topic_slug` is sanitized if omitted.
- `--update-kb` appends source records and run metadata under `knowledge_base/<topic_slug>/`; standalone `paper-trace` reports use `knowledge_base/paper-trace/<topic_slug>/`.
- `--update-kb` also writes lightweight graph artifacts: `entities.jsonl`, `links.jsonl`, and `graph_latest.json`. These cover source, keyword, trend, gap, idea, claim, formula-derivation, cycle-stage, and evaluation entities plus relations such as `supports`, `mentions`, `addresses`, `derived_from`, `validates`, `evaluates`, `improves`, and `blocks`; see `knowledge_base_schema.md` for compatibility rules.
- Extra source provenance fields from `scripts/collect_sources.py` are preserved in the knowledge base and ignored by the HTML renderer unless explicitly displayed.
