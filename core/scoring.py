"""
AuraMatrix AI - Transparent Aura-Score system (single source of truth)

Aura-Score = 100 - (sum of penalty points), floor 0.
Every component's thresholds are in the RULES table below; the UI is drawn from this table.
WARNING: the thresholds are expert assumptions; they are not calibrated or backtested into a predictive model.

Rows and categories carry language-neutral codes (row["key"], row["status"], risk_category);
localized labels are produced only for display via core.i18n.
"""

from core.i18n import t

# direction="above": penalty if value > threshold (thresholds listed high to low)
# direction="below": penalty if value < threshold (thresholds listed low to high)
RULES = [
    {"key": "change_24h", "direction": "above", "tiers": [(20, 15), (10, 8)], "needs_history": False},
    {"key": "volatility", "direction": "above", "tiers": [(100, 20), (60, 10)], "needs_history": True},
    {"key": "drawdown", "direction": "above", "tiers": [(50, 20), (30, 10)], "needs_history": True},
    {"key": "sharpe", "direction": "below", "tiers": [(0, 10)], "needs_history": True},
    {"key": "var7", "direction": "above", "tiers": [(25, 15), (15, 8)], "needs_history": True},
    {"key": "kurtosis", "direction": "above", "tiers": [(5, 5)], "needs_history": True},
    {"key": "liquidity", "direction": "below", "tiers": [(1_000_000, 10), (10_000_000, 5)], "needs_history": False},
    {"key": "vesting", "direction": "above", "tiers": [(0.5, 15), (0.2, 8)], "needs_history": False},
    {"key": "supply", "direction": "above", "tiers": [(50, 10), (20, 5)], "needs_history": True},
]

# (lower bound, category code) - high to low
CATEGORIES = [
    (75, "LOW"),
    (50, "MEDIUM"),
    (25, "HIGH"),
    (0, "VERY_HIGH"),
]

UNCERTAINTY_PREMIUM = 5  # points deducted for every component that cannot be evaluated


def rule_name(rule: dict, lang: str = "en") -> str:
    return t(lang, f"rule.{rule['key']}.name")


def rule_metric(rule: dict, lang: str = "en") -> str:
    return t(lang, f"rule.{rule['key']}.metric")


def category_label(code: str, lang: str = "en") -> str:
    return t(lang, f"cat.{code}")


def _fmt(x):
    return f"{x:,.0f}" if abs(x) >= 1000 else f"{x:g}"


def rule_text(rule: dict) -> str:
    op = ">" if rule["direction"] == "above" else "<"
    return " ; ".join(f"{op} {_fmt(lim)} → −{pen}" for lim, pen in rule["tiers"])


def _value(key, asset, stats):
    if key == "change_24h":
        v = asset.get("24h_change_pct")
        return None if v is None else abs(v)
    if key == "liquidity":
        v = asset.get("daily_volume_usd")
        return v if v and v > 0 else None
    if key == "vesting":
        v, vol = asset.get("upcoming_vesting_cliff_usd"), asset.get("daily_volume_usd")
        return v / vol if v is not None and vol and vol > 0 else None
    if key == "supply":
        return asset.get("net_inflation_rate_annual")
    if stats is None:
        return None
    return {
        "volatility": stats["annual_volatility_pct"],
        "drawdown": abs(stats["max_drawdown_pct"]),
        "sharpe": stats["sharpe_ratio"],
        "var7": stats.get(f"mc_var95_{stats['horizon_days']}d_pct"),
        "kurtosis": stats["excess_kurtosis"],
    }.get(key)


def _penalty(rule, value):
    for lim, pen in rule["tiers"]:
        if (rule["direction"] == "above" and value > lim) or (rule["direction"] == "below" and value < lim):
            return pen
    return 0


def score_asset(asset: dict, stats, lang: str = "en") -> dict:
    """Row schema: key (rule code), component (localized name), value (display string),
    rule, penalty (<= 0), status ("missing" | "penalized" | "ok")."""
    breakdown, total, evaluated, missing_n = [], 0, 0, 0
    for rule in RULES:
        v = _value(rule["key"], asset, stats)
        name = rule_name(rule, lang)
        if v is None:
            breakdown.append({"key": rule["key"], "component": name, "value": t(lang, "score.no_data"),
                              "rule": rule_text(rule), "penalty": -UNCERTAINTY_PREMIUM, "status": "missing"})
            missing_n += 1
            total += UNCERTAINTY_PREMIUM
            continue
        pen = _penalty(rule, v)
        evaluated += 1
        total += pen
        breakdown.append({"key": rule["key"], "component": name,
                          "value": (f"{v:,.0f}" if abs(v) >= 1000 else f"{v:.4g}"),
                          "rule": rule_text(rule), "penalty": -pen,
                          "status": "penalized" if pen else "ok"})
    score = max(0.0, 100.0 - total)
    category = next(code for floor, code in CATEGORIES if score >= floor)
    history_ok = stats is not None
    if not history_ok:
        category = "UNKNOWN"
    note = t(lang, f"note.{category}")
    return {
        "aura_score": round(score, 2),
        "risk_category": category,                      # language-neutral code
        "category_label": category_label(category, lang),
        "recommendation": note + " " + t(lang, "note.disclaimer"),
        "score_breakdown": breakdown,
        "coverage": t(lang, "score.coverage", n=evaluated, total=len(RULES)),
        "uncertainty_penalty": missing_n * UNCERTAINTY_PREMIUM,
        "history_available": history_ok,
    }


def display_rows(breakdown: list, lang: str = "en") -> list:
    """Localized table rows for st.dataframe (no logic should read these)."""
    return [{t(lang, "col.component"): r["component"], t(lang, "col.value"): r["value"],
             t(lang, "col.rule"): r["rule"], t(lang, "col.penalty"): r["penalty"],
             t(lang, "col.status"): t(lang, f"status.{r['status']}")} for r in breakdown]
