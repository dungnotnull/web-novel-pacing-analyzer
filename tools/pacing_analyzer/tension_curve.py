"""tension_curve.py — page-turner tension curve mapping & scoring.

Builds a per-chapter tension curve (tension, hook strength, cliffhanger flag)
and scores curve shape: rising overall trend + sag detection in the middle
third. Grounded in the page-turner tension-curve framework.
"""
from __future__ import annotations

from typing import List, Tuple

from .schemas import Chapter, TensionPoint
from .text_stats import tension_score, hook_strength, cliffhanger_present


def build_curve(chapters: List[Chapter]) -> List[TensionPoint]:
    pts = []
    for ch in chapters:
        pts.append(TensionPoint(
            chapter_index=ch.index,
            tension=round(tension_score(ch.text), 3),
            hook_strength=round(hook_strength(ch.text), 3),
            cliffhanger=cliffhanger_present(ch.text),
            label=ch.title or "ch %d" % ch.index,
        ))
    return pts


def _sag_detection(pts: List[TensionPoint]) -> Tuple[bool, float]:
    n = len(pts)
    if n < 5:
        return False, 0.0
    third = max(1, n // 3)
    mid_start = third
    mid_end = 2 * third
    mid = pts[mid_start:mid_end]
    if not mid:
        return False, 0.0
    mid_avg = sum(p.tension for p in mid) / len(mid)
    head_avg = sum(p.tension for p in pts[:mid_start]) / max(1, mid_start)
    tail_avg = sum(p.tension for p in pts[mid_end:]) / max(1, n - mid_end)
    dip = min(head_avg, tail_avg) - mid_avg
    sag = mid_avg < 0.5 and dip > 0.12
    return sag, mid_avg


def tension_curve_score(chapters: List[Chapter]) -> Tuple[float, List[str], List[TensionPoint]]:
    pts = build_curve(chapters)
    findings: List[str] = []
    if not pts:
        return 0.0, ["No chapters supplied for tension curve."], pts

    tensions = [p.tension for p in pts]
    mean_t = sum(tensions) / len(tensions)
    # rising trend: linear regression slope over normalized index
    n = len(pts)
    xs = list(range(n))
    x_mean = sum(xs) / n
    num = sum((x - x_mean) * (y - mean_t) for x, y in zip(xs, tensions))
    den = sum((x - x_mean) ** 2 for x in xs)
    slope = num / den if den else 0.0
    slope_pts = max(0.0, min(100.0, 50.0 + slope * 400.0))

    # overall tension level: serialized fiction wants sustained engagement.
    level_pts = mean_t * 100.0

    # sag detection penalty
    sag, mid_avg = _sag_detection(pts)
    sag_pts = 100.0
    if sag:
        sag_pts = max(0.0, 100.0 - (0.5 - mid_avg) * 200.0)
        sag_chs = pts[n // 3: 2 * n // 3]
        findings.append(
            "Sagging mid-arc detected (chapters {a}-{b}, mean tension {m:.2f}); "
            "inject a midpoint reversal or raise stakes.".format(
                a=sag_chs[0].chapter_index, b=sag_chs[-1].chapter_index, m=mid_avg)
        )
    else:
        findings.append("No significant mid-arc sag detected.")

    if slope <= 0:
        findings.append("Tension curve is flat or declining overall; trend slope {:.3f}/chapter.".format(slope))
    else:
        findings.append("Tension curve trends upward (slope {:.3f}/chapter).".format(slope))

    if mean_t < 0.35:
        findings.append("Overall mean tension {:.2f} is low for serialized retention.".format(mean_t))

    score = round(0.4 * level_pts + 0.3 * slope_pts + 0.3 * sag_pts, 1)
    return score, findings, pts
