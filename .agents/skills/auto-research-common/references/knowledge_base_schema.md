# Knowledge Base Schema

The knowledge base is a local, append-oriented store under `knowledge_base/<topic_slug>/`. Standalone paper traces use `knowledge_base/paper-trace/<category_slug>/`. Generated user data is ignored by Git; only `.gitkeep` placeholders are tracked.

## Versioning

- Current `schema_version`: `1.0`.
- New writers should include `schema_version` in report JSON, `sources.jsonl`, `runs.jsonl`, `keywords.json`, `entities.jsonl`, `links.jsonl`, and `graph_latest.json`.
- Readers should tolerate missing `schema_version` because older local runs may not have it.
- Do not rewrite historical JSONL rows for routine migrations; add new fields and keep readers backward-compatible.

## Files

- `sources.jsonl`: append-only source records. Each row preserves source metadata plus `topic`, `mode`, `run_id`, `recorded_at`, and `schema_version` when available.
- `runs.jsonl`: append-only report/run summaries with counts, report path, time window, and graph sizes.
- `keywords.json`: latest lightweight snapshot for quick reuse. Daily/weekly modes intentionally write empty keyword lists.
- `entities.jsonl`: append-only lightweight graph entities from each run.
- `links.jsonl`: append-only lightweight graph edges from each run.
- `graph_latest.json`: latest per-run graph snapshot for quick inspection and query tooling.

## Entity Types

- `source`: cited paper, repository, blog, news, dataset, benchmark, product, or signal.
- `keyword`: hotword, method name, dataset, benchmark, or recurring technical term.
- `trend`: trend cluster from yearly or strategic reports.
- `gap`: evidence-backed research gap or bottleneck.
- `idea`: ranked research idea with novelty metadata when available.
- `claim`: experiment-roadmap claim.
- `formula_derivation`: theory-preparation package from formula-derivation mode.

## Link Relations

- `supports`: a source supports a keyword, trend, gap, or idea.
- `mentions`: a trend mentions or is associated with a keyword.
- `addresses`: an idea addresses a gap.
- `derived_from`: a gap or derivation is derived from a trend/source.
- `validates`: a claim or derivation points to an idea it helps validate.

## Compatibility Rules

- Treat `id`, `type`, `name`, `topic`, `mode`, `run_id`, and `recorded_at` as stable entity fields.
- Treat `id`, `source`, `relation`, `target`, `topic`, `mode`, `run_id`, and `recorded_at` as stable link fields.
- Additional fields are allowed and should be ignored by older readers.
- Entity IDs are deterministic within a type and human-readable where possible; link IDs are stable hashes for one run.
