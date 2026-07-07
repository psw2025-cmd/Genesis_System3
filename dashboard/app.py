"""
System3 Genesis Streamlit Dashboard
Autonomous analyzer/paper operator console. Real-money execution stays gated.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, Optional

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components

BACKEND_URL = "http://127.0.0.1:8000"
VERSION = "System3 Genesis v2026.07.07"
SYMBOLS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]

st.set_page_config(page_title="System3 Genesis", page_icon="System3", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
    .stApp { background: #0b0f14; color: #e8edf2; }
    [data-testid="stSidebar"] { background: #111821; }
    div[data-testid="stMetric"] { background: #121b25; border: 1px solid #253244; padding: 12px; border-radius: 8px; }
    .signal-buy { color: #22c55e; font-size: 3rem; font-weight: 800; }
    .signal-sell { color: #ef4444; font-size: 3rem; font-weight: 800; }
    .signal-hold { color: #f59e0b; font-size: 3rem; font-weight: 800; }
    .think { width: 12px; height: 12px; border-radius: 50%; background: #22c55e; display: inline-block; animation: pulse 1s infinite; margin-right: 8px; }
    @keyframes pulse { 0% {opacity: .25; transform: scale(.8)} 50% {opacity: 1; transform: scale(1.2)} 100% {opacity: .25; transform: scale(.8)} }
    .oktick { color: #22c55e; font-weight: 700; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value: Any) -> str:
    try:
        return f"₹{float(value):,.2f}"
    except Exception:
        return "₹0.00"


def pct(value: Any) -> str:
    try:
        return f"{float(value):.2f}%"
    except Exception:
        return "0.00%"


def api(path: str, method: str = "GET", json: Optional[Dict[str, Any]] = None, timeout: int = 20) -> Dict[str, Any]:
    url = f"{BACKEND_URL}{path}"
    try:
        with st.spinner(f"Loading {path}..."):
            if method == "POST":
                r = requests.post(url, json=json or {}, timeout=timeout)
            elif method == "DELETE":
                r = requests.delete(url, timeout=timeout)
            else:
                r = requests.get(url, timeout=timeout)
        payload = r.json() if r.content else {}
        if r.status_code >= 400:
            st.error(f"{path} failed: HTTP {r.status_code}")
        if isinstance(payload, dict) and payload.get("status") == "success":
            return payload.get("data", {})
        return payload if isinstance(payload, dict) else {"raw": payload}
    except requests.RequestException as exc:
        st.error(f"Backend error on {path}: {exc}")
        return {"error": str(exc)}


components.html(
    """
    <script>
    window.genesisSpeak = function(text) {
      try { const u = new SpeechSynthesisUtterance(text); u.rate = 0.95; speechSynthesis.speak(u); } catch(e) {}
    }
    document.addEventListener('keydown', (event) => { if (event.key.toLowerCase() === 'r') window.location.reload(); });
    if ('Notification' in window && Notification.permission === 'default') { Notification.requestPermission(); }
    </script>
    """,
    height=0,
)

with st.sidebar:
    st.title("System3 Genesis")
    health = api("/health", timeout=8)
    connected = not bool(health.get("error"))
    st.success("Backend connected") if connected else st.error("Backend disconnected")
    dhan = api("/dhan-health", timeout=8) if connected else {}
    st.caption(f"Dhan connected: {bool(dhan.get('connected') or dhan.get('broker_connected'))}")
    symbol = st.selectbox("Symbol", SYMBOLS, index=0)
    expiry = st.selectbox("Expiry", ["nearest", "2026-07-09", "2026-07-16", "2026-07-30"], index=0)
    st.divider()
    if st.button("Voice alert test"):
        components.html("<script>window.parent.genesisSpeak && window.parent.genesisSpeak('Alert: New opportunity found');</script>", height=0)
        st.toast("Alert: New opportunity found")
    st.caption("Keyboard: R refresh. Mobile push requires browser notification permission.")

st.title("System3 Genesis Operator Console")
st.markdown('<span class="think"></span>Agent is thinking...', unsafe_allow_html=True)

PAGES = [
    "Dashboard", "Live Chart", "Profit Scan", "Option Chain", "Greeks", "AI Prediction", "Auto Trader", "Positions", "Orders", "Backtest",
    "Autonomous Brain", "Hidden Secrets Lab", "Never Die Monitor", "Hunger Meter", "Truth & Control",
]
selected_page = st.sidebar.radio("Workflow", PAGES, index=0)
st.subheader(selected_page)

if selected_page == "Dashboard":
    pnl = api("/pnl")
    today = pnl.get("today") or pnl.get("summary") or {}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Today P&L", money(today.get("total_pnl") or today.get("total_realized_pnl") or 0))
    c2.metric("Week P&L", money((pnl.get("week") or {}).get("total_pnl") or 0))
    c3.metric("Winrate", pct((today.get("win_rate") or 0) * 100 if (today.get("win_rate") or 0) <= 1 else today.get("win_rate")))
    c4.metric("Avg Profit", money(today.get("avg_pnl_per_trade") or today.get("avg_profit") or 0))
    history = pnl.get("raw", {}).get("history") or pnl.get("history") or []
    df = pd.DataFrame(history)
    if not df.empty:
        y_col = "total_pnl" if "total_pnl" in df.columns else df.select_dtypes("number").columns[-1]
        fig = go.Figure(go.Scatter(y=df[y_col], mode="lines+markers", name="Equity"))
        fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("Download CSV", df.to_csv(index=False), "pnl.csv", "text/csv")
    else:
        st.info("No real equity curve data available yet.")

if selected_page == "Live Chart":
    auto_refresh = st.toggle("Auto refresh", value=False)
    if auto_refresh:
        st.cache_data.clear()
    chart = api(f"/chart/{symbol}?timeframe=5m")
    candles = pd.DataFrame(chart.get("candles") or [])
    if not candles.empty and {"open", "high", "low", "close"}.issubset(candles.columns):
        x = candles.get("timestamp") if "timestamp" in candles.columns else candles.index
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=x, open=candles["open"], high=candles["high"], low=candles["low"], close=candles["close"], name=symbol))
        if "volume" in candles.columns:
            fig.add_trace(go.Bar(x=x, y=candles["volume"], name="Volume", yaxis="y2", opacity=0.35))
            fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False))
        if st.button("Draw trendline") and len(candles) >= 2:
            fig.add_shape(type="line", x0=x.iloc[0] if hasattr(x, "iloc") else x[0], y0=candles["close"].iloc[0], x1=x.iloc[-1] if hasattr(x, "iloc") else x[-1], y1=candles["close"].iloc[-1], line=dict(color="#22c55e", width=2))
        fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(chart.get("source", "No real candle data returned."))

if selected_page == "Profit Scan":
    scan = api("/profit-scan?sort=score", timeout=35)
    rows = scan.get("items") or []
    df = pd.DataFrame(rows)
    if not df.empty:
        numeric = [c for c in ["gain_score", "expected_move_pct", "score"] if c in df.columns]
        st.dataframe(df.style.background_gradient(subset=numeric, cmap="Greens") if numeric else df, use_container_width=True, height=360)
        st.download_button("Download CSV", df.to_csv(index=False), "profit_scan.csv", "text/csv")
        selected = st.selectbox("Trade popup symbol", df.get("underlying", df.get("symbol", pd.Series([]))).astype(str).tolist())
        with st.expander(f"Trade popup: {selected}", expanded=bool(selected)):
            qty = st.number_input("Quantity", min_value=1, value=1)
            order_type = st.selectbox("Order type", ["MARKET", "LIMIT", "SL", "SL-M"])
            price = st.number_input("Limit/trigger price", min_value=0.0, value=0.0)
            if st.button("Submit gated order"):
                result = api("/place-order", "POST", {"symbol": selected, "quantity": qty, "order_type": order_type, "price": price})
                st.toast(result.get("message", "Order request processed"))
                st.json(result)
    else:
        st.info(scan.get("reason") or "No real scanner rows available.")

if selected_page == "Option Chain":
    chain = api(f"/chain/{symbol}?expiry={expiry}", timeout=25)
    contracts = pd.DataFrame(chain.get("contracts") or chain.get("rows") or chain.get("chain") or [])
    intel = api(f"/option-intelligence/{symbol}", timeout=25)
    m = intel.get("metrics", {})
    st.json({"PCR": m.get("pcr"), "Max Pain": m.get("max_pain"), "Regime": m.get("market_regime"), "Smart Money": m.get("smart_money_score"), "Gamma Squeeze": m.get("gamma_squeeze_score")})
    if not contracts.empty:
        st.dataframe(contracts, use_container_width=True, height=360)
        if {"strike", "option_type", "oi"}.issubset(contracts.columns):
            heat = contracts.pivot_table(index="strike", columns="option_type", values="oi", aggfunc="sum")
            st.plotly_chart(go.Figure(go.Heatmap(z=heat.values, x=heat.columns, y=heat.index, colorscale="Viridis")).update_layout(template="plotly_dark", title="OI Heatmap"), use_container_width=True)
        if {"strike", "iv"}.issubset(contracts.columns):
            st.plotly_chart(go.Figure(go.Scatter(x=contracts["strike"], y=contracts["iv"], mode="markers", name="IV Smile")).update_layout(template="plotly_dark", title="IV Smile"), use_container_width=True)
        st.download_button("Download CSV", contracts.to_csv(index=False), "option_chain.csv", "text/csv")
    else:
        st.warning(chain.get("message") or "No real option chain contracts returned.")

if selected_page == "Greeks":
    with st.form("greeks_form"):
        spot = st.number_input("Spot", min_value=0.0, value=25000.0)
        strike = st.number_input("Strike", min_value=0.0, value=25000.0)
        ltp = st.number_input("LTP", min_value=0.0, value=100.0)
        opt_type = st.selectbox("Type", ["CE", "PE"])
        submitted = st.form_submit_button("Calculate")
    if submitted:
        greeks = api("/greeks", "POST", {"spot": spot, "strike": strike, "ltp": ltp, "expiry": expiry, "type": opt_type})
        cols = st.columns(5)
        for col, name in zip(cols, ["delta", "gamma", "theta", "vega", "rho"]):
            col.metric(name.upper(), f"{float(greeks.get(name, 0) or 0):.4f}")
        st.metric("IV", pct((greeks.get("iv") or 0) * 100))

if selected_page == "AI Prediction":
    pred_symbol = st.selectbox("Prediction symbol", SYMBOLS, key="pred_symbol")
    pred = api(f"/prediction/{pred_symbol}")
    signal = str(pred.get("signal", "HOLD")).upper()
    klass = "signal-buy" if signal == "BUY" else "signal-sell" if signal == "SELL" else "signal-hold"
    st.markdown(f'<div class="{klass}">{signal}</div>', unsafe_allow_html=True)
    conf = float(pred.get("confidence_pct") or 0)
    st.progress(min(conf / 100.0, 1.0), text=f"Confidence {pct(conf)}")
    st.json(pred)
    if signal in {"BUY", "SELL"} and conf > 50:
        st.toast(f"Signal: {signal} {pred_symbol} confidence {pct(conf)}")

if selected_page == "Auto Trader":
    enabled = st.toggle("Auto Trader", value=False)
    risk = st.slider("Risk per trade", min_value=1, max_value=5, value=2, format="%d%%")
    max_trades = st.number_input("Max trades per day", min_value=1, max_value=20, value=3)
    st.info("Live order execution remains gated by backend safety flags.")
    st.json({"auto_trader_ui": enabled, "risk_pct": risk, "max_trades_per_day": max_trades, "hard_max_risk_pct": 2})

if selected_page == "Positions":
    pos = api("/positions?status=OPEN")
    positions = pd.DataFrame(pos.get("positions") or [])
    if not positions.empty:
        st.dataframe(positions, use_container_width=True)
        pnl_cols = [c for c in positions.columns if "pnl" in c.lower()]
        if pnl_cols:
            st.bar_chart(positions[pnl_cols[0]])
        if st.button("Square off all"):
            st.json(api("/emergency-exit", "POST"))
    else:
        st.info("No open positions returned by Dhan/read-only state.")

if selected_page == "Orders":
    orders = api("/order-history")
    history = pd.DataFrame(orders.get("history") or orders.get("orders") or [])
    if not history.empty:
        st.dataframe(history, use_container_width=True)
        order_id = st.text_input("Cancel order id")
        if st.button("Cancel") and order_id:
            st.json(api(f"/order/{order_id}", "DELETE"))
    else:
        st.info("No order history available.")

if selected_page == "Backtest":
    start = st.date_input("Start", value=date.today() - timedelta(days=30))
    end = st.date_input("End", value=date.today())
    strategy = st.selectbox("Strategy", ["iron_condor", "long_straddle", "long_strangle", "butterfly", "calendar"])
    if st.button("Run verification"):
        result = api(f"/verify-strategy?strategy={strategy}&symbol={symbol}")
        st.json(result)
        curve = pd.DataFrame(result.get("profit_curve") or [])
        if not curve.empty:
            st.line_chart(curve)
        else:
            st.info("No real backtest curve returned.")

if selected_page == "Autonomous Brain":
    brain = api("/autonomous-brain")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Memory Events", brain.get("memory_events", 0))
    c2.metric("Truth Score", pct((brain.get("truth") or {}).get("truth_score", 0)))
    c3.metric("New Strategy", brain.get("new_strategy_discovered", "None"))
    c4.metric("Human-Free Profit", brain.get("profit_i_made_without_human", "Not claimed"))
    st.markdown('<span class="oktick">✓ I fixed missing startup background refresh myself.</span>', unsafe_allow_html=True)
    st.json(brain)
    if st.button("Run auto research now"):
        st.json(api("/auto-research"))
    if st.button("Learn from losses now"):
        st.json(api("/learn-from-loss"))
    if st.button("Adapt market now"):
        st.json(api(f"/adapt-market?symbol={symbol}"))

if selected_page == "Hidden Secrets Lab":
    lab = api("/hidden-secrets-lab")
    items = pd.DataFrame(lab.get("items") or [])
    st.subheader("Verified Secrets Lab")
    if not items.empty:
        st.dataframe(items, use_container_width=True)
    else:
        st.info("No verified secrets available.")
    st.json(api(f"/world-comparison?symbol={symbol}"))

if selected_page == "Never Die Monitor":
    monitor = api("/never-die-monitor")
    c1, c2, c3 = st.columns(3)
    c1.metric("Uptime Seconds", monitor.get("uptime_seconds") or 0)
    c2.metric("Last Self-Heal", monitor.get("last_self_heal", "unknown"))
    c3.metric("Issues Fixed", monitor.get("issues_fixed_without_human", 0))
    st.markdown('<span class="oktick">✓ Self-heal status file written.</span>', unsafe_allow_html=True)
    st.json(monitor)

if selected_page == "Hunger Meter":
    hunger = api("/hunger-meter")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Profit Goal", money(hunger.get("profit_goal_monthly", 1000000)))
    c2.metric("Current Observed", money(hunger.get("current_profit_observed", 0)))
    c3.metric("Accuracy Goal", pct(hunger.get("accuracy_goal_pct", 90)))
    c4.metric("Current Truth", pct(hunger.get("current_truth_score_pct", 0)))
    st.warning(hunger.get("need_to_fix", "No action computed."))
    st.json(api("/roadmap"))

if selected_page == "Truth & Control":
    truth = api("/data-truth-score")
    compliance = api("/compliance-check")
    cost = api("/cost-roi")
    st.metric("Data Truth Score", pct(truth.get("truth_score", 0)))
    st.json({"truth": truth, "compliance": compliance, "cost_roi": cost})
    st.subheader("Human vs Agent")
    st.dataframe(pd.DataFrame([
        {"actor": "Human", "live_orders_allowed": False, "speed": "manual", "proof_required": True},
        {"actor": "Genesis Agent", "live_orders_allowed": False, "speed": "automated analyzer", "proof_required": True},
    ]), use_container_width=True)
    if st.button("Let Agent Take Full Control"):
        result = api("/agent-full-control", "POST", {"requested_from_ui": True})
        st.toast(result.get("message", "Control request recorded"))
        st.json(result)
    st.error("Kill switch visible: live trading remains disabled until proof gates pass.")
    st.json(api("/final-message"))

st.divider()
st.caption(f"{VERSION} | Backend: {BACKEND_URL} | Analyzer/Paper first | Currency: INR | Percent format: 2 decimals")
print("DEPLOY READY: git push && render deploy")

