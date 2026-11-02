"""
AuraMatrix AI - Kahneman FOMO indicator
Measures only UPSIDE momentum; a low FOMO reading does not mean the asset is safe.
"""

from core.i18n import t
from core.quant_metrics import compute_risk_stats


class KahnemanProspectEngine:
    def analyze_fomo(self, asset_data: dict, lang: str = "en") -> dict:
        chg = asset_data.get("24h_change_pct", 0.0)
        signals = {"24h": chg * 2.2}
        stats = compute_risk_stats(asset_data.get("price_history"))
        if stats:
            signals["7d"] = stats["momentum_7d_pct"] * 1.1
        fomo = min(100.0, max(0.0, *signals.values()))
        return {
            "fomo_index": round(fomo, 2),
            "loss_aversion_warning": chg > 25.0,
            "psychological_state": t(lang, "kahneman.high" if fomo > 60 else "kahneman.none"),
            "basis": t(lang, "kahneman.basis"),
        }
