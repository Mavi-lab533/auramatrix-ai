"""
AuraMatrix AI - Hegel dialectic engine
Synthesizes thesis (Macro/On-Chain) and antithesis (Quant/Risk) indicators through the transparent
scoring system (core/scoring.py). The narrative text is written by the Meta Model API (Muse Spark).
"""

from typing import Dict, Any

from core.i18n import t
from core.quant_metrics import compute_risk_stats
from core.scoring import score_asset


class HegelDialecticEngine:
    def synthesize(self, macro_report: str, onchain_report: str, quant_report: str, asset_data: dict,
                   lang: str = "en") -> Dict[str, Any]:
        stats = compute_risk_stats(asset_data.get("price_history"))
        result = score_asset(asset_data, stats, lang)
        result["dialectic_synthesis"] = t(lang, "hegel.rule_based", score=result["aura_score"],
                                          cat=result["category_label"], coverage=result["coverage"])
        return result
