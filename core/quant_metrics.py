"""
AuraMatrix AI - Real quantitative risk metrics (from daily price history)
"""

import numpy as np

MIN_POINTS = 30
DAYS_PER_YEAR = 365  # crypto trades 24/7


def compute_risk_stats(prices, horizon_days=7, n_sims=10000, seed=42):
    """Computes risk statistics from a list of daily prices; returns None if there is too little data."""
    if not prices or len(prices) < MIN_POINTS:
        return None
    p = np.asarray(prices, dtype=float)
    p = p[p > 0]
    if len(p) < MIN_POINTS:
        return None

    r = np.diff(np.log(p))                 # daily log return
    mu, sd = r.mean(), r.std(ddof=1)
    if sd == 0:
        return None

    # Sharpe (assumes risk-free rate = 0)
    sharpe = mu / sd * np.sqrt(DAYS_PER_YEAR)
    ann_vol = sd * np.sqrt(DAYS_PER_YEAR) * 100

    # Maximum drawdown
    running_max = np.maximum.accumulate(p)
    max_dd = ((p / running_max) - 1).min() * 100

    # Historical VaR (95%, 1 day)
    simple = np.expm1(r)
    hist_var_1d = -np.percentile(simple, 5) * 100

    # Monte Carlo (bootstrap): resample past returns
    out = {}
    for h in (1, horizon_days):
        rng = np.random.default_rng(seed)  # same seed per horizon: stays identical to the stress-test base case
        sims = rng.choice(r, size=(n_sims, h), replace=True).sum(axis=1)
        loss = (1 - np.exp(sims)) * 100
        var95 = np.percentile(loss, 95)
        cvar95 = loss[loss >= var95].mean()
        out[h] = (round(float(var95), 2), round(float(cvar95), 2))

    kurt = float(np.mean(((r - mu) / sd) ** 4) - 3)
    skew = float(np.mean(((r - mu) / sd) ** 3))
    z = -1.645  # 95% left tail
    z_cf = (z + (z**2 - 1) * skew / 6 + (z**3 - 3 * z) * kurt / 24 - (2 * z**3 - 5 * z) * skew**2 / 36)
    cf_var_1d = float((1 - np.exp(mu + sd * z_cf)) * 100)
    z_last = float((r[-1] - mu) / sd)
    mom7 = float(np.expm1(r[-7:].sum()) * 100)

    return {
        "n_days": int(len(p)),
        "sharpe_ratio": round(float(sharpe), 2),
        "annual_volatility_pct": round(float(ann_vol), 2),
        "max_drawdown_pct": round(float(max_dd), 2),
        "hist_var95_1d_pct": round(float(hist_var_1d), 2),
        "mc_var95_1d_pct": out[1][0],
        "mc_cvar95_1d_pct": out[1][1],
        f"mc_var95_{horizon_days}d_pct": out[horizon_days][0],
        f"mc_cvar95_{horizon_days}d_pct": out[horizon_days][1],
        "excess_kurtosis": round(kurt, 2),
        "skewness": round(skew, 2),
        "cf_var95_1d_pct": round(cf_var_1d, 2),
        "last_day_zscore": round(z_last, 2),
        "last_day_return_pct": round(float(simple[-1] * 100), 2),
        "momentum_7d_pct": round(mom7, 2),
        "horizon_days": horizon_days,
    }


def supply_growth_detail(supply):
    """Annualized net supply growth from the circulating-supply series (market cap / price).
    The MEDIAN of the first and last 5 days is used to reduce single-day noise.
    Returns None if the series is too short or nearly constant (the source may not update supply)."""
    if not supply:
        return None
    s = [x for x in supply if x and x > 0]
    if len(s) < MIN_POINTS:
        return None
    if (max(s) - min(s)) / (sum(s) / len(s)) < 1e-4:
        return None
    k = min(5, len(s) // 6)
    start = float(np.median(s[:k]))
    end = float(np.median(s[-k:]))
    span = len(s) - k  # days between the median points
    growth = ((end / start) ** (DAYS_PER_YEAR / span) - 1) * 100
    steps = [abs(s[i] / s[i - 1] - 1) * 100 for i in range(1, len(s))]
    jump = max(steps) if steps else 0.0
    return {"growth_pct": round(float(growth), 2), "start_tokens": start,
            "end_tokens": end, "span_days": int(span),
            "max_daily_jump_pct": round(float(jump), 2)}  # >5: source revision or a real unlock


def annualized_supply_growth(supply):
    d = supply_growth_detail(supply)
    return None if d is None else d["growth_pct"]
