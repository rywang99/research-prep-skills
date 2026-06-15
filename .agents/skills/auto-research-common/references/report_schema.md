# Report JSON Schema

The renderer expects one JSON object. Required fields are marked with `required`.

```json
{
  "topic": "required: human-readable topic",
  "topic_slug": "optional: filesystem-safe slug; renderer can derive one",
  "mode": "required: registered mode id from config/research_modes.json, e.g. daily | weekly | monthly | yearly-hotwords | yearly-trends",
  "generated_at": "optional ISO datetime",
  "snapshot_date": "optional YYYY-MM-DD",
  "time_window": {
    "label": "required: human-readable window",
    "start": "optional YYYY-MM-DD",
    "end": "optional YYYY-MM-DD"
  },
  "language": "optional, default zh-CN",
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
- `summary_judgments`, `findings`, and `sources` should normally be non-empty for real reports.
- `topic_slug` is sanitized if omitted.
- `--update-kb` appends source records and run metadata under `knowledge_base/<topic_slug>/`.
- Extra source provenance fields from `scripts/collect_sources.py` are preserved in the knowledge base and ignored by the HTML renderer unless explicitly displayed.
