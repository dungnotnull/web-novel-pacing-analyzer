"""cli.py — command-line interface for the pacing analyzer.

Usage:
    python -m pacing_analyzer analyze chapters.json [--genre litrpg] [--format web_serial]
    python -m pacing_analyzer analyze --stdin < chapters.json

The chapters.json schema matches AnalysisRequest.to_dict(). Outputs the
scored report as JSON on stdout.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .harness import run
from .schemas import AnalysisRequest


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pacing_analyzer",
        description="Web-novel structure & chapter pacing analyzer (named-framework scoring).",
    )
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("analyze", help="Analyze a manuscript supplied as JSON.")
    a.add_argument("input", nargs="?", help="Path to an AnalysisRequest JSON file.")
    a.add_argument("--stdin", action="store_true", help="Read JSON from stdin.")
    a.add_argument("--genre", help="Override genre (e.g. litrpg, romance).")
    a.add_argument("--format", dest="fmt", default=None, help="Override length format.")
    a.add_argument("--out", help="Write JSON report to this path instead of stdout.")
    a.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")

    sub.add_parser("frameworks", help="List governing frameworks.")
    return p


def _load_request(args) -> AnalysisRequest:
    if args.stdin:
        raw = sys.stdin.buffer.read().decode("utf-8-sig")
    elif args.input:
        with open(args.input, encoding="utf-8-sig") as f:
            raw = f.read()
    else:
        raise SystemExit("Provide an input file path or use --stdin.")
    data = json.loads(raw)
    if args.genre:
        data["genre"] = args.genre
    if args.fmt:
        data["length_format"] = args.fmt
    return AnalysisRequest.from_dict(data)


def _emit(report, args) -> int:
    text = report.to_json(indent=2 if args.pretty else None)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print("Report written to %s (headline=%s, gates_passed=%s)" % (
            args.out, report.headline_score, report.gate_results.get("all_passed")))
    else:
        print(text)
    ok = bool(report.gate_results.get("all_passed"))
    return 0 if ok else 1


def _ensure_utf8_stdio() -> None:
    """Force UTF-8 on stdout/stderr so non-ASCII framework names never crash on
    legacy Windows console encodings (cp1252/cp1258)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def main(argv: Optional[List[str]] = None) -> int:
    _ensure_utf8_stdio()
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "frameworks":
        from .schemas import FRAMEWORKS
        for fid, name in FRAMEWORKS.items():
            print("%-18s %s" % (fid, name))
        return 0
    if args.command == "analyze":
        request = _load_request(args)
        report = run(request)
        return _emit(report, args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())


