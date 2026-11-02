"""
AuraMatrix AI - 1/3/5/10-year token inflation projection

With fixed assumptions, computes the effect of INFLATION and STAKING yield on a position's share of supply.
It does NOT forecast price. If market cap stays flat, price is diluted by the supply growth
(value multiplier = share multiplier).
"""

from core.i18n import t

HORIZONS = (1, 3, 5, 10)


def project_holdings(principal_usd: float, net_inflation_pct: float, staking_apy_pct: float = 0.0, lang: str = "en"):
    infl = net_inflation_pct / 100.0
    apy = staking_apy_pct / 100.0
    real_yield = (1 + apy) / (1 + infl) - 1  # yield net of inflation
    rows = []
    for n in HORIZONS:
        token_mult = (1 + apy) ** n                      # token count if staking rewards are reinvested
        unstaked_share = (1 / (1 + infl)) ** n           # supply-share multiplier for a non-staker
        staked_share = ((1 + apy) / (1 + infl)) ** n     # supply-share multiplier for a staker
        rows.append({
            t(lang, "proj.horizon"): n,
            t(lang, "proj.token_mult"): round(token_mult, 3),
            t(lang, "proj.share_unstaked"): round(unstaked_share, 3),
            t(lang, "proj.share_staked"): round(staked_share, 3),
            t(lang, "proj.value_staked"): round(principal_usd * staked_share, 2),
            t(lang, "proj.value_unstaked"): round(principal_usd * unstaked_share, 2),
        })
    return rows, round(real_yield * 100, 2)
