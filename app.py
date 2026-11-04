"""
AuraMatrix AI - Streamlit dashboard
Live top-100 market data + Meta Model API (Muse Spark) dialectic agents.
UI language: English (default) or Turkish, chosen in the sidebar. All text lives in core/i18n.py.
"""

from datetime import datetime, timezone

import streamlit as st
from matrix_engine import AuraMatrixMasterEngine
from main import get_api_key, format_debate_context, MetaAPIError


def _page_icon():
    try:
        import pathlib
        from PIL import Image
        return Image.open(pathlib.Path(__file__).parent / "assets" / "favicon.png")
    except Exception:
        return "🔮"


st.set_page_config(page_title="AuraMatrix AI - Financial Intelligence", page_icon=_page_icon(), layout="wide")

from core.i18n import LANGS, DEFAULT_LANG, t, pct
from core.meta_media import analyze_screenshot, generate_aura_image
from core.radar import radar_svg
from core.theme import CSS, brand_html, hero_html, role_card, synthesis_card
from core.scoring import RULES, CATEGORIES, rule_text, rule_name, rule_metric, category_label, display_rows
from core.projection import project_holdings
from core.stress import stress_test, PRESETS

st.markdown(CSS, unsafe_allow_html=True)

# ---- language switch (first widget in the sidebar so everything below can use it) ----
_codes = list(LANGS)
_choice = st.sidebar.radio(t(DEFAULT_LANG, "lang.label"), _codes, format_func=lambda c: LANGS[c],
                           index=_codes.index(DEFAULT_LANG), horizontal=True, key="lang_choice")
lang = _choice


def T(key, **kw):
    return t(lang, key, **kw)


def P(v, fmt=""):
    return pct(lang, v, fmt)


def esc(text) -> str:
    """Streamlit markdown treats '$...$' as LaTeX; escape dollar signs."""
    return str(text).replace("$", "\\$")


def render_methodology():
    st.markdown(T("meth.intro"))
    st.table([{T("col.component"): rule_name(r, lang), T("col.metric"): rule_metric(r, lang),
               T("col.rule_penalty"): rule_text(r),
               T("col.history"): T("hist.required" if r["needs_history"] else "hist.not_required")} for r in RULES])
    st.markdown(T("meth.categories") + " " + " · ".join(
        f"{category_label(code, lang)} (≥{floor})" if floor else f"{category_label(code, lang)} (<25)"
        for floor, code in CATEGORIES))
    st.markdown(T("meth.bullets"))
    st.warning(T("meth.warning"))


st.markdown(brand_html(lang), unsafe_allow_html=True)

with st.expander(T("shot.title")):
    st.caption(T("shot.help"))
    shot = st.file_uploader(T("shot.uploader"), type=["png", "jpg", "jpeg", "webp"], key="shot_up")
    if shot and st.button(T("shot.button"), key="shot_btn"):
        try:
            with st.spinner(T("shot.spinner")):
                st.session_state["shot_result"] = analyze_screenshot(shot.getvalue(), shot.type, lang, st.session_state.get("user_api_key", "").strip())
        except MetaAPIError as e:
            st.error(T("api.failed", err=e))
    sr = st.session_state.get("shot_result")
    if sr:
        if not sr.get("readable", True):
            st.warning(T("shot.unreadable"))
        st.write(esc(sr.get("summary", "")))
        if sr.get("coins"):
            roles_map = {"promoted": T("shot.promoted"), "mentioned": T("shot.mentioned")}
            st.table([{T("shot.col_coin"): esc(c.get("name_or_ticker", "?")),
                       T("shot.col_role"): roles_map.get(c.get("role"), "?"),
                       T("shot.col_claims"): esc("; ".join(map(str, c.get("claims", []))))} for c in sr["coins"]])
        if sr.get("hype_signals"):
            st.markdown("**" + T("shot.signals") + "** " + esc(", ".join(sr["hype_signals"])))
        st.caption(T("shot.disclaimer"))
with st.expander(T("meth.title")):
    render_methodology()


@st.cache_data(ttl=300, show_spinner="Loading market data...")
def load_universe() -> dict:
    return AuraMatrixMasterEngine().get_top_100_universe()


@st.cache_data(ttl=300, show_spinner=False)
def search_coins(q: str) -> list:
    return AuraMatrixMasterEngine().search_coins(q)


@st.cache_data(ttl=120, show_spinner=False)
def fetch_coin(coin_id: str):
    return AuraMatrixMasterEngine().get_coin_by_id(coin_id)


