# Tests written with Meta Muse Code (muse-spark-1.3).
"""Pytest tests for core/scoring.py::score_asset."""

import pytest

from core.scoring import RULES, UNCERTAINTY_PREMIUM, score_asset


def make_asset(**overrides):
    """Benign asset: every spot component scores a zero penalty."""
    asset = {
        "24h_change_pct": 5,
        "daily_volume_usd": 50_000_000,
        "upcoming_vesting_cliff_usd": 0,
        "net_inflation_rate_annual": 5,
    }
    asset.update(overrides)
    return asset


def make_stats(**overrides):
    """Benign stats: every history component scores a zero penalty."""
    stats = {
        "annual_volatility_pct": 30,
        "max_drawdown_pct": -10,
        "sharpe_ratio": 1.0,
        "horizon_days": 7,
        "mc_var95_7d_pct": 5,
        "excess_kurtosis": 1,
    }
    stats.update(overrides)
    return stats


def rows_by_key(result):
    return {row["key"]: row for row in result["score_breakdown"]}


def test_stats_none_gives_unknown_category():
    result = score_asset(make_asset(), None)
    assert result["risk_category"] == "UNKNOWN"
    assert result["history_available"] is False


def test_all_missing_components_have_missing_status_and_penalty():
    result = score_asset({}, None)
    assert len(result["score_breakdown"]) == len(RULES)
    for row in result["score_breakdown"]:
        assert row["status"] == "missing"
        assert row["penalty"] == -UNCERTAINTY_PREMIUM
    assert UNCERTAINTY_PREMIUM == 5
    assert result["uncertainty_penalty"] == len(RULES) * 5
    assert result["aura_score"] == 100 - len(RULES) * 5


@pytest.mark.parametrize("missing_key", [
    "24h_change_pct",
    "daily_volume_usd",
    "upcoming_vesting_cliff_usd",
    "net_inflation_rate_annual",
])
def test_asset_with_missing_component_never_scores_above_95(missing_key):
    asset = make_asset()
    del asset[missing_key]
    result = score_asset(asset, make_stats())
    assert result["aura_score"] <= 95


@pytest.mark.parametrize("change_pct, expected_penalty", [
    (25, -15),
    (15, -8),
    (5, 0),
    (-25, -15),
])
def test_change_24h_tiers(change_pct, expected_penalty):
    result = score_asset(make_asset(**{"24h_change_pct": change_pct}), make_stats())
    assert rows_by_key(result)["change_24h"]["penalty"] == expected_penalty


@pytest.mark.parametrize("volume_usd, expected_penalty", [
    (500_000, -10),
    (5_000_000, -5),
    (50_000_000, 0),
])
def test_liquidity_tiers(volume_usd, expected_penalty):
    result = score_asset(make_asset(daily_volume_usd=volume_usd), make_stats())
    assert rows_by_key(result)["liquidity"]["penalty"] == expected_penalty


def test_score_never_below_zero():
    worst_asset = make_asset(
        **{
            "24h_change_pct": 25,
            "daily_volume_usd": 100,
            "upcoming_vesting_cliff_usd": 1_000_000_000,
            "net_inflation_rate_annual": 60,
        }
    )
    worst_stats = make_stats(
        annual_volatility_pct=150,
        max_drawdown_pct=-80,
        sharpe_ratio=-1.0,
        mc_var95_7d_pct=30,
        excess_kurtosis=10,
    )
    result = score_asset(worst_asset, worst_stats)
    assert result["aura_score"] == 0
    assert result["aura_score"] >= 0
    # Missing-data path is floored too.
    assert score_asset({}, None)["aura_score"] >= 0


@pytest.mark.parametrize("asset, stats", [
    (make_asset(), make_stats()),
    (
        make_asset(**{"24h_change_pct": 25, "daily_volume_usd": 500_000}),
        make_stats(annual_volatility_pct=150, sharpe_ratio=-1.0),
    ),
])
def test_score_and_category_identical_across_languages(asset, stats):
    en = score_asset(asset, stats, "en")
    tr = score_asset(asset, stats, "tr")
    assert en["aura_score"] == tr["aura_score"]
    assert en["risk_category"] == tr["risk_category"]
