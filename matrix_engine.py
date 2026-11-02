"""
AuraMatrix AI - Master Simulation Engine
Real market data (CoinGecko) + modular risk engines.
"""

import requests

from core.quant_metrics import compute_risk_stats, supply_growth_detail

from core.hegel_dialectic import HegelDialecticEngine
from core.taleb_antifragile import TalebAntifragileEngine
from core.kahneman_prospect import KahnemanProspectEngine
from core.markowitz_sharpe import MarkowitzSharpeEngine
from core.fama_efficiency import FamaEfficiencyEngine
from main import AuraMatrixDialecticEngine, MetaAPIError

NUMERIC_FIELDS = (
    "current_price",
    "24h_change_pct",
    "daily_volume_usd",
    "upcoming_vesting_cliff_usd",
    "net_inflation_rate_annual",
)


class AuraMatrixMasterEngine:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.hegel_engine = HegelDialecticEngine()
        self.taleb_engine = TalebAntifragileEngine()
        self.kahneman_engine = KahnemanProspectEngine()
        self.markowitz_engine = MarkowitzSharpeEngine()
        self.fama_engine = FamaEfficiencyEngine()
        self.llm_engine = AuraMatrixDialecticEngine(api_key=api_key)

    def get_top_100_universe(self) -> dict:
        """Fetches the real top 100 assets from CoinGecko; returns an empty dict on error."""
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "price_change_percentage": "24h,7d",
        }
        try:
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            coins = r.json()
        except requests.RequestException as e:
            print(f"[!] Could not fetch market data: {e}")
            return {}

        universe = {}
        for c in coins:
            a = self._coin_to_asset(c)
            t = a["ticker"]
            if t in universe:  # for coins that share the same symbol
                t = f"{t}_{c['id']}"
                a["ticker"] = t
            universe[t] = a
        return universe

    @staticmethod
    def _coin_to_asset(c: dict) -> dict:
        total = c.get("total_supply") or c.get("max_supply")
        circ = c.get("circulating_supply")
        # Share of supply not yet circulating (%): a PROXY for vesting/inflation pressure
        overhang = round((total - circ) / total * 100, 2) if total and circ else None
        return {
            "ticker": c["symbol"].upper(),
            "coingecko_id": c["id"],
            "name": c["name"],
            "market_cap_rank": c.get("market_cap_rank"),
            "current_price": c.get("current_price"),
            "24h_change_pct": c.get("price_change_percentage_24h") or 0.0,
            "daily_volume_usd": c.get("total_volume"),
            "supply_overhang_pct": overhang,
            "circulating_supply_tokens": circ,
            "total_supply_tokens": total,
            "max_supply_tokens": c.get("max_supply"),
            "non_circulating_tokens": (total - circ) if total and circ else None,
            "non_circulating_usd": ((total - circ) * c["current_price"])
                                   if total and circ and c.get("current_price") else None,
            "change_7d_pct": c.get("price_change_percentage_7d_in_currency"),
            "ath_usd": c.get("ath"),
            "ath_change_pct": c.get("ath_change_percentage"),
            "market_cap_usd": c.get("market_cap"),
            "fdv_usd": c.get("fully_diluted_valuation"),
            "net_inflation_rate_annual": None,      # computed from price history (overhang is NOT inflation)
            "upcoming_vesting_cliff_usd": None,     # no free source
        }

    def search_coins(self, query: str) -> list:
        """Search CoinGecko by name/ticker (includes coins outside the top 100)."""
        try:
            r = requests.get("https://api.coingecko.com/api/v3/search",
                             params={"query": query}, timeout=15)
            r.raise_for_status()
            return r.json().get("coins", [])[:10]
        except (requests.RequestException, ValueError) as e:
            print(f"[!] Coin search failed: {e}")
            return []

    def get_coin_by_id(self, coin_id: str):
        """Current market data for a single coin; None if not found."""
        try:
            r = requests.get("https://api.coingecko.com/api/v3/coins/markets",
                             params={"vs_currency": "usd", "ids": coin_id,
                                     "price_change_percentage": "24h,7d"}, timeout=15)
            r.raise_for_status()
            data = r.json()
            return self._coin_to_asset(data[0]) if data else None
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"[!] Could not fetch coin data ({coin_id}): {e}")
            return None

    def get_market_history(self, coin_id: str, days: int = 90) -> dict:
        """CoinGecko daily price + derived circulating supply (market cap / price)."""
        from datetime import datetime, timezone
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        empty = {"dates": [], "prices": [], "supply": []}
        try:
            r = requests.get(url, params={"vs_currency": "usd", "days": days, "interval": "daily"}, timeout=20)
            r.raise_for_status()
            j = r.json()
            prices = j.get("prices", [])
            mcaps = {pt[0]: pt[1] for pt in j.get("market_caps", [])}
            out = {"dates": [], "prices": [], "supply": []}
            for ts, price in prices:
                if not price:
                    continue
                out["dates"].append(datetime.fromtimestamp(ts / 1000, timezone.utc).strftime("%Y-%m-%d"))
                out["prices"].append(price)
                mc = mcaps.get(ts)
                out["supply"].append(mc / price if mc else None)
            return out
        except (requests.RequestException, ValueError, TypeError) as e:
            print(f"[!] Could not fetch price history ({coin_id}): {e}")
            return empty

    def get_price_history(self, coin_id: str, days: int = 90) -> list:
        return self.get_market_history(coin_id, days)["prices"]

    @staticmethod
    def _clean(asset_data: dict) -> dict:
        """Converts None values to 0.0 (the modules expect numbers)."""
        data = dict(asset_data)
        for k in NUMERIC_FIELDS:
            if data.get(k) is None:
                data[k] = 0.0
        return data

    def run_full_simulation(self, asset_data: dict, use_llm: bool = True, lang: str = "en") -> dict:
        raw = dict(asset_data)  # None values are kept (the LLM receives them as "unknown")
        detail = supply_growth_detail(raw.get("supply_history"))
        supply_growth = detail["growth_pct"] if detail else None
        if detail and raw.get("circulating_supply_tokens"):
            detail["mismatch_vs_current_pct"] = round(
                (detail["end_tokens"] / raw["circulating_supply_tokens"] - 1) * 100, 2)
        if raw.get("net_inflation_rate_annual") is None and supply_growth is not None:
            raw["net_inflation_rate_annual"] = supply_growth
            raw["inflation_source"] = "90-day circulating-supply growth, annualized (approximate)"  # sent to the LLM; keep English
        asset_data = self._clean(raw)
        print(f"[*] AuraMatrix Engine: Analyzing {asset_data.get('ticker')}...")

        tail_risk = self.taleb_engine.evaluate_tail_risk(asset_data, lang)
        fomo_analysis = self.kahneman_engine.analyze_fomo(asset_data, lang)
        sharpe_data = self.markowitz_engine.calculate_sharpe(asset_data, lang)
        anomaly_data = self.fama_engine.check_anomaly(asset_data, lang)

        risk_stats = compute_risk_stats(asset_data.get("price_history"))
        # Rough estimate when there is no history (NOT a real Monte Carlo)
        var_95_heuristic = round(abs(asset_data.get("24h_change_pct", 5.0)) * 1.85, 2)

        macro_report = f"Macro: Tail Risk Score: {tail_risk['tail_risk_score']}"
        onchain_report = f"On-Chain: Anomaly: {anomaly_data['anomaly_detected']}"
        if risk_stats:
            quant_report = (f"Quant: MC VaR95 1d {risk_stats['mc_var95_1d_pct']}%, "
                            f"Sharpe: {risk_stats['sharpe_ratio']}")
        else:
            quant_report = "Quant: no price history, VaR/Sharpe could not be computed"

        synthesis = self.hegel_engine.synthesize(
            macro_report, onchain_report, quant_report, raw, lang
        )

        agent_reports, llm_error = None, None
        if use_llm:
            try:
                metrics = {
                    "tail_risk_score": tail_risk["tail_risk_score"],
                    "fomo_index": fomo_analysis["fomo_index"],
                    "history_stats": risk_stats if risk_stats else
                        "UNAVAILABLE: no price history; do NOT estimate VaR, Sharpe or volatility",
                    "vesting_data_available": bool(raw.get("upcoming_vesting_cliff_usd")),
                }
                skip = {"price_history", "supply_history", "history_dates", "supply_overhang_pct"}
                llm_view = {k: v for k, v in raw.items() if k not in skip}
                for old, new in (("net_inflation_rate_annual", "net_inflation_rate_annual_pct"),
                                 ("current_price", "current_price_usd")):
                    if old in llm_view:
                        llm_view[new] = llm_view.pop(old)
                if raw.get("supply_overhang_pct") is not None:
                    llm_view["non_circulating_supply_pct"] = raw["supply_overhang_pct"]  # NOT inflation
                agent_reports = self.llm_engine.run_agents(llm_view, metrics, lang)
                narrative = self.llm_engine.synthesize(
                    agent_reports, synthesis["aura_score"], asset_data.get("ticker", ""),
                    category=synthesis["category_label"], coverage=synthesis["coverage"],
                    missing=[r["component"] for r in synthesis["score_breakdown"]
                             if r["status"] == "missing"], lang=lang)
                synthesis["dialectic_synthesis"] = narrative["dialectic_synthesis"]
                if narrative["recommendation"]:
                    synthesis["recommendation"] = narrative["recommendation"]
            except MetaAPIError as e:
                llm_error = str(e)

        return {
            "asset": asset_data.get("ticker", "BTC"),
            "synthesis_result": synthesis,
            "agent_reports": agent_reports,
            "llm_error": llm_error,
            "inputs": {k: v for k, v in raw.items()
                       if k not in ("price_history", "supply_history", "history_dates")},
            "sub_modules": {
                "taleb_tail_risk": tail_risk,
                "kahneman_fomo": fomo_analysis,
                "markowitz_sharpe": sharpe_data,
                "fama_efficiency": anomaly_data,
                "var_95_heuristic": var_95_heuristic,
                "risk_stats": risk_stats,
                "supply_growth_annualized_pct": supply_growth,
                "supply_growth_detail": detail,
            },
        }
