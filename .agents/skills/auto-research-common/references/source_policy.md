# Source Policy

## Priority

Use the strongest available source for each claim:

1. Primary source: paper PDF/arXiv/OpenReview/proceedings, official project page, official GitHub release, company/lab blog, standard/spec page, dataset or benchmark page.
2. Secondary technical source: credible engineering blog, conference recap, reputable technical media, maintainer discussion.
3. Community signal: GitHub issues, Hacker News, Reddit, X/Twitter, Zhihu, forum posts. Use only as weak evidence unless confirmed elsewhere.

## Required metadata

Record these fields for every source when available:

- `title`
- `url`
- `source_type`: paper, repo, blog, news, benchmark, dataset, standard, community, product, signal, other
- `published_at` or best-known date
- `accessed_at`
- `authors_or_org`
- `summary`
- `tags`
- `confidence`: high, medium, low

## Citation rules

- Do not cite a source for claims it does not support.
- Prefer paraphrase over long quotation.
- For latest/current claims, include exact dates in the report.
- If a source date is ambiguous, mark it as `date_unknown` or explain in the finding.

## Deduplication

Cluster equivalent sources:

- Same paper on arXiv, project page, and GitHub -> one finding with related links.
- News article repeating an official announcement -> cite official source first, news second only for additional context.
- Forks or mirrors -> keep original repository unless the fork contains meaningful new work.

## Confidence labels

- `high`: primary source, clear date, direct evidence, or independently confirmed by multiple strong sources.
- `medium`: credible source but partial evidence, indirect inference, or single-source support.
- `low`: community signal, unclear date, speculation, or insufficient confirmation.

## Scope defaults

Unless the user narrows scope, cover both academic and industry sources. For academic-only requests, still include official code/dataset pages attached to papers. For industry-only requests, include papers only when they explain a product or technical direction.
