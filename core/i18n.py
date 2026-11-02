"""
AuraMatrix AI - Minimal i18n (English default, Turkish selectable).

All user-facing text lives here. Logic never depends on localized strings:
scoring rows carry language-neutral codes ("key", "status"), and risk categories are codes
("LOW", "MEDIUM", "HIGH", "VERY_HIGH", "UNKNOWN") that are only turned into labels for display.
"""

LANGS = {"en": "English", "tr": "Türkçe"}
DEFAULT_LANG = "en"
LLM_LANGUAGE = {"en": "English", "tr": "Turkish"}


def pct(lang: str, v, fmt: str = "") -> str:
    """Percent sign placement: '37%' in English, '%37' in Turkish."""
    s = format(v, fmt) if fmt else str(v)
    return f"%{s}" if lang == "tr" else f"{s}%"


def t(lang: str, key: str, **kw) -> str:
    table = STRINGS.get(lang) or STRINGS[DEFAULT_LANG]
    s = table.get(key)
    if s is None:
        s = STRINGS[DEFAULT_LANG].get(key, key)
    return s.format(**kw) if kw else s


STRINGS = {
    "en": {
        # --- scoring: rules ---
        "rule.change_24h.name": "24h price move", "rule.change_24h.metric": "|24h change| (%)", "rule.change_24h.short": "24h move",
        "rule.volatility.name": "Annual volatility", "rule.volatility.metric": "90d annualized (%)", "rule.volatility.short": "Volatility",
        "rule.drawdown.name": "Maximum drawdown", "rule.drawdown.metric": "|90d max drawdown| (%)", "rule.drawdown.short": "Max drawdown",
        "rule.sharpe.name": "Sharpe ratio", "rule.sharpe.metric": "90d, risk-free rate = 0", "rule.sharpe.short": "Sharpe",
        "rule.var7.name": "Monte Carlo VaR95 (7 days)", "rule.var7.metric": "possible 7d loss (%)", "rule.var7.short": "VaR95 (7d)",
        "rule.kurtosis.name": "Fat tails", "rule.kurtosis.metric": "excess kurtosis", "rule.kurtosis.short": "Fat tails",
        "rule.liquidity.name": "Daily trading volume", "rule.liquidity.metric": "USD", "rule.liquidity.short": "Liquidity",
        "rule.vesting.name": "Vesting pressure", "rule.vesting.metric": "vesting / daily volume ratio", "rule.vesting.short": "Vesting",
        "rule.supply.name": "Net supply growth", "rule.supply.metric": "annualized (%)", "rule.supply.short": "Supply growth",
        # --- scoring: categories & notes ---
        "cat.LOW": "Low risk", "cat.MEDIUM": "Medium risk", "cat.HIGH": "High risk", "cat.VERY_HIGH": "Very high risk",
        "cat.UNKNOWN": "Uncertain",
        "cat.UNKNOWN.long": "Uncertain (no price history, limited data)",
        "note.LOW": "The computed indicators are in the low-risk band.",
        "note.MEDIUM": "Some indicators show a moderate level of risk.",
        "note.HIGH": "Several indicators are in the high-risk band.",
        "note.VERY_HIGH": "Most indicators are in the very-high-risk band.",
        "note.UNKNOWN": ("Without price history, the volatility, drawdown, Sharpe and VaR components could not be computed. "
                         "The score relies only on spot data and does NOT mean low risk."),
        "note.disclaimer": "This is not investment advice.",
        "score.no_data": "no data",
        "score.coverage": "{n}/{total} components evaluated",
        "status.missing": "not evaluated", "status.penalized": "penalty applied", "status.ok": "threshold not exceeded",
        "col.component": "Component", "col.value": "Measured value", "col.rule": "Rule", "col.penalty": "Penalty", "col.status": "Status",
        "col.metric": "Metric", "col.rule_penalty": "Rule (penalty)", "col.history": "Needs history",
        "hist.required": "required", "hist.not_required": "not required",
        # --- radar ---
        "radar.aria": "Risk radar: each axis is a score component, risk increases outward",
        "radar.missing": "{name}: no data (uncertainty premium applied)",
        "radar.point": "{name}: {value} · penalty {pen}",
        # --- theme ---
        "brand.tag": ("Three agents weigh thesis and antithesis, a fourth objects. "
                      "The score is computed from an open rule table and missing data is never hidden."),
        "logo.alt": "AuraMatrix logo",
        "hero.provisional": ("Provisional score: without price history, volatility, drawdown, Sharpe and VaR could not be computed. "
                             "This score does not mean low risk."),
        "hero.fomo": "FOMO indicator {v} / 100",
        "card.synthesis": "Synthesis", "card.assessment": "Risk assessment",
        # --- stress presets ---
        "preset.base": "Base case (no shock)",
        "preset.vol2": "Volatility doubles",
        "preset.liq": "Sudden liquidity shock (-3σ on day 1, vol ×1.5)",
        "preset.panic": "Panic selling (-5σ on day 1, vol ×2)",
        "preset.custom": "Custom",
        # --- projection ---
        "proj.horizon": "Horizon (years)",
        "proj.token_mult": "Token count multiplier (staking)",
        "proj.share_unstaked": "Share multiplier - not staked",
        "proj.share_staked": "Share multiplier - staked",
        "proj.value_staked": "Value (if market cap stays flat, staked, USD)",
        "proj.value_unstaked": "Value (if market cap stays flat, not staked, USD)",
        # --- sub-modules ---
        "taleb.basis_hist": "90d history: 7d CVaR95 × 2 (cap 100). Fragile = max drawdown < -50% or CVaR95 > 30%.",
        "taleb.basis_nohist": "24h change only: |change| × 2.5 (cap 100). Rough estimate, no history available.",
        "taleb.fragile": "Loss scenarios are severe (fragile profile).",
        "taleb.not_fragile": "Tail risk is below the thresholds.",
        "kahneman.high": "Clear FOMO signal", "kahneman.none": "No clear FOMO signal",
        "kahneman.basis": "max(24h change × 2.2 ; 7d momentum × 1.1), scaled 0-100. Declines count as 0.",
        "markowitz.insufficient": "Insufficient price history: could not be computed.",
        "markowitz.level_strong": "Strong", "markowitz.level_weak": "Weakly positive", "markowitz.level_neg": "Negative",
        "markowitz.status": "{level} risk-return profile (last {n} days, risk-free rate = 0).",
        "fama.unknown": "Uncertain", "fama.insufficient": "Insufficient price history: test could not be run.",
        "fama.overreaction": "Possible overreaction",
        "fama.stat_only": "Statistical deviation, but economically small",
        "fama.momentum": "Strong short-term momentum",
        "fama.efficient": "Consistent with efficient pricing",
        "fama.details": ("Last-day return {ret}% (z={z}); an anomaly requires |z|>2 AND |return|>={min}%. "
                         "7-day momentum {mom}%."),
        "hegel.rule_based": "Rule-based synthesis: Aura-Score {score}/100 ({cat}); {coverage}.",
        "engine.src_inflation": "90-day circulating-supply growth, annualized (approximate)",
        # --- app: static ---
        "app.title": "AuraMatrix AI - Financial Intelligence",
        "lang.label": "Language / Dil",
        "shot.title": "Read a pump-message screenshot (Muse Spark vision)",
        "shot.help": ("Upload a screenshot of a post like 'this coin will 100x' from Telegram or X. The model extracts the coins, "
                      "promises and pressure tactics. Then analyze that coin from the sidebar with 'Search coin'."),
        "shot.uploader": "Screenshot", "shot.button": "Read image", "shot.spinner": "Muse Spark is reading the image...",
        "shot.unreadable": "The image could not be read or contains no relevant text.",
        "shot.col_coin": "Coin", "shot.col_role": "Role", "shot.col_claims": "Claims",
        "shot.promoted": "Promoted", "shot.mentioned": "Mentioned",
        "shot.signals": "Pressure signals:",
        "shot.disclaimer": "This is an AI extraction and may be wrong; the claims in the post are not verified.",
        "api.failed": "Meta Model API call failed: {err}",
        "meth.title": "How is the score computed?",
        "meth.intro": "**Aura-Score = 100 − sum of penalty points** (floor 0). Each component is penalized according to the thresholds below.",
        "meth.categories": "**Risk categories:**",
        "meth.bullets": ("- **Uncertainty premium:** −5 points for every component that cannot be evaluated. Missing data can never raise the score; "
                         "an asset with a missing component can score at most 95.\n"
                         "- **Without price history** the category is always *Uncertain*, because volatility, drawdown, Sharpe and VaR cannot be computed; "
                         "missing data does not inflate the score, but it does not mean low risk either.\n"
                         "- **Tail risk (Taleb):** 7d CVaR95 × 2 when history exists; otherwise |24h change| × 2.5.\n"
                         "- **FOMO (Kahneman):** max(24h change × 2.2 ; 7d momentum × 1.1), measures upside only.\n"
                         "- **VaR/CVaR:** 10,000 bootstrap simulations of 90-day daily returns. The Sharpe ratio assumes a risk-free rate of 0."),
        "meth.warning": ("Thresholds are expert assumptions; they are not calibrated or backtested into a predictive model. "
                         "The score is not a probability estimate or investment advice."),
        "load.market": "Loading market data...",
        # --- app: sidebar ---
        "sb.header": "Asset parameters",
        "sb.mode": "Data source",
        "sb.mode_top": "Pick from Top 100", "sb.mode_search": "Search coin (all CoinGecko)", "sb.mode_manual": "Manual entry",
        "sb.cg_failed": "Could not load CoinGecko data. Search for a coin or switch to manual entry.",
        "sb.coin": "Coin",
        "sb.search_input": "Coin name or ticker (e.g. tagger)",
        "sb.no_results": "No results on CoinGecko. Try manual entry.",
        "sb.results": "Results",
        "sb.coin_failed": "Could not load market data for this coin.",
        "sb.src_note": ("Price, volume and change: CoinGecko. Vesting: no data. Non-circulating supply: {over} "
                        "(NOT inflation, informational only). Inflation: computed from historical circulating supply."),
        "sb.no_data": "no data",
        "sb.circ": "Circulating supply", "sb.total": "Total supply", "sb.noncirc": "Non-circulating",
        "sb.mcap": "Market cap", "sb.fdv": "FDV (fully diluted)", "sb.tokens": "tokens",
        "sb.cap_label": "Supply cap",
        "sb.cap_yes": "{mx} tokens (hard cap) · {rest} of the cap has not been minted yet",
        "sb.cap_no": "not defined (the source lists no cap; this does not necessarily mean 'unlimited minting')",
        "sb.7d": "7 days", "sb.ath_dist": "Distance from all-time high (ATH)",
        "sb.info_note": ("These are informational and do not enter the score. A supply cap is NOT inflation: the unminted share shows "
                         "supply that may come later but not when."),
        "sb.noncirc_note": ("Non-circulating supply = total − circulating. This does NOT mean locked/vesting: it may be unminted, "
                            "in treasury or locked. The unlock schedule is not available from this source."),
        "sb.manual_note": "Enter the values yourself. Without price history, Sharpe/VaR cannot be computed.",
        "sb.ticker": "Asset / Ticker", "sb.price": "Current price ($)", "sb.change": "24h change (%)",
        "sb.volume": "Daily volume ($)", "sb.vesting": "Upcoming vesting unlock ($)", "sb.inflation": "Annual net inflation (%)",
        "sb.inflation_help": "Leave 0 to compute automatically from historical circulating supply (if available). If you enter a value, it is used instead.",
        "sb.apy": "Staking APY (%) - 0 = not staked",
        "sb.apy_help": "Nominal annual staking yield (enter yourself). Used in the projection.",
        "sb.principal": "Position for projection ($)",
        "sb.use_llm": "Use Meta Muse Spark agents",
        "sb.api_key": "Meta Model API key (optional)",
        "sb.api_key_help": "Used only in this browser session and sent only to Meta's API. It is never stored or logged by this app.",
        "sb.no_key": "No API key: scores, risk statistics, radar, stress test and projection still work; the Meta agents need a key.",
        "sb.run": "Start dialectic analysis",
        "sb.empty": "Ticker is empty or price is 0. Pick/search a coin or enter the values first.",
        "sb.hist_spinner": "Loading price history (90 days)...",
        "sb.agents_spinner": "Agents are working...",
        # --- app: analysis ---
        "an.source": "Data source: {src} · Timestamp: {ts}",
        "an.inputs": "Inputs used in the analysis",
        "an.lang_stale": "This analysis was generated in {old}. Click 'Start dialectic analysis' again to regenerate it in {new}.",
        "an.llm_failed": "Meta Model API call failed; the text below is rule-based (not AI output): {err}",
        "an.llm_ok": "Synthesis and agent reports were produced by muse-spark-1.3.",
        "an.breakdown": "Score breakdown for this analysis ({cov})",
        "an.synth_header": "Synthesis and risk assessment",
        "an.edu": "For education only; not investment advice.",
        "an.radar_header": "Risk radar",
        "an.radar_caption": ("Each axis is a score component; closer to the center = lower risk, risk (penalty) increases outward. "
                             "Dashed yellow circle: no data, uncertainty premium applied. Hover a point to see its value."),
        "an.img_button": "Generate artistic image with Meta (muse-image-1.0, optional)",
        "an.img_spinner": "Muse Image is drawing...",
        "an.img_caption": "Abstract graphic generated from the risk category. It carries no data and is only a visual interpretation.",
        "an.agents_header": "Agent reports (Muse Spark)",
        "role.macro": "Macro agent (thesis)", "role.onchain": "On-chain agent (thesis)", "role.quant": "Quant agent (antithesis)",
        "wi.header": "🔧 What-if agent (tool calling)",
        "wi.caption": ("Ask a hypothetical question, e.g. 'What if volume drops to 1M USD?' The Meta model does not guess: it calls the real "
                       "scoring code as a tool and reports what it returns. The 90-day price statistics stay fixed."),
        "wi.input": "Your what-if question", "wi.button": "Ask", "wi.spinner": "The agent is calling the scoring tool...",
        "wi.calls": "Tool calls made by the model ({n})", "wi.no_calls": "The model answered without calling the tool; treat the answer with caution.",
        "dev.header": "😈 Devil's Advocate",
        "dev.caption": "A fourth agent that tries to refute the score and the synthesis. It uses only the data in this analysis and invents no events.",
        "dev.call": "😈 Call the Devil's Advocate",
        "dev.spinner": "The Devil's Advocate is preparing an objection...",
        "dev.reply": "Your counter-argument or question", "dev.send": "Send", "dev.reply_spinner": "Preparing a reply...",
        "mod.header": "Modular risk matrix",
        "mod.taleb": "Taleb: tail risk", "mod.kahneman": "Kahneman: FOMO",
        "mod.markowitz": "Markowitz: Sharpe (from 90 days of real data)",
        "mod.fama": "Fama: efficiency test (z-score and economic significance)",
        "stats.header": "Risk statistics (90 days)",
        "stats.sharpe": "Sharpe", "stats.vol": "Annual volatility", "stats.dd": "Max drawdown", "stats.var": "MC VaR95 ({h}d)",
        "stats.caption": ("Monte Carlo (10,000 bootstrap simulations), 1d CVaR95: {cvar}, excess kurtosis: {kurt}, skewness: {skew}. "
                          "Cornish-Fisher 1d VaR95 (parametric, adjusted for kurtosis and skewness): {cf}. Risk-free rate assumed 0."),
        "stats.price_col": "Price ($)",
        "stats.supply_caption": "Annualized net supply growth (from 90-day circulating supply, approximate): {v}",
        "stats.supply_note": ("Derived supply series: ≈{start:,.0f} → ≈{end:,.0f} tokens ({days} days). This is derived as market cap ÷ price "
                              "and is NOT official issuance data; compare it with the known issuance rate for large coins. "),
        "stats.warn_mismatch": "WARNING: the last value of the series deviates {mm} from the current circulating supply; the data may be inconsistent.",
        "stats.warn_jump": ("WARNING: the series has a {j} jump in a single day. This may be the source revising its circulating-supply "
                            "calculation (data revision) or a real token unlock; the annualized growth may be inflated because of it, "
                            "verify with an independent source. "),
        "stats.csv": "Download price series as CSV (for independent verification)",
        "stats.nohist": "No price history: Sharpe/Monte Carlo could not be computed. Rough VaR estimate: {v} (not a real simulation).",
        # --- app: stress ---
        "st.header": "Stress test (scenario = assumption, not a forecast)",
        "st.need_hist": "The stress test needs price history (available in the Top 100 / Search coin modes).",
        "st.caption": ("The shock size is chosen in units of the asset's OWN daily volatility (σ). Because we cannot reliably model the price "
                       "impact of events like rate hikes or equity crashes, the scenario is a shock size, not an event."),
        "st.scenario": "Scenario", "st.vm": "Volatility multiplier", "st.shock": "Day-1 shock (-σ)",
        "st.col_scenario": "Scenario", "st.col_var": "7d VaR95 (%)", "st.col_cvar": "7d CVaR95 (%)",
        "st.col_p20": "Probability of loss > 20% (%)", "st.col_pos": "VaR95 for a {amt} USD position (USD)",
        "st.row_base": "Base (no shock)",
        "st.row_scen": "Scenario (vol ×{vm}, -{sh}σ ≈ {shock} on day 1)",
        "st.foot": ("Daily σ ≈ {sigma} · 10,000 bootstrap simulations, assuming past returns repeat and days are independent. "
                    "In tail events the real loss can exceed these values."),
        # --- app: projection ---
        "pr.header": "1, 3, 5 and 10-year inflation projection",
        "pr.no_infl": ("No inflation data, or it is unreliable (price history unavailable, or the source does not update circulating supply and the series stayed flat). "
                       "Fill in 'Annual net inflation' in the sidebar to enable the projection."),
        "pr.negative": ("Net inflation is negative ({v}, supply contraction). Because this is not counted as a return and extrapolating "
                        "90 days of data to 10 years is meaningless, inflation is set to 0 in the projection."),
        "pr.caption": ("Annual net inflation used: {infl} · Staking APY: {apy} · Real (inflation-adjusted) yield: {real}. "
                       "This is NOT a price forecast: inflation is held constant (extrapolating 90 days of supply growth to 10 years is very uncertain) "
                       "and market cap is assumed to stay flat."),
    },
}