universe = load_universe()

st.sidebar.header(T("sb.header"))
modes = ["top", "search", "manual"]
mode_names = {"top": T("sb.mode_top"), "search": T("sb.mode_search"), "manual": T("sb.mode_manual")}
mode = st.sidebar.radio(T("sb.mode"), modes, format_func=lambda m: mode_names[m],
                        index=0 if universe else 1, key="mode_choice")

blank = {"ticker": "", "current_price": 0.0, "24h_change_pct": 0.0, "daily_volume_usd": 0.0,
         "upcoming_vesting_cliff_usd": 0.0, "net_inflation_rate_annual": 0.0}
asset_c = None

if mode == "top":
    if not universe:
        st.sidebar.error(T("sb.cg_failed"))
    else:
        labels = {k: f"#{d['market_cap_rank']} {k} - {d['name']}" for k, d in universe.items()}
        # Keep the user's coin when the cached Top-100 list refreshes (ranks/order change every few minutes).
        keys = list(labels)
        prev = st.session_state.get("coin_pick_prev")
        idx = keys.index(prev) if prev in keys else 0
        pick = st.sidebar.selectbox(T("sb.coin"), keys, index=idx, format_func=lambda k: labels[k])
        st.session_state["coin_pick_prev"] = pick
        asset_c = universe[pick]
elif mode == "search":
    q = st.sidebar.text_input(T("sb.search_input"))
    if q.strip():
        results = search_coins(q.strip())
        if not results:
            st.sidebar.warning(T("sb.no_results"))
        else:
            rl = {r["id"]: f"{r['symbol'].upper()} - {r['name']} (#{r.get('market_cap_rank') or '?'})" for r in results}
            pid = st.sidebar.selectbox(T("sb.results"), list(rl), format_func=lambda i: rl[i])
            asset_c = fetch_coin(pid)
            if asset_c is None:
                st.sidebar.error(T("sb.coin_failed"))

if asset_c:
    source, cg_id = "coingecko", asset_c["coingecko_id"]
    defaults = {
        "ticker": asset_c["ticker"],
        "current_price": float(asset_c["current_price"] or 0.0),
        "24h_change_pct": float(asset_c["24h_change_pct"] or 0.0),
        "daily_volume_usd": float(asset_c["daily_volume_usd"] or 0.0),
        "upcoming_vesting_cliff_usd": 0.0,
        "net_inflation_rate_annual": 0.0,
    }
    over = asset_c["supply_overhang_pct"]
    st.sidebar.caption(esc(T("sb.src_note", over=T("sb.no_data") if over is None else P(over))))
    USD = "\\$"  # keep markdown from reading '$' as LaTeX

    def _n(x, pre=""):
        return T("sb.no_data") if x is None else f"{pre}{x:,.0f}"

    tok = T("sb.tokens")
    st.sidebar.markdown(
        f"**{T('sb.circ')}:** {_n(asset_c.get('circulating_supply_tokens'))} {tok}  \n"
        f"**{T('sb.total')}:** {_n(asset_c.get('total_supply_tokens'))} {tok}  \n"
        f"**{T('sb.noncirc')}:** {_n(asset_c.get('non_circulating_tokens'))} {tok} "
        f"≈ {_n(asset_c.get('non_circulating_usd'), USD)}  \n"
        f"**{T('sb.mcap')}:** {_n(asset_c.get('market_cap_usd'), USD)}  \n"
        f"**{T('sb.fdv')}:** {_n(asset_c.get('fdv_usd'), USD)}")
    mx, circ = asset_c.get("max_supply_tokens"), asset_c.get("circulating_supply_tokens")
    if mx and circ:
        cap_txt = T("sb.cap_yes", mx=f"{mx:,.0f}", rest=P(max(0.0, (mx - circ) / mx * 100), ".1f"))
    else:
        cap_txt = T("sb.cap_no")
    ch7, athc = asset_c.get("change_7d_pct"), asset_c.get("ath_change_pct")
    st.sidebar.markdown(
        f"**{T('sb.cap_label')}:** {cap_txt}  \n"
        f"**{T('sb.7d')}:** {T('sb.no_data') if ch7 is None else P(ch7, '+.1f')}  \n"
        f"**{T('sb.ath_dist')}:** {T('sb.no_data') if athc is None else P(athc, '.1f')}"
        + ("" if not asset_c.get("ath_usd") else f" (ATH {USD}{asset_c['ath_usd']:,.4g})"))
    st.sidebar.caption(T("sb.info_note"))
    st.sidebar.caption(T("sb.noncirc_note"))
