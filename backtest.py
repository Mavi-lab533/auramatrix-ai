"""
AuraMatrix AI - Backtest of the score (a simple, honest test).

Question: when the Aura-Score was low (risky), did the next 30 days really see deeper drawdowns?

Method
- Fetch 365 days of daily price + volume for ~30 coins from CoinGecko.
- For each coin, every 7 days compute the score from "the 90 days up to that day" (looks only backward).
- Compare the score with the realized maximum drawdown of the following 30 days.
- Baseline: the 90-day volatility alone (a very simple measure). If the score cannot beat it, the report says so honestly.

Limits (also written into the report)
- Vesting and supply growth are not available historically; these two components are missing in the test. A constant -10 is deducted in every row.
- Windows overlap and coins are correlated: no p-value is given, only direction and magnitude.
- ~30 coins, a single year, mostly surviving large coins: there is survivorship bias.
Run:  python backtest.py        (needs internet, ~6-8 minutes)
"""
import json
import os
import sys
import time

import numpy as np
import requests

from core.quant_metrics import compute_risk_stats
from core.scoring import score_asset, RULES, rule_name

NAME = {r["key"]: rule_name(r, "en") for r in RULES}

COINS = ["bitcoin", "ethereum", "solana", "ripple", "cardano", "dogecoin", "avalanche-2", "chainlink",
         "polkadot", "litecoin", "injective-protocol", "near", "uniswap", "aptos", "arbitrum", "optimism",
         "cosmos", "stellar", "filecoin", "the-graph", "aave", "maker", "render-token", "bitcoin-cash",
         "ethereum-classic", "algorand", "decentraland", "the-sandbox", "curve-dao-token", "pepe"]
LOOKBACK, FORWARD, STEP = 90, 30, 7


def fetch(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    for attempt in range(5):
        r = requests.get(url, params={"vs_currency": "usd", "days": 365, "interval": "daily"}, timeout=30)
        if r.status_code == 429:
            time.sleep(30 * (attempt + 1))
            continue
        r.raise_for_status()
        d = r.json()
        prices = [p[1] for p in d["prices"]]
        vols = [v[1] for v in d["total_volumes"]]
        n = min(len(prices), len(vols))
        return prices[:n], vols[:n]
    raise RuntimeError(f"{coin_id}: rate limit not cleared")


def ranks(x):
    order = np.argsort(x)
    r = np.empty(len(x))
    r[order] = np.arange(len(x))
    # tied values get the average rank
    for v in np.unique(x):
        m = x == v
        r[m] = r[m].mean()
    return r


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.corrcoef(ranks(a), ranks(b))[0, 1])


def max_drawdown_pct(p):
    p = np.asarray(p, float)
    return float(((p / np.maximum.accumulate(p)) - 1).min() * 100)


def build_rows(series):
    rows = []
    for coin, (prices, vols) in series.items():
        for t in range(LOOKBACK, len(prices) - FORWARD, STEP):
            hist = prices[t - LOOKBACK:t + 1]
            st = compute_risk_stats(hist, n_sims=2000)
            if st is None:
                continue
            ch24 = (prices[t] / prices[t - 1] - 1) * 100
            asset = {"24h_change_pct": ch24, "daily_volume_usd": vols[t], "upcoming_vesting_cliff_usd": None,
                     "net_inflation_rate_annual": None}
            res = score_asset(asset, st)
            sc = res["aura_score"]
            pens = {b["key"]: -b["penalty"] for b in res["score_breakdown"]
                    if b["status"] != "missing"}
            fwd_dd = max_drawdown_pct(prices[t:t + FORWARD + 1])
            fwd_ret = (prices[t + FORWARD] / prices[t] - 1) * 100
            rows.append({"coin": coin, "score": sc, "vol90": st["annual_volatility_pct"],
                         "fwd_dd": fwd_dd, "fwd_ret": fwd_ret, "t": t, "pens": pens})
    return rows



def cross_sectional(rows, key_fn, min_coins=10):
    """Ranks coins against each other on every date; averages the per-date Spearman values (removes market direction)."""
    by_t = {}
    for r in rows:
        by_t.setdefault(r["t"], []).append(r)
    vals = []
    for grp in by_t.values():
        if len(grp) < min_coins:
            continue
        x = np.array([key_fn(r) for r in grp], float)
        y = np.array([r["fwd_dd"] for r in grp], float)
        if x.std() == 0 or y.std() == 0:
            continue
        vals.append(spearman(x, y))
    return (float(np.mean(vals)), len(vals)) if vals else (float("nan"), 0)


def variant_score(r, drop):
    """Score with some components removed from the penalty sum (EXPLORATORY; chosen after seeing results)."""
    return 100.0 - sum(v for k, v in r["pens"].items() if k not in drop)