STRINGS["tr"] = {
    "rule.change_24h.name": "24s fiyat hareketi", "rule.change_24h.metric": "|24s değişim| (%)", "rule.change_24h.short": "24s hareket",
    "rule.volatility.name": "Yıllık volatilite", "rule.volatility.metric": "90g yıllıklandırılmış (%)", "rule.volatility.short": "Volatilite",
    "rule.drawdown.name": "Maksimum düşüş", "rule.drawdown.metric": "|90g maks. düşüş| (%)", "rule.drawdown.short": "Maks. düşüş",
    "rule.sharpe.name": "Sharpe oranı", "rule.sharpe.metric": "90g, risksiz oran=0", "rule.sharpe.short": "Sharpe",
    "rule.var7.name": "Monte Carlo VaR95 (7 gün)", "rule.var7.metric": "olası 7g kayıp (%)", "rule.var7.short": "VaR95 (7g)",
    "rule.kurtosis.name": "Kalın kuyruk", "rule.kurtosis.metric": "aşırı basıklık (excess kurtosis)", "rule.kurtosis.short": "Kalın kuyruk",
    "rule.liquidity.name": "Günlük işlem hacmi", "rule.liquidity.metric": "USD", "rule.liquidity.short": "Likidite",
    "rule.vesting.name": "Vesting baskısı", "rule.vesting.metric": "vesting / günlük hacim oranı", "rule.vesting.short": "Vesting",
    "rule.supply.name": "Net arz artışı", "rule.supply.metric": "yıllıklandırılmış (%)", "rule.supply.short": "Arz artışı",
    "cat.LOW": "Düşük risk", "cat.MEDIUM": "Orta risk", "cat.HIGH": "Yüksek risk", "cat.VERY_HIGH": "Çok yüksek risk",
    "cat.UNKNOWN": "Belirsiz",
    "cat.UNKNOWN.long": "Belirsiz (fiyat geçmişi yok, sınırlı veri)",
    "note.LOW": "Hesaplanan göstergeler düşük risk bandında.",
    "note.MEDIUM": "Bazı göstergeler orta düzeyde risk işareti veriyor.",
    "note.HIGH": "Birden fazla gösterge yüksek risk bandında.",
    "note.VERY_HIGH": "Göstergelerin çoğu çok yüksek risk bandında.",
    "note.UNKNOWN": ("Fiyat geçmişi olmadığı için volatilite, düşüş, Sharpe ve VaR bileşenleri hesaplanamadı. "
                     "Skor yalnızca anlık verilere dayanır ve düşük risk anlamına GELMEZ."),
    "note.disclaimer": "Bu bir yatırım tavsiyesi değildir.",
    "score.no_data": "veri yok",
    "score.coverage": "{n}/{total} bileşen değerlendirildi",
    "status.missing": "değerlendirilemedi", "status.penalized": "ceza uygulandı", "status.ok": "eşik aşılmadı",
    "col.component": "Bileşen", "col.value": "Ölçülen değer", "col.rule": "Kural", "col.penalty": "Ceza", "col.status": "Durum",
    "col.metric": "Ölçüt", "col.rule_penalty": "Kural (ceza)", "col.history": "Geçmiş verisi",
    "hist.required": "gerekli", "hist.not_required": "gerekmez",
    "radar.aria": "Risk radarı: her eksen bir skor bileşeni, dışa doğru risk artar",
    "radar.missing": "{name}: veri yok (belirsizlik primi uygulandı)",
    "radar.point": "{name}: {value} · ceza {pen}",
    "brand.tag": ("Üç ajan tez ve antitezi tartar, dördüncüsü itiraz eder. "
                  "Skor, kuralları açık bir tabloyla hesaplanır ve eksik veri saklanmaz."),
    "logo.alt": "AuraMatrix logosu",
    "hero.provisional": ("Geçici skor: fiyat geçmişi olmadığı için volatilite, düşüş, Sharpe ve VaR "
                         "hesaplanamadı. Bu skor düşük risk anlamına gelmez."),
    "hero.fomo": "FOMO göstergesi {v} / 100",
    "card.synthesis": "Sentez", "card.assessment": "Risk değerlendirmesi",
    "preset.base": "Baz durum (şok yok)",
    "preset.vol2": "Volatilite 2 katına çıkar",
    "preset.liq": "Ani likidite şoku (-3σ ilk gün, vol ×1,5)",
    "preset.panic": "Panik satışı (-5σ ilk gün, vol ×2)",
    "preset.custom": "Özel",
    "proj.horizon": "Ufuk (yıl)",
    "proj.token_mult": "Token sayısı çarpanı (staking)",
    "proj.share_unstaked": "Pay çarpanı - stake etmeyen",
    "proj.share_staked": "Pay çarpanı - stake eden",
    "proj.value_staked": "Değer (piyasa değeri sabitse, stake eden, USD)",
    "proj.value_unstaked": "Değer (piyasa değeri sabitse, stake etmeyen, USD)",
    "taleb.basis_hist": "90g geçmiş: 7g CVaR95 × 2 (tavan 100). Kırılgan = maks. düşüş < -%50 veya CVaR95 > %30.",
    "taleb.basis_nohist": "Yalnızca 24s değişim: |değişim| × 2,5 (tavan 100). Kaba tahmin, geçmiş veri yok.",
    "taleb.fragile": "Kayıp senaryoları yüksek (kırılgan profil).",
    "taleb.not_fragile": "Kuyruk riski eşiklerin altında.",
    "kahneman.high": "Belirgin FOMO sinyali", "kahneman.none": "Belirgin FOMO sinyali yok",
    "kahneman.basis": "max(24s değişim × 2,2 ; 7g momentum × 1,1), 0-100 arası. Düşüşler 0 sayılır.",
    "markowitz.insufficient": "Yetersiz fiyat geçmişi: hesaplanamadı.",
    "markowitz.level_strong": "Güçlü", "markowitz.level_weak": "Zayıf pozitif", "markowitz.level_neg": "Negatif",
    "markowitz.status": "{level} risk-getiri profili (son {n} gün, risksiz oran=0).",
    "fama.unknown": "Belirsiz", "fama.insufficient": "Yetersiz fiyat geçmişi: test yapılamadı.",
    "fama.overreaction": "Olası aşırı tepki (overreaction)",
    "fama.stat_only": "İstatistiksel sapma var ama ekonomik olarak küçük",
    "fama.momentum": "Güçlü kısa vadeli momentum",
    "fama.efficient": "Etkin fiyatlama ile uyumlu",
    "fama.details": ("Son gün getirisi %{ret} (z={z}); anomali için |z|>2 VE |getiri|>=%{min} gerekir. "
                     "7 günlük momentum %{mom}."),
    "hegel.rule_based": "Kural tabanlı sentez: Aura-Score {score}/100 ({cat}); {coverage}.",
    "engine.src_inflation": "90 günlük dolaşım arzı artışı, yıllıklandırılmış (yaklaşık)",
    "app.title": "AuraMatrix AI - Finansal Zekâ",
    "lang.label": "Language / Dil",
    "shot.title": "Pump mesajı ekran görüntüsünü oku (Muse Spark görsel)",
    "shot.help": ("Telegram veya X'te gördüğün 'bu coin 100x yapar' gibi bir gönderinin ekran görüntüsünü yükle. "
                  "Model görünen coinleri, vaatleri ve baskı tekniklerini çıkarır. Sonra soldan 'Coin ara' ile o coini analiz et."),
    "shot.uploader": "Ekran görüntüsü", "shot.button": "Görseli oku", "shot.spinner": "Muse Spark görseli okuyor...",
    "shot.unreadable": "Görsel okunamadı veya içinde ilgili metin yok.",
    "shot.col_coin": "Coin", "shot.col_role": "Rol", "shot.col_claims": "Vaatler",
    "shot.promoted": "Tanıtılan", "shot.mentioned": "Anılan",
    "shot.signals": "Baskı işaretleri:",
    "shot.disclaimer": "Yapay zekâ çıkarımıdır, hata yapabilir; gönderideki iddialar doğrulanmış değildir.",
    "api.failed": "Meta Model API çağrısı başarısız: {err}",
    "meth.title": "Skor nasıl hesaplanıyor?",
    "meth.intro": "**Aura-Score = 100 − ceza puanlarının toplamı** (alt sınır 0). Her bileşen aşağıdaki eşiklere göre ceza alır.",
    "meth.categories": "**Risk kategorileri:**",
    "meth.bullets": ("- **Belirsizlik primi:** değerlendirilemeyen her bileşen için −5 puan düşülür. Veri eksikliği skoru yükseltemez; eksik veri olan varlık en fazla 95 alabilir.\n"
                     "- **Fiyat geçmişi yoksa** kategori her zaman *Belirsiz* olur, çünkü volatilite, düşüş, Sharpe ve VaR hesaplanamaz; eksik veri skoru şişirmez, ama düşük risk anlamına da gelmez.\n"
                     "- **Kuyruk riski (Taleb):** geçmiş varsa 7g CVaR95 × 2; yoksa |24s değişim| × 2,5.\n"
                     "- **FOMO (Kahneman):** max(24s değişim × 2,2 ; 7g momentum × 1,1), yalnızca yükselişi ölçer.\n"
                     "- **VaR/CVaR:** 90 günlük günlük getirilerden 10.000 bootstrap simülasyonu. Sharpe'ta risksiz oran 0 varsayılır."),
    "meth.warning": ("Eşikler uzman varsayımıdır; geçmiş verilerle kalibre veya backtest edilmemiştir. "
                     "Skor bir olasılık tahmini veya yatırım tavsiyesi değildir."),
    "load.market": "Piyasa verisi yükleniyor...",
    "sb.header": "Varlık parametreleri",
    "sb.mode": "Veri kaynağı",
    "sb.mode_top": "Top 100'den seç", "sb.mode_search": "Coin ara (tüm CoinGecko)", "sb.mode_manual": "Manuel giriş",
    "sb.cg_failed": "CoinGecko verisi alınamadı. Coin ara veya manuel girişe geç.",
    "sb.coin": "Coin",
    "sb.search_input": "Coin adı veya ticker (ör. tagger)",
    "sb.no_results": "CoinGecko'da sonuç bulunamadı. Manuel girişi dene.",
    "sb.results": "Sonuçlar",
    "sb.coin_failed": "Bu coinin piyasa verisi alınamadı.",
    "sb.src_note": ("Fiyat, hacim ve değişim: CoinGecko. Vesting: veri yok. Dolaşım dışı arz: {over} "
                    "(enflasyon DEĞİL, bilgi amaçlı). Enflasyon: geçmiş dolaşım arzından hesaplanır."),
    "sb.no_data": "veri yok",
    "sb.circ": "Dolaşımdaki arz", "sb.total": "Toplam arz", "sb.noncirc": "Dolaşım dışı",
    "sb.mcap": "Piyasa değeri", "sb.fdv": "FDV (tam seyreltilmiş)", "sb.tokens": "token",
    "sb.cap_label": "Arz tavanı",
    "sb.cap_yes": "{mx} token (üst sınır var) · tavanın {rest}'i henüz basılmadı",
    "sb.cap_no": "tanımlı değil (kaynakta üst sınır yok; bu 'sonsuz basılır' demek olmayabilir)",
    "sb.7d": "7 gün", "sb.ath_dist": "Zirveden (ATH) uzaklık",
    "sb.info_note": ("Bunlar bilgi amaçlıdır, skora girmez. Arz tavanı enflasyon DEĞİLDİR: henüz basılmamış pay, "
                     "gelecekte çıkacak arzı gösterir ama zamanlamasını göstermez."),
    "sb.noncirc_note": ("Dolaşım dışı arz = toplam − dolaşımdaki. Bu kilitli/vesting demek DEĞİLDİR: "
                        "basılmamış, hazinede veya kilitli olabilir. Açılış takvimi bu kaynakta yok."),
    "sb.manual_note": "Değerleri kendin gir. Fiyat geçmişi olmadığı için Sharpe/VaR hesaplanmaz.",
    "sb.ticker": "Varlık / Ticker", "sb.price": "Güncel Fiyat ($)", "sb.change": "24 Saatlik Değişim (%)",
    "sb.volume": "Günlük Hacim ($)", "sb.vesting": "Vesting Kilit Açılımı ($)", "sb.inflation": "Yıllık Net Enflasyon (%)",
    "sb.inflation_help": "0 bırakırsan geçmiş dolaşım arzından otomatik hesaplanır (varsa). Manuel girersen o kullanılır.",
    "sb.apy": "Staking APY (%) - 0 = stake edilmiyor",
    "sb.apy_help": "Nominal yıllık staking getirisi (kendin gir). Projeksiyonda kullanılır.",
    "sb.principal": "Projeksiyon için pozisyon ($)",
    "sb.use_llm": "Meta Muse Spark ajanlarını kullan",
    "sb.api_key": "Meta Model API anahtarı (isteğe bağlı)",
    "sb.api_key_help": "Yalnızca bu tarayıcı oturumunda kullanılır, sadece Meta API'sine gönderilir. Uygulama tarafından saklanmaz veya kaydedilmez.",
    "sb.no_key": "API anahtarı yok: skor, risk istatistikleri, radar, stres testi ve projeksiyon çalışır; Meta ajanları için anahtar gerekir.",
    "sb.run": "Diyalektik analizi başlat",
    "sb.empty": "Ticker boş veya fiyat 0. Önce bir coin seç/ara ya da değerleri gir.",
    "sb.hist_spinner": "Fiyat geçmişi yükleniyor (90 gün)...",
    "sb.agents_spinner": "Ajanlar çalışıyor...",
    "an.source": "Veri kaynağı: {src} · Zaman damgası: {ts}",
    "an.inputs": "Analizde kullanılan girdiler",
    "an.lang_stale": "Bu analiz {old} dilinde üretildi. {new} dilinde yeniden üretmek için 'Diyalektik analizi başlat'a tekrar bas.",
    "an.llm_failed": "Meta Model API çağrısı başarısız, aşağıdaki metin kural tabanlıdır (yapay zekâ çıktısı değil): {err}",
    "an.llm_ok": "Sentez ve ajan raporları muse-spark-1.3 tarafından üretildi.",
    "an.breakdown": "Bu analizin puan dökümü ({cov})",
    "an.synth_header": "Sentez ve risk değerlendirmesi",
    "an.edu": "Eğitim amaçlıdır; yatırım tavsiyesi değildir.",
    "an.radar_header": "Risk radarı",
    "an.radar_caption": ("Her eksen bir skor bileşenidir; merkeze yakın = düşük risk, dışa doğru risk (ceza) artar. "
                         "Kesikli sarı daire: veri yok, belirsizlik primi uygulandı. Noktanın üzerine gelince değer görünür."),
    "an.img_button": "Meta ile sanatsal görsel üret (muse-image-1.0, isteğe bağlı)",
    "an.img_spinner": "Muse Image çiziyor...",
    "an.img_caption": "Risk kategorisine göre üretilen soyut grafik. Veri taşımaz, yalnızca görsel bir yorumdur.",
    "an.agents_header": "Ajan raporları (Muse Spark)",
    "role.macro": "Makro ajan (tez)", "role.onchain": "On-chain ajan (tez)", "role.quant": "Quant ajan (antitez)",
    "wi.header": "🔧 Ya şöyle olsaydı ajanı (araç çağırma)",
    "wi.caption": ("Varsayımsal bir soru sor, ör. 'Hacim 1M USD'ye düşse ne olur?' Meta modeli tahmin yürütmez: gerçek skor kodunu "
                   "araç olarak çağırır ve dönen sonucu aktarır. 90 günlük fiyat istatistikleri sabit kalır."),
    "wi.input": "Ya şöyle olsaydı sorun", "wi.button": "Sor", "wi.spinner": "Ajan skor aracını çağırıyor...",
    "wi.calls": "Modelin yaptığı araç çağrıları ({n})", "wi.no_calls": "Model aracı çağırmadan yanıtladı; yanıta temkinli yaklaş.",
    "dev.header": "😈 Şeytanın Avukatı",
    "dev.caption": "Skoru ve sentezi çürütmeye çalışan dördüncü ajan. Yalnızca bu analizdeki verilere dayanır, yeni olay uydurmaz.",
    "dev.call": "😈 Şeytanın Avukatı'nı çağır",
    "dev.spinner": "Şeytanın Avukatı itiraz hazırlıyor...",
    "dev.reply": "Karşı argümanın veya sorun", "dev.send": "Gönder", "dev.reply_spinner": "Cevap hazırlanıyor...",
    "mod.header": "Modüler risk matrisi",
    "mod.taleb": "Taleb: kuyruk riski", "mod.kahneman": "Kahneman: FOMO",
    "mod.markowitz": "Markowitz: Sharpe (90 günlük gerçek veriden)",
    "mod.fama": "Fama: etkinlik testi (z-skoru ve ekonomik anlamlılık)",
    "stats.header": "Risk istatistikleri (90 gün)",
    "stats.sharpe": "Sharpe", "stats.vol": "Yıllık Volatilite", "stats.dd": "Maks. Düşüş", "stats.var": "MC VaR95 ({h}g)",
    "stats.caption": ("Monte Carlo (10.000 bootstrap simülasyonu), CVaR95 1g: {cvar}, aşırı basıklık: {kurt}, çarpıklık: {skew}. "
                      "Cornish-Fisher 1g VaR95 (basıklık ve çarpıklığa göre düzeltilmiş, parametrik): {cf}. Risksiz oran 0 varsayıldı."),
    "stats.price_col": "Fiyat ($)",
    "stats.supply_caption": "Yıllıklandırılmış net arz artışı (90 günlük dolaşım arzından, yaklaşık): {v}",
    "stats.supply_note": ("Türetilmiş arz serisi: ≈{start:,.0f} → ≈{end:,.0f} token ({days} gün). Bu değer piyasa değeri ÷ fiyatla türetilir, "
                          "resmi ihraç verisi DEĞİLDİR; büyük coinlerde bilinen ihraç oranıyla karşılaştır. "),
    "stats.warn_mismatch": "UYARI: serinin son değeri güncel dolaşım arzından {mm} sapıyor, veri tutarsız olabilir.",
    "stats.warn_jump": ("UYARI: serinin tek bir gününde {j} sıçrama var. Bu, kaynağın dolaşım arzı "
                        "hesabını değiştirmesi (veri revizyonu) ya da gerçek bir token açılımı olabilir; yıllıklandırılmış "
                        "artış bu yüzden şişmiş olabilir, bağımsız kaynakla doğrula. "),
    "stats.csv": "Fiyat serisini CSV indir (bağımsız doğrulama için)",
    "stats.nohist": "Fiyat geçmişi yok: Sharpe/Monte Carlo hesaplanamadı. Kaba VaR tahmini: {v} (gerçek simülasyon değil).",
    "st.header": "Stres testi (senaryo = varsayım, tahmin değil)",
    "st.need_hist": "Stres testi için fiyat geçmişi gerekli (Top 100 / Coin ara modlarında gelir).",
    "st.caption": ("Şok büyüklüğü, varlığın KENDİ günlük oynaklığı (σ) cinsinden seçilir. Faiz artışı veya borsa krizi gibi "
                   "olayların fiyata etkisini güvenilir biçimde modelleyemediğimiz için olay değil şok büyüklüğü senaryo olarak verilir."),
    "st.scenario": "Senaryo", "st.vm": "Volatilite çarpanı", "st.shock": "İlk gün şoku (-σ)",
    "st.col_scenario": "Senaryo", "st.col_var": "7g VaR95 (%)", "st.col_cvar": "7g CVaR95 (%)",
    "st.col_p20": "Kayıp > %20 olasılığı (%)", "st.col_pos": "{amt} USD pozisyon için VaR95 (USD)",
    "st.row_base": "Baz (şok yok)",
    "st.row_scen": "Senaryo (vol ×{vm}, -{sh}σ ≈ {shock} ilk gün)",
    "st.foot": ("Günlük σ ≈ {sigma} · 10.000 bootstrap simülasyonu, geçmiş getirilerin tekrarlandığı "
                "ve günlerin bağımsız olduğu varsayılır. Kuyruk olaylarında gerçek kayıp bu değerleri aşabilir."),
    "pr.header": "1, 3, 5 ve 10 yıllık enflasyon projeksiyonu",
    "pr.no_infl": ("Enflasyon verisi yok veya güvenilmez (fiyat geçmişi alınamadı ya da kaynak dolaşım arzını güncellemiyor, seri sabit kaldı). "
                   "Soldan 'Yıllık Net Enflasyon' alanını doldurarak projeksiyonu aç."),
    "pr.negative": ("Net enflasyon negatif ({v}, arz daralması). Bu bir getiri sayılmadığı ve 90 günlük veriyi "
                    "10 yıla taşımak anlamsız olduğu için projeksiyonda enflasyon 0 alındı."),
    "pr.caption": ("Kullanılan yıllık net enflasyon: {infl} · Staking APY: {apy} · Enflasyona göre net getiri: {real}. "
                   "Fiyat tahmini DEĞİLDİR: enflasyon sabit kabul edilir (90 günlük arz artışının 10 yıla taşınması çok belirsizdir) "
                   "ve piyasa değerinin sabit kaldığı varsayılır."),
}