else:
    source, cg_id, defaults = "manual", None, blank
    st.sidebar.caption(T("sb.manual_note"))

k = cg_id if source == "coingecko" else "manual"
ticker = st.sidebar.text_input(T("sb.ticker"), value=defaults["ticker"], key=f"t_{k}")
current_price = st.sidebar.number_input(T("sb.price"), value=defaults["current_price"], format="%.8g", key=f"p_{k}")
change_pct = st.sidebar.number_input(T("sb.change"), value=defaults["24h_change_pct"], key=f"c_{k}")
daily_volume = st.sidebar.number_input(T("sb.volume"), value=defaults["daily_volume_usd"], key=f"v_{k}")
vesting_cliff = st.sidebar.number_input(T("sb.vesting"), value=defaults["upcoming_vesting_cliff_usd"], key=f"vc_{k}")
inflation_rate = st.sidebar.number_input(T("sb.inflation"), value=defaults["net_inflation_rate_annual"], key=f"i_{k}",
                                         help=T("sb.inflation_help"))
staking_apy = st.sidebar.number_input(T("sb.apy"), value=0.0, min_value=0.0, key=f"apy_{k}", help=T("sb.apy_help"))
principal = st.sidebar.number_input(T("sb.principal"), value=1000.0, min_value=1.0, key=f"pr_{k}")
use_llm = st.sidebar.checkbox(T("sb.use_llm"), value=True)
user_key = st.sidebar.text_input(T("sb.api_key"), type="password", key="user_api_key", help=T("sb.api_key_help"))
API_KEY = user_key.strip() or get_api_key()   # session-only key typed in the UI, else .env / environment
if use_llm and not API_KEY:
    st.sidebar.info(T("sb.no_key"))

