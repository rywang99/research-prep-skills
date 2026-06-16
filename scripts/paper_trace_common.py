#!/usr/bin/env python3
"""Shared helpers for HTML-first paper trace workflows."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ARXIV_RE = re.compile(r"(?:arxiv:)?(\d{4}\.\d{4,5})(?:v\d+)?", re.I)
ROOT = Path(__file__).resolve().parents[1]


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def today() -> str:
    return dt.date.today().isoformat()


def text(value: Any, default: str = "") -> str:
    return default if value is None else str(value)


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    if slug:
        return slug[:80]
    return "paper-" + hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]


def compact_slug(value: str, prefix: str = "item") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    if slug:
        return slug[:80]
    return f"{prefix}-" + hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]


TOPIC_SLUG_ALIASES = [
    (["空间音频大模型", "spatial audio llm", "spatial-audio-llm"], "spatial-audio-llm"),
    (["空间音频理解", "spatial audio understanding"], "spatial-audio-understanding"),
    (["说话人日志", "speaker diarization", "diarization"], "speaker-diarization"),
    (["多说话人语音识别", "multi-speaker speech recognition", "multi-talker speech recognition"], "multi-speaker-speech-recognition"),
    (["自动化调研", "auto research", "auto-research"], "auto-research-agent"),
]


def known_topic_slug(value: str) -> str | None:
    low = clean_space(value).lower()
    for aliases, slug in TOPIC_SLUG_ALIASES:
        if any(alias.lower() in low for alias in aliases):
            return slug
    return None


def infer_method_short_name(source: dict[str, Any]) -> str:
    title = clean_space(text(source.get("title"), "Paper"))
    if not title:
        return "Paper"
    prefix = re.split(r"\s*[:：]\s*", title, maxsplit=1)[0].strip()
    if 2 <= len(prefix) <= 60 and len(prefix.split()) <= 8:
        return prefix
    markers = [
        " using ",
        " via ",
        " with ",
        " for ",
        " from ",
        " by ",
        " in ",
        " on ",
        " towards ",
        " toward ",
    ]
    split_points = [title.lower().find(marker) for marker in markers]
    split_points = [idx for idx in split_points if idx > 8]
    if split_points:
        candidate = title[: min(split_points)].strip(" -:：")
        if 2 <= len(candidate) <= 80:
            return candidate
    words = re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", title)
    if words:
        return " ".join(words[: min(5, len(words))])
    return title[:60].strip() or "Paper"


def infer_method_slug(source: dict[str, Any]) -> str:
    return compact_slug(infer_method_short_name(source), prefix="method")


def infer_paper_category(source: dict[str, Any], topic: str = "") -> dict[str, str]:
    topic = clean_space(topic)
    if topic:
        return {
            "label": topic,
            "slug": known_topic_slug(topic) or compact_slug(topic, prefix="topic"),
        }

    haystack = " ".join(
        [
            text(source.get("title")),
            text(source.get("summary")),
            " ".join(text(tag) for tag in as_list(source.get("tags"))),
        ]
    ).lower()
    rules = [
        ("空间音频大模型", "spatial-audio-llm", ["spatial audio", "foa", "ambisonic", "ambisonics", "omni llm", "lalms", "so-encoder", "sound localization"]),
        ("说话人日志", "speaker-diarization", ["speaker diarization", "diarization", "eend", "speaker-wise speech"]),
        ("多说话人语音识别", "multi-speaker-speech-recognition", ["multi-talker", "multi-speaker", "speech recognition", "asr", "whisper"]),
        ("自动化调研 Agent", "auto-research-agent", ["research agent", "automated research", "auto-research"]),
    ]
    for label, slug, keywords in rules:
        if any(keyword in haystack for keyword in keywords):
            return {"label": label, "slug": slug}

    tags = [text(tag) for tag in as_list(source.get("tags"))]
    arxiv_tags = [tag for tag in tags if re.match(r"^[a-z-]+(\.[A-Z]{2})?$", tag)]
    if arxiv_tags:
        label = f"arXiv {arxiv_tags[0]}"
        return {"label": label, "slug": compact_slug(label, prefix="arxiv")}
    return {"label": "paper-trace", "slug": "paper-trace"}


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}-{hashlib.sha1(value.encode('utf-8')).hexdigest()[:12]}"


def normalize_arxiv_id(value: str) -> str | None:
    match = ARXIV_RE.search(value)
    return match.group(1) if match else None


def arxiv_abs_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/abs/{arxiv_id}"


def arxiv_pdf_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/pdf/{arxiv_id}"


def fetch_arxiv_source(arxiv_id: str, timeout: int = 30) -> dict[str, Any]:
    url = "https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(arxiv_id)
    req = urllib.request.Request(url, headers={"User-Agent": "auto-research-paper-trace/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        root = ET.fromstring(resp.read())
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entry = root.find("a:entry", ns)
    if entry is None:
        raise ValueError(f"arXiv metadata not found for {arxiv_id}")
    title = " ".join(text(entry.findtext("a:title", namespaces=ns)).split())
    summary = " ".join(text(entry.findtext("a:summary", namespaces=ns)).split())
    published = text(entry.findtext("a:published", namespaces=ns))[:10] or "date_unknown"
    authors = []
    for author in entry.findall("a:author", ns):
        name = author.findtext("a:name", namespaces=ns)
        if name:
            authors.append(name)
    categories = [cat.attrib.get("term", "") for cat in entry.findall("a:category", ns) if cat.attrib.get("term")]
    return {
        "id": "src-arxiv-" + arxiv_id.replace(".", "-"),
        "title": title or f"arXiv:{arxiv_id}",
        "url": arxiv_abs_url(arxiv_id),
        "pdf_url": arxiv_pdf_url(arxiv_id),
        "source_type": "paper",
        "published_at": published,
        "accessed_at": today(),
        "authors_or_org": ", ".join(authors),
        "summary": summary,
        "tags": ["arxiv", *categories[:5]],
        "confidence": "high",
        "provider": "arxiv",
        "query": arxiv_id,
        "external_id": arxiv_id,
        "collected_at": now_iso(),
    }


def source_from_paper_input(paper: str, timeout: int = 30) -> dict[str, Any]:
    value = paper.strip()
    arxiv_id = normalize_arxiv_id(value)
    if arxiv_id:
        return fetch_arxiv_source(arxiv_id, timeout=timeout)
    path = Path(value).expanduser()
    if path.exists():
        title = path.stem.replace("_", " ").replace("-", " ")
        return {
            "id": stable_id("src-local-paper", str(path.resolve())),
            "title": title,
            "url": str(path),
            "pdf_url": str(path),
            "source_type": "paper",
            "published_at": "date_unknown",
            "accessed_at": today(),
            "authors_or_org": "local file",
            "summary": "Local PDF supplied for paper trace.",
            "tags": ["local-pdf"],
            "confidence": "medium",
            "provider": "local",
            "query": value,
            "external_id": str(path),
            "collected_at": now_iso(),
        }
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.path.lower().endswith(".pdf"):
        title = Path(parsed.path).stem.replace("_", " ").replace("-", " ") or value
        return {
            "id": stable_id("src-pdf", value),
            "title": title,
            "url": value,
            "pdf_url": value,
            "source_type": "paper",
            "published_at": "date_unknown",
            "accessed_at": today(),
            "authors_or_org": "unknown",
            "summary": "Direct PDF URL supplied for paper trace.",
            "tags": ["pdf"],
            "confidence": "medium",
            "provider": "pdf",
            "query": value,
            "external_id": value,
            "collected_at": now_iso(),
        }
    return {
        "id": stable_id("src-title-paper", value),
        "title": value,
        "url": "",
        "source_type": "paper",
        "published_at": "date_unknown",
        "accessed_at": today(),
        "authors_or_org": "unknown",
        "summary": "Paper title supplied without a resolvable official PDF/metadata URL.",
        "tags": ["title-only"],
        "confidence": "low",
        "provider": "manual",
        "query": value,
        "external_id": value,
        "collected_at": now_iso(),
    }


def download_pdf_to_temp(pdf_url: str, tmpdir: Path, timeout: int = 45) -> Path | None:
    if not pdf_url:
        return None
    path = Path(pdf_url).expanduser()
    target = tmpdir / "paper.pdf"
    if path.exists():
        shutil.copyfile(path, target)
        return target
    parsed = urllib.parse.urlparse(pdf_url)
    if parsed.scheme not in {"http", "https"}:
        return None
    req = urllib.request.Request(pdf_url, headers={"User-Agent": "auto-research-paper-trace/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            target.write_bytes(resp.read())
    except Exception:
        return None
    return target if target.exists() and target.stat().st_size > 0 else None


def extract_pdf_text(pdf: Path, max_chars: int = 50000) -> str:
    if not shutil.which("pdftotext"):
        return ""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), "-"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=60,
        )
    except Exception:
        return ""
    return clean_space(result.stdout)[:max_chars]


def clean_space(value: str) -> str:
    return " ".join(value.split())


def extract_available_text(source: dict[str, Any], timeout: int = 45) -> tuple[str, str]:
    pdf_url = text(source.get("pdf_url"))
    with tempfile.TemporaryDirectory(prefix="paper-trace-") as tmp:
        pdf = download_pdf_to_temp(pdf_url, Path(tmp), timeout=timeout) if pdf_url else None
        if pdf:
            extracted = extract_pdf_text(pdf)
            if extracted:
                return extracted, "pdf_temp_pdftotext"
    fallback = clean_space(text(source.get("summary")))
    return fallback, "metadata_summary"


def sentence_candidates(value: str) -> list[str]:
    cleaned = clean_space(value)
    pieces = re.split(r"(?<=[.!?。！？])\s+", cleaned)
    result: list[str] = []
    for piece in pieces:
        piece = piece.strip()
        words = piece.split()
        if 8 <= len(words) <= 80 and not re.match(r"^(references|acknowledg|appendix)\b", piece, re.I):
            result.append(piece)
    return result


def pick_by_keywords(sentences: list[str], keywords: list[str], limit: int = 3) -> list[str]:
    found = []
    seen = set()
    for sentence in sentences:
        low = sentence.lower()
        if any(k in low for k in keywords):
            key = re.sub(r"\W+", "", low)[:100]
            if key not in seen:
                seen.add(key)
                found.append(sentence)
        if len(found) >= limit:
            break
    return found


def contains_cjk(value: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", value))


def chinese_summary(source: dict[str, Any], topic: str = "") -> str:
    summary = clean_space(text(source.get("summary")))
    if summary and contains_cjk(summary) and not re.search(r"[A-Za-z]", summary):
        return summary[:260]
    context = f"围绕“{topic}”" if topic else "围绕当前研究主题"
    return f"该论文是{context}纳入溯源的一篇文献；自动溯源基于来源元数据和临时全文抽取信号生成，并只保留中文归纳，不直接展示英文原文片段。"


def signal_count(sentences: list[str], keywords: list[str]) -> int:
    return len(pick_by_keywords(sentences, keywords, limit=8))


def make_reading_points(sentences: list[str], limit: int = 8) -> list[dict[str, str]]:
    groups = [
        ("研究动机", ["challenge", "problem", "however", "difficult", "gap", "motivation", "need"], "优先阅读引言和问题定义，确认论文试图解决的具体缺口、应用场景和约束条件。"),
        ("方法设计", ["we propose", "framework", "model", "architecture", "training", "algorithm", "method"], "优先阅读方法章节，整理模型结构、训练目标、输入输出格式和推理流程。"),
        ("前作关系", ["previous", "prior", "基线", "compared", "related", "existing"], "优先阅读相关工作和 基线 描述，确认它继承了哪些模型族、数据集或评测协议。"),
        ("实验设置", ["experiment", "dataset", "benchmark", "result", "outperform", "evaluation", "metric"], "优先阅读实验章节，核对数据集、指标、基线、消融和跨场景泛化。"),
        ("复现信息", ["code", "implementation", "hyperparameter", "available", "preprocess", "training data"], "优先检查代码、模型、数据许可、超参数、预处理和评测脚本是否足够复现。"),
        ("局限风险", ["limitation", "future work", "fail", "cannot", "risk", "constraint"], "优先阅读局限和未来工作，标记失败模式、适用边界和潜在部署风险。"),
    ]
    points: list[dict[str, str]] = []
    for category, keywords, statement in groups:
        count = signal_count(sentences, keywords)
        if count:
            points.append({
                "category": category,
                "statement": f"自动抽取文本中检测到与{category}相关的线索，建议按该主题精读。",
                "why_read": statement,
            })
        if len(points) >= limit:
            break
    if not points:
        points.append({
            "category": "总体扫读",
            "statement": "未稳定检测到结构化线索，建议按摘要、引言、方法、实验和局限的顺序快速扫读。",
            "why_read": "先建立任务设定和贡献边界，再决定是否进行深度复现。",
        })
    return points[:limit]


def infer_lineage(sentences: list[str], topic: str) -> list[str]:
    count = signal_count(sentences, ["previous", "prior", "existing", "基线", "related work", "compared"])
    if count:
        return ["从可抽取文本看，论文包含与前作、既有系统或 基线 对比相关的内容；应重点核对相关工作如何定义直接前作，以及实验中选择了哪些强基线。"]
    context = f"在{topic}方向中，" if topic else ""
    return [f"{context}建议把技术脉络核对重点放在任务定义、常用模型族、数据集协议和 基线 选择上；当前自动抽取未稳定识别出明确前作链条。"]


def infer_method_delta(sentences: list[str]) -> list[str]:
    count = signal_count(sentences, ["we propose", "framework", "architecture", "model", "training", "method", "algorithm"])
    if count:
        return ["自动抽取文本中检测到方法设计相关线索；建议重点确认论文相对前作改变的是模型结构、训练目标、特征组织、推理流程还是系统组合方式。"]
    return ["自动抽取未稳定定位清晰的方法增量；建议人工阅读方法章节，按“输入、模块、训练目标、输出、复杂度”拆解贡献。"]


def infer_experiment_protocol(sentences: list[str]) -> list[str]:
    count = signal_count(sentences, ["experiment", "dataset", "benchmark", "evaluation", "result", "metric", "ablation"])
    if count:
        return ["自动抽取文本中检测到实验和评测相关线索；建议核对数据集、划分、指标、基线、公平比较、消融实验和统计显著性。"]
    return ["自动抽取未稳定定位实验协议；建议人工核对数据来源、评测脚本、指标定义和跨论文可比性。"]


def infer_repro_risks(sentences: list[str]) -> list[str]:
    count = signal_count(sentences, ["code", "implementation", "hyperparameter", "available", "preprocess", "training data", "limitation", "future work"])
    if count:
        return ["自动抽取文本中检测到与实现、数据、代码可用性或局限相关的线索；复现前应检查开源状态、数据许可、训练成本、超参数和评测一致性。"]
    return ["复现风险需要重点关注代码/模型/数据是否公开、训练成本是否可承受、数据许可是否清晰，以及评测协议是否能独立复现。"]


def generate_trace(source: dict[str, Any], topic: str = "", timeout: int = 45) -> dict[str, Any]:
    available_text, extraction_status = extract_available_text(source, timeout=timeout)
    sentences = sentence_candidates(available_text)
    title = text(source.get("title"), "Paper")
    topic_text = f"“{topic}”" if topic else "该研究方向"
    return {
        "source_id": source.get("id"),
        "title": title,
        "display_title": "论文技术溯源",
        "url": source.get("url"),
        "published_at": source.get("published_at"),
        "authors_or_org": source.get("authors_or_org"),
        "trace_status": "ok" if available_text else "metadata_only",
        "extraction_status": extraction_status,
        "one_sentence_position": chinese_summary(source, topic),
        "core_problem": f"这篇论文需要围绕{topic_text}中的任务设定、输入输出、优化目标和评测指标来判断贡献边界；自动溯源不展示英文原文，只提供中文阅读路线。",
        "technical_lineage": infer_lineage(sentences, topic),
        "method_delta": infer_method_delta(sentences),
        "experiment_protocol": infer_experiment_protocol(sentences),
        "reproducibility_risks": infer_repro_risks(sentences),
        "reading_points": make_reading_points(sentences, limit=8),
        "follow_up_queries": [
            "检索该论文是否公开代码、模型权重和评测脚本。",
            "检索该论文使用的数据集、指标和 基线 是否有独立复现。",
            "检索后续引用和相关工作，确认该方法是否被进一步采用或修正。",
        ],
        "evidence_urls": [u for u in [source.get("url"), source.get("pdf_url")] if u],
        "generated_at": now_iso(),
    }


def parse_date(value: Any) -> dt.date | None:
    match = re.search(r"\d{4}-\d{2}-\d{2}", text(value))
    if not match:
        return None
    try:
        return dt.date.fromisoformat(match.group(0))
    except ValueError:
        return None


def in_window(date_value: dt.date | None, start: dt.date | None, end: dt.date | None) -> bool:
    if date_value is None:
        return False
    if start and date_value < start:
        return False
    if end and date_value > end:
        return False
    return True


def is_traceable_paper_source(source: dict[str, Any]) -> bool:
    stype = text(source.get("source_type"))
    url = text(source.get("url"))
    if stype == "paper":
        return bool(url or source.get("title"))
    if stype in {"benchmark", "dataset"} and re.search(r"arxiv\.org/(abs|pdf)/|\.pdf($|[?#])", url, re.I):
        return True
    return False


def source_to_trace_input(source: dict[str, Any]) -> dict[str, Any]:
    result = dict(source)
    url = text(result.get("url"))
    arxiv_id = normalize_arxiv_id(url)
    if arxiv_id and not result.get("pdf_url"):
        result["pdf_url"] = arxiv_pdf_url(arxiv_id)
    elif url.lower().endswith(".pdf") and not result.get("pdf_url"):
        result["pdf_url"] = url
    return result
