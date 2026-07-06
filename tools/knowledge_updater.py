#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""knowledge_updater.py — self-improving knowledge pipeline.

Crawl ArXiv (cs.CL) and (optionally) crawl4ai-fetched authoritative domain
pages, score by recency + domain-keyword relevance, deduplicate by URL/DOI
hash, and append date-stamped entries to SECOND-KNOWLEDGE-BRAIN.md in the
correct sections (Key Research Papers table + Knowledge Update Log).

Production-safe: graceful degradation when offline or when crawl4ai is not
installed — it logs and no-ops rather than corrupting the brain.

Usage:
    python tools/knowledge_updater.py                 # run crawl + append
    python tools/knowledge_updater.py --dry-run       # print, do not write
    python tools/knowledge_updater.py --since 2025-01-01 --max 30
    python tools/knowledge_updater.py --brain /path/SECOND-KNOWLEDGE-BRAIN.md

Recommended schedule: weekly cron.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import logging
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Iterable, List, Optional, Set

LOG = logging.getLogger("knowledge_updater")

DEFAULT_BRAIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                             "SECOND-KNOWLEDGE-BRAIN.md")

ARXIV_CATEGORIES = ["cs.CL"]
SEARCH_QUERIES = [
    "narrative pacing reader retention serialized fiction",
    "story structure beat sheet analysis",
    "web novel trope trends",
    "cliffhanger curiosity gap engagement",
]
DOMAINS = ["storygrid.com"]
KEYWORDS = sorted({w.lower() for q in SEARCH_QUERIES for w in q.split() if len(w) > 3})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", "ignore")).hexdigest()[:12]


def _existing_hashes(text: str) -> Set[str]:
    return set(re.findall(r"<!--h:([0-9a-f]{12})-->", text))


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

def fetch_arxiv(category: str, max_results: int = 15,
                 since: Optional[datetime.date] = None) -> List[Dict[str, str]]:
    """Query the ArXiv Atom API for a category; return normalized entries."""
    base = "http://export.arxiv.org/api/query"
    url = base + "?" + urllib.parse.urlencode({
        "search_query": "cat:" + category,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": str(max_results),
    })
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = r.read().decode("utf-8", "ignore")
    except Exception as e:  # graceful degradation
        LOG.warning("arxiv fetch failed for %s: %s", category, e)
        return []

    entries: List[Dict[str, str]] = []
    for block in re.findall(r"<entry>(.*?)</entry>", data, re.S):
        def g(tag: str, b: str = block) -> str:
            m = re.search(r"<%s>(.*?)</%s>" % (tag, tag), b, re.S)
            return _clean(m.group(1)) if m else ""

        title = g("title")
        if not title:
            continue
        summary = g("summary")
        published = g("published")[:10]
        if since:
            try:
                if datetime.date.fromisoformat(published) < since:
                    continue
            except ValueError:
                pass
        m = re.search(r"<id>(.*?)</id>", block, re.S)
        link = _clean(m.group(1)) if m else ""
        authors = ", ".join(_clean(a) for a in re.findall(r"<name>(.*?)</name>", block, re.S))
        entries.append({
            "title": title, "authors": authors, "date": published,
            "url": link, "abstract": summary, "venue": "ArXiv",
        })
    return entries


def crawl4ai_domains(domains: Iterable[str]) -> List[Dict[str, str]]:
    """Optional crawl4ai pull of authoritative domain landing pages.

    No-op (graceful degradation) if crawl4ai is not installed or network fails.
    """
    try:
        from crawl4ai import WebCrawler  # type: ignore
    except Exception:
        LOG.info("crawl4ai not installed; skipping domain crawl (graceful degradation).")
        return []
    out: List[Dict[str, str]] = []
    try:
        crawler = WebCrawler()
        crawler.warmup()
    except Exception as e:
        LOG.warning("crawl4ai warmup failed: %s", e)
        return []
    for d in domains:
        try:
            res = crawler.run(url="https://" + d)
            md = getattr(res, "markdown", "") or ""
            out.append({
                "title": "Domain scan: " + d, "authors": "",
                "date": str(datetime.date.today()),
                "url": "https://" + d, "abstract": md[:400],
                "venue": "Web",
            })
        except Exception as e:
            LOG.warning("crawl4ai failed for %s: %s", d, e)
    return out


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def relevance(entry: Dict[str, str]) -> float:
    """Score = keyword-match density + recency weight (2-year decay)."""
    text = (entry["title"] + " " + entry["abstract"]).lower()
    kw = sum(1 for k in KEYWORDS if k in text)
    try:
        d = datetime.date.fromisoformat(entry["date"])
        age = (datetime.date.today() - d).days
        rec = max(0.0, 1.0 - age / 730.0)
    except Exception:
        rec = 0.0
    return kw + 2.0 * rec


