"""Data-driven risk radar (SVG). No AI needed; every axis is one component of the score table."""
import math
from html import escape

from core.i18n import t

BLUE, ROSE, GOLD = "#7C9CFF", "#FF7FA7", "#F4C265"


def _max_penalty(rule) -> float:
    return max(p for _, p in rule["tiers"])


def radar_svg(breakdown: list, rules: list, size: int = 520, lang: str = "en") -> str:
    n = len(breakdown)
    if n < 3:
        return ""
    cx = cy = size / 2
    R = size * 0.29
    maxes = {r["key"]: _max_penalty(r) for r in rules}

    def pt(i, frac):
        a = -math.pi / 2 + 2 * math.pi * i / n
        return cx + R * frac * math.cos(a), cy + R * frac * math.sin(a)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" role="img" '
           f'aria-label="{escape(t(lang, "radar.aria"))}" style="max-width:{size}px;width:100%">',
           f'<defs><linearGradient id="rg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BLUE}"/>'
           f'<stop offset=".55" stop-color="{ROSE}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient></defs>']
    for ring in (0.25, 0.5, 0.75, 1.0):                       # grid rings
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, ring) for i in range(n)))
        out.append(f'<polygon points="{pts}" fill="none" stroke="#3A3566" stroke-width="1"/>')
    for i in range(n):                                          # axes
        x, y = pt(i, 1.0)
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#3A3566" stroke-width="1"/>')

    poly, marks = [], []
    for i, row in enumerate(breakdown):
        missing = row["status"] == "missing"
        if missing:
            frac = 0.0
            x, y = pt(i, 0.0)
        else:
            mx = maxes.get(row["key"], 1) or 1
            frac = min(1.0, -row["penalty"] / mx) if row["penalty"] < 0 else 0.0
            x, y = pt(i, max(frac, 0.04))
        poly.append((x, y))
        if missing:
            xm, ym = pt(i, 0.30)
            tip = escape(t(lang, "radar.missing", name=row["component"]))
            marks.append(f'<circle cx="{xm:.1f}" cy="{ym:.1f}" r="7" fill="none" stroke="{GOLD}" stroke-width="1.5" '
                         f'stroke-dasharray="3 3"><title>{tip}</title></circle>')
        else:
            color = ROSE if frac >= 0.5 else (GOLD if frac > 0 else BLUE)
            tip = escape(t(lang, "radar.point", name=row["component"], value=row["value"], pen=row["penalty"]))
            marks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}"><title>{tip}</title></circle>')
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)
    out.append(f'<polygon points="{pts}" fill="url(#rg)" fill-opacity=".22" stroke="url(#rg)" stroke-width="2.5" stroke-linejoin="round"/>')
    out += marks
    for i, row in enumerate(breakdown):                         # labels
        x, y = pt(i, 1.2)
        anchor = "middle" if abs(x - cx) < 8 else ("start" if x > cx else "end")
        label = t(lang, f"rule.{row['key']}.short")
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="#A7A3C8" font-size="13" font-family="DM Sans,sans-serif" '
                   f'text-anchor="{anchor}" dominant-baseline="middle">{escape(label)}</text>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="2.5" fill="#A7A3C8"/></svg>')
    return "".join(out)
