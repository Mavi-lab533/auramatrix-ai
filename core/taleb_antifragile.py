"""
AuraMatrix AI - Taleb tail-risk module
Uses the 7-day CVaR95 when price history exists; otherwise a rough estimate from the 24h change only.
"""

from core.i18n import t
from core.quant_metrics import compute_risk_stats


class TalebAntifragileEngine:
    def evaluate_tail_risk(self, asset_data: dict, lang: str = "en") -> dict:
        stats = compute_risk_stats(asset_data.get("price_history"))
        if stats:
            cvar = stats[f"mc_cvar95_{stats['horizon_days']}d_pct"]
            score = min(100.0, cvar * 2)
            fragile = stats["max_drawdown_pct"] < -50 or cvar > 30
            basis = t(lang, "taleb.basis_hist")
            fat = stats["excess_kurtosis"] > 3
        else:
            score = min(100.0, abs(asset_data.get("24h_change_pct", 0.0)) * 2.5)
            fragile = score > 40.0
            basis = t(lang, "taleb.basis_nohist")
            fat = None
        return {
            "tail_risk_score": round(score, 2),
            "is_fragile": fragile,
            "fat_tails": fat,
            "basis": basis,
            "assessment": t(lang, "taleb.fragile" if fragile else "taleb.not_fragile"),
        }
