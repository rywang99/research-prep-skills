#!/usr/bin/env python3
"""Collect candidate research sources from no-key public APIs.

The script intentionally stays dependency-free so it can run in a fresh checkout.
It produces JSONL records compatible with the auto-research report source schema,
plus a few provenance fields that help later review and deduplication.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True

from common_utils import now_iso, slugify, today_date, write_jsonl

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = ("arxiv", "openalex", "github")
TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_KEYS = {"fbclid", "gclid", "igshid", "mc_cid", "mc_eid", "ref", "source"}
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}

def as_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def parse_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return dt.datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    try:
        return dt.datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def within_window(date_text: str | None, cutoff: dt.date | None) -> bool:
    if cutoff is None:
        return True
    parsed = parse_date(date_text)
    return parsed is None or (cutoff <= parsed <= today_date())


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def canonical_url(value: str | None) -> str:
    if not value:
        return ""
    parsed = urllib.parse.urlsplit(value.strip())
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    path = re.sub(r"/+$", "", parsed.path)
    query_pairs = []
    for key, val in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True):
        if key in TRACKING_QUERY_KEYS or any(key.startswith(prefix) for prefix in TRACKING_QUERY_PREFIXES):
            continue
        query_pairs.append((key, val))
    query = urllib.parse.urlencode(query_pairs, doseq=True)
    return urllib.parse.urlunsplit((scheme, netloc, path, query, ""))


def arxiv_external_id(url: str) -> str:
    match = re.search(r"arxiv\.org/(?:abs|pdf)/([^?#]+)", url)
    if not match:
        return ""
    return match.group(1).removesuffix(".pdf")


def title_key(title: str) -> str:
    compact = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
    return hashlib.sha1(compact.encode("utf-8")).hexdigest()[:16] if compact else ""


def stable_source_id(provider: str, external_id: str, url: str, title: str) -> str:
    for raw in (external_id, canonical_url(url), title_key(title)):
        if raw:
            digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
            return f"src-{provider}-{digest}"
    return f"src-{provider}-{hashlib.sha1(now_iso().encode('utf-8')).hexdigest()[:12]}"


def dedup_key(record: dict[str, Any]) -> str:
    provider = as_text(record.get("provider"))
    external_id = as_text(record.get("external_id"))
    if external_id:
        return f"external:{provider}:{external_id.lower()}"
    url = canonical_url(as_text(record.get("url")))
    if url:
        return f"url:{url}"
    return f"title:{title_key(as_text(record.get('title')))}"


def make_record(
    *,
    provider: str,
    query: str,
    title: str,
    url: str,
    source_type: str,
    published_at: str | None = None,
    authors_or_org: str | None = None,
    summary: str | None = None,
    tags: Iterable[str] = (),
    confidence: str = "medium",
    external_id: str = "",
    collected_at: str | None = None,
) -> dict[str, Any]:
    clean_title = normalize_space(title)
    clean_url = canonical_url(url)
    record = {
        "id": stable_source_id(provider, external_id, clean_url, clean_title),
        "title": clean_title,
        "url": clean_url,
        "source_type": source_type,
        "published_at": published_at or "date_unknown",
        "accessed_at": today_date().isoformat(),
        "authors_or_org": normalize_space(authors_or_org or ""),
        "summary": normalize_space(summary or ""),
        "tags": list(dict.fromkeys([tag for tag in tags if tag])),
        "confidence": confidence,
        "provider": provider,
        "query": query,
        "external_id": external_id,
        "collected_at": collected_at or now_iso(),
    }
    return record


def http_json(url: str, timeout: int, headers: dict[str, str] | None = None) -> dict[str, Any]:
    req_headers = {"User-Agent": "auto-research-skills/0.1 (+https://github.com/local/auto-research-skills)"}
    if headers:
        req_headers.update(headers)
    request = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - user-initiated CLI fetch
        return json.loads(response.read().decode("utf-8"))


def http_text(url: str, timeout: int, headers: dict[str, str] | None = None) -> str:
    req_headers = {"User-Agent": "auto-research-skills/0.1 (+https://github.com/local/auto-research-skills)"}
    if headers:
        req_headers.update(headers)
    request = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - user-initiated CLI fetch
        return response.read().decode("utf-8")


def collect_arxiv(query: str, limit: int, cutoff: dt.date | None, timeout: int) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode(
        {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
    )
    feed = http_text(f"https://export.arxiv.org/api/query?{params}", timeout)
    root = ET.fromstring(feed)
    records: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", ARXIV_NS):
        title = normalize_space(as_text(entry.findtext("atom:title", default="", namespaces=ARXIV_NS)))
        published = as_text(entry.findtext("atom:published", default="", namespaces=ARXIV_NS))[:10] or None
        if not within_window(published, cutoff):
            continue
        url = as_text(entry.findtext("atom:id", default="", namespaces=ARXIV_NS))
        authors = [normalize_space(as_text(a.findtext("atom:name", default="", namespaces=ARXIV_NS))) for a in entry.findall("atom:author", ARXIV_NS)]
        summary = normalize_space(as_text(entry.findtext("atom:summary", default="", namespaces=ARXIV_NS)))
        categories = [cat.attrib.get("term", "") for cat in entry.findall("atom:category", ARXIV_NS)]
        records.append(
            make_record(
                provider="arxiv",
                query=query,
                title=title,
                url=url,
                source_type="paper",
                published_at=published,
                authors_or_org=", ".join(a for a in authors if a),
                summary=summary,
                tags=["arxiv", *categories[:5]],
                confidence="high",
                external_id=arxiv_external_id(url),
            )
        )
    return records


def collect_openalex(query: str, limit: int, cutoff: dt.date | None, timeout: int) -> list[dict[str, Any]]:
    params: dict[str, str | int] = {
        "search": query,
        "per-page": limit,
        "sort": "publication_date:desc",
    }
    if cutoff:
        params["filter"] = f"from_publication_date:{cutoff.isoformat()},to_publication_date:{today_date().isoformat()}"
    url = f"https://api.openalex.org/works?{urllib.parse.urlencode(params)}"
    payload = http_json(url, timeout)
    records: list[dict[str, Any]] = []
    for item in payload.get("results", []):
        if not isinstance(item, dict):
            continue
        title = normalize_space(as_text(item.get("title") or item.get("display_name")))
        if not title:
            continue
        published = as_text(item.get("publication_date") or "") or None
        if not within_window(published, cutoff):
            continue
        primary_location = item.get("primary_location") if isinstance(item.get("primary_location"), dict) else {}
        source_url = as_text(primary_location.get("landing_page_url") or item.get("doi") or item.get("id"))
        authorships = item.get("authorships") if isinstance(item.get("authorships"), list) else []
        authors = []
        for authorship in authorships[:10]:
            if not isinstance(authorship, dict):
                continue
            author = authorship.get("author") if isinstance(authorship.get("author"), dict) else {}
            name = as_text(author.get("display_name"))
            if name:
                authors.append(name)
        concepts = item.get("concepts") if isinstance(item.get("concepts"), list) else []
        tags = ["openalex"]
        for concept in concepts[:4]:
            if isinstance(concept, dict) and concept.get("display_name"):
                tags.append(as_text(concept.get("display_name")))
        records.append(
            make_record(
                provider="openalex",
                query=query,
                title=title,
                url=source_url,
                source_type="paper",
                published_at=published,
                authors_or_org=", ".join(authors),
                summary=as_text(item.get("type_crossref") or item.get("type") or "Academic work indexed by OpenAlex."),
                tags=tags,
                confidence="medium",
                external_id=as_text(item.get("doi") or item.get("id")),
            )
        )
    return records


def collect_github(query: str, limit: int, cutoff: dt.date | None, timeout: int) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode(
        {
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": min(limit, 100),
        }
    )
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    payload = http_json(f"https://api.github.com/search/repositories?{params}", timeout, headers=headers)
    records: list[dict[str, Any]] = []
    for item in payload.get("items", []):
        if not isinstance(item, dict):
            continue
        updated = as_text(item.get("updated_at"))[:10] or None
        if not within_window(updated, cutoff):
            continue
        full_name = as_text(item.get("full_name"))
        stars = item.get("stargazers_count")
        language = as_text(item.get("language"))
        tags = ["github"]
        if language:
            tags.append(language)
        if isinstance(stars, int):
            tags.append(f"stars:{stars}")
        records.append(
            make_record(
                provider="github",
                query=query,
                title=full_name or as_text(item.get("name")),
                url=as_text(item.get("html_url")),
                source_type="repo",
                published_at=updated,
                authors_or_org=as_text(item.get("owner", {}).get("login") if isinstance(item.get("owner"), dict) else ""),
                summary=as_text(item.get("description") or ""),
                tags=tags,
                confidence="high",
                external_id=full_name,
            )
        )
    return records


COLLECTORS = {
    "arxiv": collect_arxiv,
    "openalex": collect_openalex,
    "github": collect_github,
}


def deduplicate(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for record in records:
        key = dedup_key(record)
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


def parse_sources(value: str) -> list[str]:
    sources = [part.strip().lower() for part in value.split(",") if part.strip()]
    unknown = sorted(set(sources) - set(COLLECTORS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown source(s): {', '.join(unknown)}")
    return sources


def collect_all(args: argparse.Namespace) -> list[dict[str, Any]]:
    cutoff = today_date() - dt.timedelta(days=args.window_days) if args.window_days else None
    records: list[dict[str, Any]] = []
    for query in args.query:
        for source in args.sources:
            try:
                collector = COLLECTORS[source]
                records.extend(collector(query, args.limit_per_source, cutoff, args.timeout))
                if source == "arxiv":
                    time.sleep(args.polite_delay)
            except (urllib.error.URLError, TimeoutError, ET.ParseError, json.JSONDecodeError) as exc:
                print(f"WARN: {source} query failed for {query!r}: {exc}", file=sys.stderr)
    return deduplicate(records)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect source candidates from public no-key research APIs.")
    parser.add_argument("--topic", required=True, help="Human-readable topic; used for default query and output path")
    parser.add_argument("--query", action="append", help="Search query; repeatable. Defaults to --topic")
    parser.add_argument("--sources", type=parse_sources, default=list(DEFAULT_SOURCES), help="Comma-separated providers: arxiv,openalex,github")
    parser.add_argument("--window-days", type=int, default=30, help="Keep sources dated within this rolling window; 0 disables filtering")
    parser.add_argument("--limit-per-source", type=int, default=10, help="Maximum results per source per query")
    parser.add_argument("--output", type=Path, help="Output JSONL path; defaults to knowledge_base/<topic_slug>/collected_sources.jsonl")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds")
    parser.add_argument("--polite-delay", type=float, default=3.0, help="Delay after each arXiv request")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.limit_per_source < 1:
        parser.error("--limit-per-source must be >= 1")
    if args.window_days < 0:
        parser.error("--window-days must be >= 0")
    if not args.query:
        args.query = [args.topic]
    output = args.output or ROOT / "knowledge_base" / slugify(args.topic) / "collected_sources.jsonl"
    records = collect_all(args)
    write_jsonl(output, records)
    print(f"wrote {len(records)} source records to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
