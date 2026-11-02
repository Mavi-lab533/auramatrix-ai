"""
AuraMatrix AI - Hegelian dialectic agents on the Meta Model API
Three agents (Macro, On-Chain, Quant) run in parallel; a fourth call writes the synthesis.
On failure NO fake answer is produced; an explicit MetaAPIError is raised.
Output language (English / Turkish) is a parameter of every call.
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

import requests

from core.i18n import LLM_LANGUAGE, t
from core.scoring import score_asset

ENDPOINT = "https://api.meta.ai/v1/chat/completions"
MODEL = "muse-spark-1.3"


def _load_dotenv() -> None:
    """Reads the .env file in the project folder (no extra library needed). .env is NEVER committed to the repo."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    try:
        with open(path, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except OSError:
        pass


_load_dotenv()


def get_api_key() -> str:
    return os.environ.get("MODEL_API_KEY", "")


class MetaAPIError(Exception):
    pass


_ROLE_PROMPTS = {
    "macro": ("You are a Macro and Inflationist Agent. Analyze global liquidity, interest rates and inflation pressure for the "
              "given crypto asset. Use ONLY the data provided; if a field is missing or zero because data is unavailable, say so. "
              "Answer in {L}, max 120 words."),
    "onchain": ("You are an On-Chain and Tokenomics Agent. Analyze supply overhang, emissions, burn and vesting pressure for the "
                "given asset. Use ONLY the data provided; state clearly when data is unavailable. Answer in {L}, max 120 words."),
    "quant": ("You are a Quant Risk Agent. Analyze volatility, price extension, liquidity (volume) and downside risk from the "
              "given metrics. Use ONLY the data provided. Answer in {L}, max 120 words."),
}

_STYLE_EXAMPLES = {
    "en": ("say 'annual net inflation' or 'no vesting data' instead. "
           "Write large numbers readably (1.57 trillion USD, 77.5 billion USD)."),
    "tr": ("say 'yıllık net enflasyon' or 'vesting verisi yok' instead. "
           "Write large numbers readably (1,57 trilyon USD, 77,5 milyar USD)."),
}


def units_note(lang: str) -> str:
    return (
        " UNITS: every field whose name ends with _pct is ALREADY a percentage (0.37 means 0.37%, NOT 37%). "
        "*_usd fields are US dollars. Do not claim high inflation/emission unless net_inflation_rate_annual_pct is large "
        "in percent terms. Never convert units yourself. "
        "Supply figures come from CoinGecko (market cap / price); they may not reflect staking emission or token burns, "
        "so a ~0% net inflation means 'no change in the reported supply', NOT proof that there is no emission or burn. "
        f"STYLE: write in plain {LLM_LANGUAGE[lang]} for a retail reader. Never quote raw field names (no snake_case such as "
        "net_inflation_rate_annual_pct, vesting_data_available, upcoming_vesting_cliff_usd); "
        + _STYLE_EXAMPLES[lang]
    )


def consistency_note(lang: str) -> str:
    low = t(lang, "cat.LOW")
    return (
        " CONSISTENCY: name the given risk category verbatim and keep the tone consistent with it. Do NOT call the "
        f"situation strong, safe or healthy unless the category is '{low}'. Always mention the data gaps listed, "
        "because unevaluated components can make the score look better than reality. Do not give buy/sell advice."
    )


def system_prompt(role: str, lang: str = "en") -> str:
    return _ROLE_PROMPTS[role].format(L=LLM_LANGUAGE[lang]) + units_note(lang)


def synthesis_prompt(lang: str = "en") -> str:
    return (
        "You are the Hegelian synthesis engine. Given three agent reports (thesis: macro/on-chain, "
        "antithesis: quant/risk) and a computed Aura-Score, write the dialectical synthesis in "
        f"{LLM_LANGUAGE[lang]}. "
        "Respond ONLY with JSON: {\"dialectic_synthesis\": \"<3-4 sentences>\", "
        "\"recommendation\": \"<1-2 sentence risk assessment, not investment advice>\"}"
    ) + units_note(lang) + consistency_note(lang)


def devil_prompt(lang: str = "en") -> str:
    return (
        "You are the Devil's Advocate agent of a crypto risk-analysis system. The system produced a risk score and a "
        "synthesis. Challenge it constructively. Using ONLY the data in the context (never invent events, prices, whale "
        "moves, news or exchange problems), give the 3 strongest reasons the score could be MISLEADING: data gaps, the short "
        "90-day window, noisy Sharpe, bootstrap assumptions (past returns repeat, days independent), derived supply "
        "estimates, missing vesting/unlock data, thresholds being unvalidated expert assumptions. Number them. Then list 2 "
        "concrete things the user should verify independently. If the user replies with a counter-argument, answer "
        "honestly: concede valid points, hold firm where the data supports the risk. No buy/sell advice. "
        f"Answer in {LLM_LANGUAGE[lang]}, max 200 words."
    ) + units_note(lang)


def format_debate_context(result: dict) -> str:
    """Analysis summary for the Devil's Advocate (units explicit). Rows use language-neutral keys."""
    s, sub = result["synthesis_result"], result["sub_modules"]
    lines = [f"Asset: {result['asset']}", f"Aura-Score: {s['aura_score']}/100",
             f"Risk category: {s['category_label']}", f"Score coverage: {s['coverage']}", "Score breakdown:"]
    for r in s["score_breakdown"]:
        lines.append(f"- {r['component']}: value={r['value']} | rule={r['rule']} | "
                     f"penalty={r['penalty']} | {r['status']}")
    lines.append("90-day history stats: " + (json.dumps(sub["risk_stats"], ensure_ascii=False)
                                             if sub.get("risk_stats") else "UNAVAILABLE"))
    if sub.get("supply_growth_detail"):
        lines.append("Derived supply series: " + json.dumps(sub["supply_growth_detail"], ensure_ascii=False))
    inputs = dict(result.get("inputs", {}))
    for old, new in (("net_inflation_rate_annual", "net_inflation_rate_annual_pct"), ("current_price", "current_price_usd")):
        if old in inputs:
            inputs[new] = inputs.pop(old)
    lines.append("Inputs: " + json.dumps(inputs, ensure_ascii=False, default=str))
    if result.get("agent_reports"):
        for k, v in result["agent_reports"].items():
            lines.append(f"{k} agent: {v}")
    lines.append("Synthesis: " + s["dialectic_synthesis"])
    return "\n".join(lines)


RESCORE_TOOL = {
    "type": "function",
    "function": {
        "name": "rescore",
        "description": ("Recompute the Aura-Score with hypothetical inputs using the real scoring rules. "
                        "Omit a field to keep its current value."),
        "parameters": {
            "type": "object",
            "properties": {
                "change_24h_pct": {"type": "number", "description": "Hypothetical 24h price change in percent (5 means +5%)."},
                "daily_volume_usd": {"type": "number", "description": "Hypothetical daily trading volume in USD."},
                "vesting_unlock_usd": {"type": "number", "description": "Hypothetical upcoming token unlock in USD."},
                "net_inflation_pct": {"type": "number", "description": "Hypothetical annual net supply inflation in percent."},
            },
        },
    },
}

_ARG_TO_FIELD = {"change_24h_pct": "24h_change_pct", "daily_volume_usd": "daily_volume_usd",
                 "vesting_unlock_usd": "upcoming_vesting_cliff_usd", "net_inflation_pct": "net_inflation_rate_annual"}


def _whatif_inputs(asset: dict) -> dict:
    return {a: asset.get(f) for a, f in _ARG_TO_FIELD.items()}


def _run_rescore(args: dict, asset: dict, stats, lang: str) -> dict:
    """Executes the tool: only whitelisted numeric fields are overridden; everything else is untouched."""
    hypo = dict(asset)
    applied = {}
    for a, f in _ARG_TO_FIELD.items():
        v = args.get(a)
        if isinstance(v, (int, float)) and not isinstance(v, bool) and abs(v) < 1e15:
            hypo[f] = float(v)
            applied[a] = float(v)
    res = score_asset(hypo, stats, lang)
    return {"applied": applied, "aura_score": res["aura_score"], "category": res["category_label"],
            "coverage": res["coverage"],
            "penalties": {r["component"]: r["penalty"] for r in res["score_breakdown"] if r["penalty"]}}


class AuraMatrixDialecticEngine:
    def __init__(self, api_key: str = "", endpoint: str = ENDPOINT, model: str = MODEL):
        self.api_key = api_key or get_api_key()
        self.endpoint = endpoint
        self.model = model

    def _request(self, messages: list, tools: list = None) -> dict:
        """POST to chat/completions and return the assistant message dict (may contain tool_calls)."""
        if not self.api_key:
            raise MetaAPIError("API key not found: add the line MODEL_API_KEY=... to the .env file in the project folder.")
        payload = {"model": self.model, "messages": messages, "temperature": 0.2}
        if tools:
            payload["tools"] = tools
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            r = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        except requests.RequestException as e:
            raise MetaAPIError(f"Connection error: {e}") from e
        if r.status_code != 200:
            raise MetaAPIError(f"API returned {r.status_code}: {r.text[:300]}")
        try:
            return r.json()["choices"][0]["message"]
        except (KeyError, IndexError, ValueError) as e:
            raise MetaAPIError(f"Unexpected response format: {r.text[:300]}") from e

    def _chat(self, system: str, user) -> str:
        msgs = [{"role": "system", "content": system}] \
            + ([{"role": "user", "content": user}] if isinstance(user, str) else list(user))
        return (self._request(msgs).get("content") or "").strip()

    def whatif(self, question: str, asset: dict, stats, lang: str = "en", max_rounds: int = 3):
        """Agentic what-if: the model may call the `rescore` tool (the real scoring code) any number of times.
        Returns (answer_text, calls) where calls is a list of {"args", "result"} for transparency."""
        base = score_asset(asset, stats, lang)
        sys_msg = (
            "You are the what-if agent of a crypto risk-analysis system. The user asks how the Aura-Score would change "
            "under hypothetical inputs. NEVER guess scores: call the rescore tool with the hypothetical values and report "
            "exactly what it returns. You may call it several times to compare cases. Only the inputs the tool exposes can "
            "change; the 90-day price-history statistics stay fixed, say so if relevant. Explain which component moved. "
            f"No buy/sell advice. Answer in {LLM_LANGUAGE[lang]}, max 150 words."
        )
        messages = [{"role": "system", "content": sys_msg},
                    {"role": "user", "content": f"Current score: {base['aura_score']}/100 ({base['category_label']}). "
                                                f"Current inputs: {json.dumps(_whatif_inputs(asset), default=str)}\n"
                                                f"Question: {question}"}]
        calls = []
        for _ in range(max_rounds + 1):
            msg = self._request(messages, tools=[RESCORE_TOOL])
            tcs = msg.get("tool_calls") or []
            if not tcs:
                return (msg.get("content") or "").strip(), calls
            messages.append({"role": "assistant", "content": msg.get("content") or "", "tool_calls": tcs})
            for tc in tcs:
                try:
                    args = json.loads(tc["function"].get("arguments") or "{}")
                except ValueError:
                    args = {}
                result = _run_rescore(args, asset, stats, lang)
                calls.append({"args": args, "result": result})
                messages.append({"role": "tool", "tool_call_id": tc.get("id", ""),
                                 "content": json.dumps(result, ensure_ascii=False)})
        return (self._request(messages).get("content") or "").strip(), calls

    def devils_advocate(self, context: str, turns: list, lang: str = "en") -> str:
        """turns: [("assistant", text), ("user", text), ...]; the first user message is context + task."""
        msgs = [{"role": "user", "content": "CONTEXT:\n" + context + "\n\nTask: challenge this analysis."}]
        msgs += [{"role": role, "content": text} for role, text in turns]
        return self._chat(devil_prompt(lang), msgs)

    def run_agents(self, asset_data: dict, metrics: dict, lang: str = "en") -> Dict[str, str]:
        user = "Asset data: " + json.dumps(asset_data, ensure_ascii=False) + \
               "\nComputed metrics: " + json.dumps(metrics, ensure_ascii=False)
        with ThreadPoolExecutor(max_workers=3) as ex:
            futures = {role: ex.submit(self._chat, system_prompt(role, lang), user) for role in _ROLE_PROMPTS}
            return {role: f.result() for role, f in futures.items()}

    def synthesize(self, reports: Dict[str, str], aura_score: float, ticker: str,
                   category: str = "", coverage: str = "", missing=None, lang: str = "en") -> Dict[str, str]:
        gaps = ", ".join(missing) if missing else "none"
        user = (f"Asset: {ticker}\nAura-Score: {aura_score}/100\nRisk category (use verbatim): {category}\n"
                f"Score coverage: {coverage}\nComponents NOT evaluated (data gaps): {gaps}\n"
                f"Macro: {reports['macro']}\nOn-chain: {reports['onchain']}\nQuant: {reports['quant']}")
        text = self._chat(synthesis_prompt(lang), user)
        cleaned = text.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(cleaned)
            return {
                "dialectic_synthesis": data.get("dialectic_synthesis", cleaned),
                "recommendation": data.get("recommendation", ""),
            }
        except ValueError:
            return {"dialectic_synthesis": text, "recommendation": ""}


if __name__ == "__main__":
    sample = {"ticker": "BTC", "current_price": 65000, "24h_change_pct": 2.1,
              "daily_volume_usd": 3e10, "upcoming_vesting_cliff_usd": 0.0,
              "net_inflation_rate_annual": 1.7}
    eng = AuraMatrixDialecticEngine()
    try:
        out = eng.run_agents(sample, {})
        print(json.dumps(out, indent=2, ensure_ascii=False))
    except MetaAPIError as e:
        print("ERROR:", e)
