"""
AuraMatrix AI - Visual identity

Idea: the Hegelian dialectic lives in three colors. Thesis = aubergine-blue, antithesis = rose, synthesis = gilt.
The logo is a ring of these three colors; agent cards are tinted by role. The one bold element is the "aura" ring
around the score. Everything else stays calm.
"""

import html

from core.i18n import t

TOKENS = {
    "bg": "#15132A", "surface": "#1E1B38", "line": "#3A3566", "text": "#ECE9FA", "muted": "#A7A3C8",
    "thesis": "#7C9CFF", "anti": "#FF7FA7", "synth": "#F4C265",
    "risk_low": "#52D6A8", "risk_mid": "#D6E06A", "risk_high": "#F58A4B", "risk_vhigh": "#F0506E",
}

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=DM+Sans:wght@400;500;700&display=swap');
:root{--bg:#15132A;--surf:#1E1B38;--surf2:#272347;--line:#3A3566;--text:#ECE9FA;--muted:#A7A3C8;--thesis:#7C9CFF;--anti:#FF7FA7;--synth:#F4C265}
@property --fill{syntax:'<number>';inherits:false;initial-value:0}
html,body,.stApp,[data-testid="stAppViewContainer"]{font-family:'DM Sans',system-ui,-apple-system,'Segoe UI',sans-serif}
h1,h2,h3,[data-testid="stHeading"] *{font-family:'Bricolage Grotesque','DM Sans',system-ui,sans-serif!important;letter-spacing:-.015em}
h3,[data-testid="stHeading"] h3{font-weight:700}
[data-testid="stSidebar"]{background:var(--surf);border-right:1px solid var(--line)}
[data-testid="stSidebar"] h2{font-size:1.15rem}
[data-testid="stHeader"]{background:transparent}
.stButton>button,[data-testid="stBaseButton-secondary"],[data-testid="stFormSubmitButton"] button{background:var(--synth);color:#1B1630;border:0;border-radius:10px;font-weight:700;padding:.5rem 1.1rem}
.stButton>button:hover,[data-testid="stBaseButton-secondary"]:hover,[data-testid="stFormSubmitButton"] button:hover{filter:brightness(1.08);color:#1B1630}
.stButton>button:focus-visible,[data-testid="stBaseButton-secondary"]:focus-visible{outline:2px solid var(--text);outline-offset:2px}
[data-testid="stExpander"]{border:1px solid var(--line);border-radius:12px;background:var(--surf)}
[data-testid="stExpander"] summary{font-weight:500}
[data-testid="stTable"] table{border-collapse:collapse;font-variant-numeric:tabular-nums}
[data-testid="stTable"] th{color:var(--muted);font-weight:500;border-bottom:1px solid var(--line)!important}
[data-testid="stTable"] td{border-bottom:1px solid rgba(58,53,102,.55)!important}
[data-testid="stMetricValue"]{font-family:'Bricolage Grotesque',sans-serif;font-variant-numeric:tabular-nums}
[data-testid="stCaptionContainer"]{color:var(--muted)}
.am-brand{display:flex;align-items:center;gap:16px;margin:2px 0 4px}
.am-logo{width:56px;height:56px;flex:none}
.am-mark{width:46px;height:46px;border-radius:50%;flex:none;display:grid;place-items:center;background:conic-gradient(from 200deg,var(--thesis),var(--anti),var(--synth),var(--thesis))}
.am-mark::after{content:"";width:27px;height:27px;border-radius:50%;background:var(--bg)}
.am-name{font:700 2.1rem/1.05 'Bricolage Grotesque','DM Sans',sans-serif;letter-spacing:-.025em}
.am-tag{color:var(--muted);max-width:64ch;margin:4px 0 20px;line-height:1.5}
.am-hero{display:flex;gap:30px;align-items:center;padding:24px 28px;border:1px solid var(--line);border-radius:18px;background:var(--surf);margin:6px 0 18px}
.am-halo{--fill:var(--p);width:156px;height:156px;border-radius:50%;flex:none;display:grid;place-items:center;background:conic-gradient(var(--c) calc(var(--fill)*1%),rgba(255,255,255,.08) 0);box-shadow:0 0 46px var(--glow);animation:amfill 1.3s cubic-bezier(.2,.7,.2,1) both}
@keyframes amfill{from{--fill:0}}
.am-halo-in{width:120px;height:120px;border-radius:50%;background:var(--surf);display:flex;flex-direction:column;align-items:center;justify-content:center}
.am-score{font:700 2.7rem/1 'Bricolage Grotesque','DM Sans',sans-serif;font-variant-numeric:tabular-nums;letter-spacing:-.03em}
.am-of{color:var(--muted);font-size:.8rem;margin-top:2px}
.am-cat{font:700 1.9rem/1.1 'Bricolage Grotesque','DM Sans',sans-serif;letter-spacing:-.02em}
.am-meta{color:var(--muted);margin-top:6px}
.am-note{margin-top:10px;max-width:60ch;color:var(--text);line-height:1.5;font-size:.95rem}
.am-fomo{margin-top:16px;display:flex;align-items:center;gap:12px;color:var(--muted);font-size:.92rem}
.am-bar{flex:0 0 150px;height:6px;border-radius:4px;background:rgba(255,255,255,.09);overflow:hidden}
.am-bar>i{display:block;height:100%;background:var(--c)}
.am-card{border:1px solid var(--line);border-left:4px solid var(--role);border-radius:12px;background:var(--surf);padding:16px 20px;margin:12px 0}
.am-role{font:700 1rem/1.2 'Bricolage Grotesque','DM Sans',sans-serif;color:var(--role);margin-bottom:8px}
.am-body{white-space:pre-wrap;line-height:1.6;max-width:80ch}
.am-synth .am-body{font-size:1.04rem;line-height:1.65}
.am-assess{margin-top:14px;padding-top:12px;border-top:1px solid var(--line);color:var(--text);line-height:1.55;max-width:80ch}
.am-assess b{color:var(--synth)}
@media (max-width:700px){.am-hero{flex-direction:column;align-items:flex-start}.am-name{font-size:1.7rem}}
@media (prefers-reduced-motion:reduce){.am-halo{animation:none}}
</style>"""


def _safe(text) -> str:
    """Embed LLM text into HTML safely: escape it and keep '$' from being parsed as LaTeX."""
    return html.escape(str(text)).replace("$", "&#36;")


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def risk_color(category: str) -> str:
    """category is a language-neutral code: LOW / MEDIUM / HIGH / VERY_HIGH / UNKNOWN."""
    return {"VERY_HIGH": TOKENS["risk_vhigh"], "HIGH": TOKENS["risk_high"],
            "MEDIUM": TOKENS["risk_mid"], "LOW": TOKENS["risk_low"]}.get(category, TOKENS["muted"])


def _mark_html(lang: str = "en") -> str:
    """Animated SVG logo mark (assets/auramatrix_mark.svg); falls back to a CSS ring if the file is missing."""
    try:
        import base64, pathlib
        svg = (pathlib.Path(__file__).resolve().parent.parent / "assets" / "auramatrix_mark.svg").read_bytes()
        b64 = base64.b64encode(svg).decode("ascii")
        return f'<img class="am-logo" alt="{html.escape(t(lang, "logo.alt"))}" src="data:image/svg+xml;base64,{b64}">'
    except Exception:
        return '<div class="am-mark"></div>'


def brand_html(lang: str = "en") -> str:
    return ('<div class="am-brand">' + _mark_html(lang) + '<div class="am-name">AuraMatrix AI</div></div>'
            f'<div class="am-tag">{_safe(t(lang, "brand.tag"))}</div>')


def hero_html(ticker, score, category, coverage, fomo, provisional=False, lang: str = "en") -> str:
    color = TOKENS["muted"] if provisional else risk_color(category)
    note = ""
    if provisional:
        note = f'<div class="am-note">{_safe(t(lang, "hero.provisional"))}</div>'
    return (f'<div class="am-hero"><div class="am-halo" style="--p:{score:g};--c:{color};--glow:{_rgba(color, .30)}">'
            f'<div class="am-halo-in"><span class="am-score">{score:g}</span><span class="am-of">/ 100</span></div></div>'
            f'<div><div class="am-cat" style="color:{color}">{_safe(t(lang, "cat." + category))}</div>'
            f'<div class="am-meta">{_safe(ticker)}, {_safe(coverage)}</div>{note}'
            f'<div class="am-fomo" style="--c:{TOKENS["thesis"]}"><span>{_safe(t(lang, "hero.fomo", v=format(fomo, "g")))}</span>'
            f'<span class="am-bar"><i style="width:{min(max(fomo, 0), 100):g}%"></i></span></div></div></div>')


def role_card(label: str, role: str, text: str) -> str:
    color = {"thesis": TOKENS["thesis"], "anti": TOKENS["anti"], "synth": TOKENS["synth"]}[role]
    return (f'<div class="am-card" style="--role:{color}"><div class="am-role">{_safe(label)}</div>'
            f'<div class="am-body">{_safe(text)}</div></div>')


def synthesis_card(text: str, assessment: str, lang: str = "en") -> str:
    return (f'<div class="am-card am-synth" style="--role:{TOKENS["synth"]}"><div class="am-role">{_safe(t(lang, "card.synthesis"))}</div>'
            f'<div class="am-body">{_safe(text)}</div>'
            f'<div class="am-assess"><b>{_safe(t(lang, "card.assessment"))}</b><br>{_safe(assessment)}</div></div>')