if st.sidebar.button(T("sb.run")):
    if not ticker.strip() or current_price <= 0:
        st.error(T("sb.empty"))
        st.stop()
    asset_data = {
        "data_source": "coingecko" if source == "coingecko" else "manual_user_input",
        "ticker": ticker,
        "current_price": current_price,
        "24h_change_pct": change_pct,
        "daily_volume_usd": daily_volume,
        "upcoming_vesting_cliff_usd": vesting_cliff if (vesting_cliff > 0 or source == "manual") else None,
        "net_inflation_rate_annual": inflation_rate if (inflation_rate != 0 or source == "manual") else None,
        "supply_overhang_pct": asset_c["supply_overhang_pct"] if asset_c else None,
        **({f: asset_c.get(f) for f in ("circulating_supply_tokens", "total_supply_tokens", "non_circulating_tokens",
                                        "non_circulating_usd", "market_cap_usd", "fdv_usd")} if asset_c else {}),
        "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }

    engine = AuraMatrixMasterEngine(api_key=API_KEY)
    if cg_id and source == "coingecko":
        with st.spinner(T("sb.hist_spinner")):
            hist = engine.get_market_history(cg_id)
        asset_data["price_history"] = hist["prices"]
        asset_data["supply_history"] = hist["supply"]
        asset_data["history_dates"] = hist["dates"]
    with st.spinner(T("sb.agents_spinner")):
        result = engine.run_full_simulation(asset_data, use_llm=use_llm, lang=lang)

    st.session_state["analysis"] = {"asset_data": asset_data, "result": result, "use_llm": use_llm,
                                    "debate": [], "stress_run": False, "lang": lang}

analysis = st.session_state.get("analysis")
if analysis:
    asset_data, result, use_llm = analysis["asset_data"], analysis["result"], analysis["use_llm"]
    if analysis.get("lang", DEFAULT_LANG) != lang:
        st.info(T("an.lang_stale", old=LANGS[analysis["lang"]], new=LANGS[lang]))
    st.caption(T("an.source", src=asset_data["data_source"], ts=asset_data["fetched_at_utc"]))
    with st.expander(T("an.inputs")):
        st.json(result["inputs"])

    synthesis = result["synthesis_result"]
    sub = result["sub_modules"]

    if use_llm and result["llm_error"]:
        st.error(T("an.llm_failed", err=result["llm_error"]))
    elif use_llm:
        st.success(T("an.llm_ok"))

    st.markdown(hero_html(result["asset"], synthesis["aura_score"], synthesis["risk_category"],
                          synthesis["coverage"], sub["kahneman_fomo"]["fomo_index"],
                          provisional=not synthesis["history_available"], lang=lang), unsafe_allow_html=True)
    with st.expander(T("an.breakdown", cov=synthesis["coverage"]), expanded=True):
        st.dataframe(display_rows(synthesis["score_breakdown"], lang), hide_index=True)

    st.subheader(T("an.synth_header"))
    st.markdown(synthesis_card(synthesis["dialectic_synthesis"], synthesis["recommendation"], lang), unsafe_allow_html=True)
    st.caption(T("an.edu"))

    st.subheader(T("an.radar_header"))
    st.markdown(f'<div style="max-width:560px;margin:auto">{radar_svg(synthesis["score_breakdown"], RULES, lang=lang)}</div>',
                unsafe_allow_html=True)
    st.caption(T("an.radar_caption"))

    if st.button(T("an.img_button"), key="aura_img_btn"):
        try:
            with st.spinner(T("an.img_spinner")):
                analysis["aura_image"] = generate_aura_image(synthesis["risk_category"], synthesis["aura_score"], API_KEY)
        except MetaAPIError as e:
            st.error(T("api.failed", err=e))
    if analysis.get("aura_image"):
        st.image(analysis["aura_image"], width=640, caption=T("an.img_caption"))

    if result["agent_reports"]:
        st.subheader(T("an.agents_header"))
        roles = {"macro": ("role.macro", "thesis"), "onchain": ("role.onchain", "thesis"), "quant": ("role.quant", "anti")}
        for key, text in result["agent_reports"].items():
            label_key, tone = roles[key]
            st.markdown(role_card(T(label_key), tone, text), unsafe_allow_html=True)

    st.subheader(T("dev.header"))
    st.caption(T("dev.caption"))
    llm = AuraMatrixMasterEngine(api_key=API_KEY).llm_engine
    debate = analysis["debate"]
    ctx = format_debate_context(result)
    if st.button(T("dev.call"), key="adv_call"):
        try:
            with st.spinner(T("dev.spinner")):
                debate.clear()
                debate.append(("assistant", llm.devils_advocate(ctx, [], lang)))
        except MetaAPIError as e:
            st.error(T("api.failed", err=e))
    for role, text in debate:
        with st.chat_message("assistant" if role == "assistant" else "user"):
            st.write(esc(text))
    if debate:
        with st.form("debate_form", clear_on_submit=True):
            reply = st.text_area(T("dev.reply"), height=80)
            sent = st.form_submit_button(T("dev.send"))
        if sent and reply.strip():
            try:
                with st.spinner(T("dev.reply_spinner")):
                    debate.append(("user", reply.strip()))
                    debate.append(("assistant", llm.devils_advocate(ctx, debate, lang)))
                st.rerun()
            except MetaAPIError as e:
                debate.pop()
                st.error(T("api.failed", err=e))

    st.subheader(T("wi.header"))
    st.caption(T("wi.caption"))
    with st.form("whatif_form"):
        wi_q = st.text_input(T("wi.input"), key="wi_q")
        wi_go = st.form_submit_button(T("wi.button"))
    if wi_go and wi_q.strip():
        base_asset = {**result["inputs"], "price_history": asset_data.get("price_history")}
        try:
            with st.spinner(T("wi.spinner")):
                analysis["whatif"] = llm.whatif(wi_q.strip(), base_asset, sub["risk_stats"], lang)
        except MetaAPIError as e:
            st.error(T("api.failed", err=e))
    if analysis.get("whatif"):
        wi_text, wi_calls = analysis["whatif"]
        st.write(esc(wi_text))
        if wi_calls:
            with st.expander(T("wi.calls", n=len(wi_calls))):
                for c in wi_calls:
                    st.json(c)
        else:
            st.warning(T("wi.no_calls"))

    st.subheader(T("mod.header"))
    with st.expander(T("mod.taleb")):
        st.write(sub["taleb_tail_risk"])
    with st.expander(T("mod.kahneman")):
        st.write(sub["kahneman_fomo"])
    with st.expander(T("mod.markowitz")):
        st.write(sub["markowitz_sharpe"])
    with st.expander(T("mod.fama")):
        st.write(sub["fama_efficiency"])
    stats = sub["risk_stats"]
    st.subheader(T("stats.header"))
    if stats:
        a, b, c2, d = st.columns(4)
        a.metric(T("stats.sharpe"), stats["sharpe_ratio"])
        b.metric(T("stats.vol"), P(stats["annual_volatility_pct"]))
        c2.metric(T("stats.dd"), P(stats["max_drawdown_pct"]))
        d.metric(T("stats.var", h=stats["horizon_days"]), P(stats["mc_var95_7d_pct"]))
        st.caption(T("stats.caption", cvar=P(stats["mc_cvar95_1d_pct"]), kurt=stats["excess_kurtosis"],
                     skew=stats["skewness"], cf=P(stats["cf_var95_1d_pct"])))
        import pandas as pd
        dates, prices = asset_data["history_dates"], asset_data["price_history"]
        if len(dates) == len(prices):
            st.line_chart(pd.DataFrame({T("stats.price_col"): prices}, index=pd.to_datetime(dates)), color="#F4C265")
        else:
            st.line_chart(prices)
        sg = sub["supply_growth_annualized_pct"]
        if sg is not None:
            st.caption(T("stats.supply_caption", v=P(sg)))
            sd_ = sub["supply_growth_detail"]
            note = T("stats.supply_note", start=sd_["start_tokens"], end=sd_["end_tokens"], days=sd_["span_days"])
            mm = sd_.get("mismatch_vs_current_pct")
            if mm is not None and abs(mm) > 0.5:
                note += T("stats.warn_mismatch", mm=P(mm))
            if sd_.get("max_daily_jump_pct", 0) > 5:
                note += T("stats.warn_jump", j=P(sd_["max_daily_jump_pct"]))
            st.caption(esc(note))
        csv = "date,price_usd\n" + "\n".join(f"{dt},{p}" for dt, p in zip(asset_data["history_dates"], asset_data["price_history"]))
        st.download_button(T("stats.csv"), csv, f"{asset_data['ticker']}_90d.csv", "text/csv")
    else:
        st.warning(T("stats.nohist", v=P(sub["var_95_heuristic"])))

    st.subheader(T("st.header"))
    hist_prices = asset_data.get("price_history") or []
    if len(hist_prices) < 30:
        st.info(T("st.need_hist"))
    else:
        st.caption(T("st.caption"))
        names = list(PRESETS) + ["custom"]
        pick_s = st.selectbox(T("st.scenario"), names, format_func=lambda c: T(f"preset.{c}"), key="stress_pick")
        if pick_s == "custom":
            c1, c2 = st.columns(2)
            vm = c1.slider(T("st.vm"), 0.5, 4.0, 1.5, 0.1, key="stress_vm")
            sh = c2.slider(T("st.shock"), 0.0, 8.0, 3.0, 0.5, key="stress_sh")
        else:
            vm, sh = PRESETS[pick_s]
        base = stress_test(hist_prices, 1.0, 0.0)
        scen = stress_test(hist_prices, vm, sh)
        if base and scen:
            pos_col = T("st.col_pos", amt=f"{principal:,.0f}")
            rows = [
                {T("st.col_scenario"): T("st.row_base"), T("st.col_var"): base["var95_pct"], T("st.col_cvar"): base["cvar95_pct"],
                 T("st.col_p20"): base["prob_loss_over_20pct"],
                 pos_col: round(principal * base["var95_pct"] / 100, 2)},
                {T("st.col_scenario"): T("st.row_scen", vm=vm, sh=sh, shock=P(scen["shock_pct"])),
                 T("st.col_var"): scen["var95_pct"], T("st.col_cvar"): scen["cvar95_pct"],
                 T("st.col_p20"): scen["prob_loss_over_20pct"],
                 pos_col: round(principal * scen["var95_pct"] / 100, 2)},
            ]
            if vm == 1.0 and sh == 0.0:
                rows = rows[:1]  # a shock-free scenario equals the base case; do not repeat it
            st.table(rows)
            st.caption(T("st.foot", sigma=P(scen["daily_sigma_pct"])))

    st.subheader(T("pr.header"))
    infl_used = result["inputs"].get("net_inflation_rate_annual")
    if infl_used is None:
        st.info(T("pr.no_infl"))
    else:
        infl_proj = max(infl_used, 0.0)
        if infl_used < 0:
            st.info(T("pr.negative", v=P(infl_used)))
        rows, real_apy = project_holdings(principal, infl_proj, staking_apy, lang)
        st.table(rows)
        st.caption(T("pr.caption", infl=P(infl_proj), apy=P(staking_apy), real=P(real_apy)))