def report(rows):
    s = np.array([r["score"] for r in rows]); v = np.array([r["vol90"] for r in rows])
    dd = np.array([r["fwd_dd"] for r in rows]); ret = np.array([r["fwd_ret"] for r in rows])
    out = ["# AuraMatrix AI - Backtest (simple test)", "",
           f"Sample: {len(rows)} (coin, date) observations, {len(set(r['coin'] for r in rows))} coins, "
           f"{LOOKBACK} days of history → next {FORWARD} days.", "",
           "## Result", "",
           f"- Spearman correlation between the score and the max drawdown of the next {FORWARD} days: **{spearman(s, dd):+.2f}** "
           "(positive = higher score, SHALLOWER drawdown; the expected direction is positive)",
           f"- Same measure for the baseline (90d volatility only): **{spearman(-v, dd):+.2f}** (the lower the volatility, the shallower the drawdown)",
           f"- Score vs. return over the next {FORWARD} days: **{spearman(s, ret):+.2f}** (the score is NOT a return forecast; for information only)", "",
           f"## Average max drawdown of the next {FORWARD} days by score bucket", "",
           "| Score bucket | Observations | Avg. max drawdown (%) | Median (%) |", "|---|---|---|---|"]
    qs = np.quantile(s, [0, .25, .5, .75, 1])
    for i in range(4):
        m = (s >= qs[i]) & (s <= qs[i + 1]) if i == 3 else (s >= qs[i]) & (s < qs[i + 1])
        if m.sum():
            out.append(f"| {qs[i]:.0f}–{qs[i+1]:.0f} | {int(m.sum())} | {dd[m].mean():.1f} | {np.median(dd[m]):.1f} |")
    out += ["", "## Diagnosis: which component works in which direction?", "",
            f"Spearman correlation between each component's penalty and the max drawdown of the next {FORWARD} days. "
            "A bigger penalty should mean a deeper drawdown, so **negative** is expected; positive = the component works backwards.", "",
            "| Component | Correlation | Direction |", "|---|---|---|"]
    names = sorted({k for r in rows for k in r["pens"]})  # rule keys
    for n in names:
        x = np.array([r["pens"].get(n, 0) for r in rows], float)
        if x.std() == 0:
            out.append(f"| {NAME[n]} | - | penalty never applied |")
            continue
        c = spearman(x, dd)
        out.append(f"| {NAME[n]} | {c:+.2f} | {'expected' if c < -0.03 else ('reversed' if c > 0.03 else 'neutral')} |")
    ts = np.array([r["t"] for r in rows]); mid = np.median(ts)
    a, b = ts <= mid, ts > mid
    out += ["", "## Time split (consistency check)", "",
            f"- First half: score-drawdown correlation **{spearman(s[a], dd[a]):+.2f}**, volatility baseline **{spearman(-v[a], dd[a]):+.2f}**",
            f"- Second half: score-drawdown correlation **{spearman(s[b], dd[b]):+.2f}**, volatility baseline **{spearman(-v[b], dd[b]):+.2f}**"]
    out += ["", "## Same-day comparison (market direction removed)", "",
            f"On every date the coins are compared with each other (which fell deeper over the next {FORWARD} days?) and the per-date values are averaged.", "",
            "| Measure | Avg. same-day correlation | Number of dates |", "|---|---|---|"]
    for label, fn in [("Current score", lambda r: r["score"]), ("Baseline: -volatility", lambda r: -r["vol90"])]:
        m, n = cross_sectional(rows, fn); out.append(f"| {label} | {m:+.2f} | {n} |")
    out += ["", "## EXPLORATORY variants (chosen after seeing results; not evidence)", "",
            "Rationale written first: Sharpe measures past return and maximum drawdown measures past loss; these are performance/past-event measures, not risk.", "",
            "| Variant | Overall | Same-day | First half | Second half |", "|---|---|---|---|---|"]
    for label, drop in [("Current score", set()), ("Sharpe removed", {"sharpe"}),
                        ("Sharpe + max drawdown removed", {"sharpe", "drawdown"})]:
        vs = np.array([variant_score(r, drop) for r in rows])
        if vs.std() == 0:
            continue
        cs, _ = cross_sectional(rows, lambda r, d=drop: variant_score(r, d))
        out.append(f"| {label} | {spearman(vs, dd):+.2f} | {cs:+.2f} | {spearman(vs[a], dd[a]):+.2f} | {spearman(vs[b], dd[b]):+.2f} |")
    out += ["", "## Honesty notes", "",
            "- This is not proof, it is a first check. Because of overlapping windows and correlated coins, no significance test was run.",
            "- The test has no vesting, supply-growth or market-cap components; the score was computed from past price, volume and 24h change only.",
            "- If the score mostly reflects volatility, a correlation similar to the baseline is expected; no added value is claimed.",
            "- Surviving large coins were chosen: real risks (collapsed coins) are missing from the sample.",
            "- Tuning the score after seeing the results risks overfitting; if it is tuned, it must be re-tested on a separate period."]
    return "\n".join(out)


CACHE = "backtest_cache.json"


def main():
    series = {}
    if os.path.exists(CACHE):  # do not re-fetch data on the second run
        series = {k: tuple(v) for k, v in json.load(open(CACHE)).items()}
        print(f"Loaded {len(series)} coins from cache ({CACHE}).")
    else:
        for i, c in enumerate(COINS, 1):
            try:
                series[c] = fetch(c)
                print(f"[{i}/{len(COINS)}] {c}: {len(series[c][0])} days")
            except Exception as e:
                print(f"[{i}/{len(COINS)}] {c}: SKIPPED ({e})", file=sys.stderr)
            time.sleep(8)
        json.dump(series, open(CACHE, "w"))
    rows = build_rows(series)
    if len(rows) < 50:
        sys.exit("Not enough observations.")
    text = report(rows)
    open("backtest_results.md", "w", encoding="utf-8").write(text)
    print("\n" + text)


if __name__ == "__main__":
    main()
