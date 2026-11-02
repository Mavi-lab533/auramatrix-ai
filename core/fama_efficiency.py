"""
AuraMatrix AI - Fama market-efficiency engine
Simple z-score test: requires statistical AND economic significance (|return| >= 2%) together.
This is not a formal efficiency test.
"""

from core.i18n import t
from core.quant_metrics import compute_risk_stats

MIN_ECONOMIC_MOVE_PCT = 2.0


class FamaEfficiencyEngine:
    def check_anomaly(self, asset_data: dict, lang: str = "en") -> dict:
        stats = compute_risk_stats(asset_data.get("price_history"))
        if stats is None:
            return {"efficiency_level": t(lang, "fama.unknown"), "anomaly_detected": None,
                    "details": t(lang, "fama.insufficient")}
        z, ret, mom = stats["last_day_zscore"], stats["last_day_return_pct"], stats["momentum_7d_pct"]
        statistical = abs(z) > 2
        economic = abs(ret) >= MIN_ECONOMIC_MOVE_PCT
        anomaly = statistical and economic
        if anomaly:
            level = t(lang, "fama.overreaction")
        elif statistical:
            level = t(lang, "fama.stat_only")
        elif abs(mom) > 20:
            level = t(lang, "fama.momentum")
        else:
            level = t(lang, "fama.efficient")
        return {
            "efficiency_level": level,
            "anomaly_detected": anomaly,
            "details": t(lang, "fama.details", ret=ret, z=z, min=MIN_ECONOMIC_MOVE_PCT, mom=mom),
        }
