"""
AuraMatrix AI - Scenario-based stress test

This is NOT a forecast, it is a "what if" calculation. The shock size is expressed in units of the asset's OWN
daily volatility (sigma); we cannot reliably model the price impact of macro events (rate hikes, equity crashes),
so the user picks a shock size rather than an event.
"""

import numpy as np

MIN_POINTS = 30

# preset code -> (volatility multiplier, day-1 shock in sigma); names come from i18n ("preset.<code>")
PRESETS = {
    "base": (1.0, 0.0),
    "vol2": (2.0, 0.0),
    "liq": (1.5, 3.0),
    "panic": (2.0, 5.0),
}


def stress_test(prices, vol_mult=1.0, shock_sigma=0.0, horizon=7, n_sims=10000, seed=42):
    """Bootstrap simulation: scale past daily returns by vol_mult and subtract a day-1 shock of shock_sigma x sigma."""
    if not prices or len(prices) < MIN_POINTS:
        return None
    p = np.asarray([x for x in prices if x and x > 0], dtype=float)
    if len(p) < MIN_POINTS:
        return None
    r = np.diff(np.log(p))
    mu, sd = r.mean(), r.std(ddof=1)
    if sd == 0:
        return None
    scaled = mu + (r - mu) * vol_mult
    rng = np.random.default_rng(seed)
    sims = rng.choice(scaled, size=(n_sims, horizon), replace=True)
    sims[:, 0] -= shock_sigma * sd
    path = np.cumsum(sims, axis=1)
    loss = (1 - np.exp(path[:, -1])) * 100          # end-of-period loss (%)
    worst = (1 - np.exp(path.min(axis=1))) * 100    # worst point within the period (%)
    var95 = float(np.percentile(loss, 95))
    return {
        "horizon_days": horizon,
        "daily_sigma_pct": round(float(sd * 100), 2),
        "shock_pct": round(float((1 - np.exp(-shock_sigma * sd)) * 100), 2),
        "var95_pct": round(var95, 2),
        "cvar95_pct": round(float(loss[loss >= var95].mean()), 2),
        "worst_intraperiod_median_pct": round(float(np.median(worst)), 2),
        "prob_loss_over_20pct": round(float((loss > 20).mean() * 100), 2),
    }
