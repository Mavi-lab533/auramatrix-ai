# AuraMatrix AI - Backtest (simple test)

Sample: 1080 (coin, date) observations, 30 coins, 90 days of history → next 30 days.

## Result

- Spearman correlation between the score and the max drawdown of the next 30 days: **-0.16** (positive = higher score, SHALLOWER drawdown; the expected direction is positive)
- Same measure for the baseline (90d volatility only): **+0.16** (the lower the volatility, the shallower the drawdown)
- Score vs. return over the next 30 days: **-0.16** (the score is NOT a return forecast; for information only)

## Average max drawdown of the next 30 days by score bucket

| Score bucket | Observations | Avg. max drawdown (%) | Median (%) |
|---|---|---|---|
| 5–52 | 241 | -17.2 | -16.0 |
| 52–70 | 452 | -16.3 | -15.4 |
| 70–90 | 387 | -19.5 | -18.4 |

## Diagnosis: which component works in which direction?

Spearman correlation between each component's penalty and the max drawdown of the next 30 days. A bigger penalty should mean a deeper drawdown, so **negative** is expected; positive = the component works backwards.

| Component | Correlation | Direction |
|---|---|---|
| 24h price move | -0.06 | expected |
| Maximum drawdown | +0.27 | reversed |
| Fat tails | -0.00 | neutral |
| Daily trading volume | -0.04 | expected |
| Sharpe ratio | +0.30 | reversed |
| Monte Carlo VaR95 (7 days) | +0.11 | reversed |
| Annual volatility | -0.14 | expected |

## Time split (consistency check)

- First half: score-drawdown correlation **-0.36**, volatility baseline **-0.13**
- Second half: score-drawdown correlation **-0.00**, volatility baseline **+0.44**

## Same-day comparison (market direction removed)

On every date the coins are compared with each other (which fell deeper over the next 30 days?) and the per-date values are averaged.

| Measure | Avg. same-day correlation | Number of dates |
|---|---|---|
| Current score | +0.30 | 36 |
| Baseline: -volatility | +0.43 | 36 |

## EXPLORATORY variants (chosen after seeing results; not evidence)

Rationale written first: Sharpe measures past return and maximum drawdown measures past loss; these are performance/past-event measures, not risk.

| Variant | Overall | Same-day | First half | Second half |
|---|---|---|---|---|
| Current score | -0.16 | +0.30 | -0.36 | -0.00 |
| Sharpe removed | -0.10 | +0.32 | -0.35 | +0.15 |
| Sharpe + max drawdown removed | +0.01 | +0.31 | -0.30 | +0.28 |

## Honesty notes

- This is not proof, it is a first check. Because of overlapping windows and correlated coins, no significance test was run.
- The test has no vesting, supply-growth or market-cap components; the score was computed from past price, volume and 24h change only.
- If the score mostly reflects volatility, a correlation similar to the baseline is expected; no added value is claimed.
- Surviving large coins were chosen: real risks (collapsed coins) are missing from the sample.
- Tuning the score after seeing the results risks overfitting; if it is tuned, it must be re-tested on a separate period.