# ---------------------------------------------------------------------------
# Brain mutation
# ---------------------------------------------------------------------------

def _insert_table_rows(text: str, rows: List[str]) -> str:
    """Insert new rows after the last existing row of the Key Research Papers table."""
    lines = text.splitlines()
    # locate the table section
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().lower().startswith("## key research papers"):
            start = i
            break
    if start is None:
        # append a new section
        return text.rstrip() + "\n\n## Key Research Papers\n\n| Title | Authors | Year | Venue | DOI/Link | Relevance |\n|-------|---------|------|-------|----------|-----------|\n" + "\n".join(rows) + "\n"
    # find table header + separator then existing rows
    i = start + 1
    while i < len(lines) and not lines[i].strip().startswith("|"):
        i += 1
    # header
    header_i = i
    sep_i = i + 1
    # last pipe-row index
    last_row = sep_i
    j = sep_i + 1
    while j < len(lines) and lines[j].lstrip().startswith("|"):
        last_row = j
        j += 1
    new_lines = lines[:last_row + 1] + rows + lines[last_row + 1:]
    return "\n".join(new_lines) + ("\n" if text.endswith("\n") else "")


def _append_log(text: str, lines: List[str]) -> str:
    m = re.search(r"^## Knowledge Update Log\s*$", text, re.M)
    if m is None:
        return text.rstrip() + "\n\n## Knowledge Update Log\n" + "\n".join(lines) + "\n"
    insert_at = m.end()
    # find end of section (next '## ' or EOF)
    after = text[insert_at:]
    nxt = re.search(r"\n## ", after)
    section_end = insert_at + (nxt.start() if nxt else len(after))
    section = text[insert_at:section_end].rstrip()
    new_section = section + ("\n" if section else "\n") + "\n".join(lines) + "\n"
    return text[:insert_at] + new_section + text[section_end:]


def append_entries(entries: List[Dict[str, str]], brain_path: str,
                    dry_run: bool = False) -> int:
    with open(brain_path, encoding="utf-8") as f:
        text = f.read()
    existing = _existing_hashes(text)
    today = datetime.date.today().isoformat()
    new_rows: List[str] = []
    log_lines: List[str] = []
    for e in sorted(entries, key=relevance, reverse=True):
        key = _hash(e["url"] or e["title"])
        if key in existing:
            continue
        existing.add(key)
        row = "| {t} | {a} | {y} | {v} | {u} | score={s:.2f} <!--h:{h}--> |".format(
            t=e["title"][:90].replace("|", "/"),
            a=(e["authors"][:40] or "-"),
            y=(e["date"][:4] or "-"),
            v=e.get("venue", "ArXiv/Web"),
            u=e["url"] or "-",
            s=relevance(e), h=key,
        )
        new_rows.append(row)
        log_lines.append("- %s — added: %s" % (today, e["title"][:90]))

    if not new_rows:
        LOG.info("no new entries to append.")
        return 0

    if dry_run:
        for r in new_rows:
            print(r)
        for l in log_lines:
            print(l)
        return len(new_rows)

    text = _insert_table_rows(text, new_rows)
    text = _append_log(text, log_lines)
    with open(brain_path, "w", encoding="utf-8") as f:
        f.write(text)
    LOG.info("appended %d new entries to %s", len(new_rows), brain_path)
    return len(new_rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Refresh SECOND-KNOWLEDGE-BRAIN.md")
    p.add_argument("--brain", default=DEFAULT_BRAIN, help="Path to SECOND-KNOWLEDGE-BRAIN.md")
    p.add_argument("--max", type=int, default=15, help="Max ArXiv results per category")
    p.add_argument("--since", default=None, help="Only entries on/after YYYY-MM-DD")
    p.add_argument("--no-domains", action="store_true", help="Skip crawl4ai domain crawl")
    p.add_argument("--dry-run", action="store_true", help="Print entries; do not write")
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="[%(levelname)s] %(message)s")
    since = None
    if args.since:
        try:
            since = datetime.date.fromisoformat(args.since)
        except ValueError:
            LOG.error("invalid --since date: %s", args.since)
            return 2

    entries: List[Dict[str, str]] = []
    for cat in ARXIV_CATEGORIES:
        entries += fetch_arxiv(cat, max_results=args.max, since=since)
    if not args.no_domains:
        entries += crawl4ai_domains(DOMAINS)

    if not entries:
        LOG.info("nothing fetched (offline?). Brain left unchanged.")
        return 0

    if not os.path.exists(args.brain):
        LOG.error("brain file not found: %s", args.brain)
        return 2

    n = append_entries(entries, args.brain, dry_run=args.dry_run)
    print("[ok] %d new entries %s." % (n, "(dry-run)" if args.dry_run else "appended"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
