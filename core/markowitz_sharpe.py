"""
AuraMatrix AI - Markowitz Sharpe engine
Computes the Sharpe ratio and variance from real price history.
"""

from core.i18n import t
from core.quant_metrics import compute_risk_stats


class MarkowitzSharpeEngine:
    def calculate_sharpe(self, asset_data: dict, lang: str = "en") -> dict:
        stats = compute_risk_stats(asset_data.get("price_history"))
        if stats is None:
            return {"sharpe_ratio": None, "portfolio_variance": None,
                    "status": t(lang, "markowitz.insufficient")}
        daily_var = (stats["annual_volatility_pct"] / 100) ** 2 / 365
        s = stats["sharpe_ratio"]
        level = t(lang, "markowitz.level_strong" if s > 1 else "markowitz.level_weak" if s > 0 else "markowitz.level_neg")
        return {
            "sharpe_ratio": s,
            "annual_volatility_pct": stats["annual_volatility_pct"],
            "portfolio_variance": round(daily_var, 6),
            "status": t(lang, "markowitz.status", level=level, n=stats["n_days"]),
        }
