import re
from pathlib import Path

html_path = Path(r"C:\Genesis_System3_clean\content\app\templates\premium.html")
content = html_path.read_text(encoding="utf-8")

# Define replacement for renderCandlestickChart & related JS
candlestick_code = '''
    // Interactive HTML5 Candlestick Chart Renderer with Technical Overlays
    let showIndicators = { vol: true, ema: true, vwap: true };

    function toggleIndicator(ind) {
      if (showIndicators.hasOwnProperty(ind)) {
        showIndicators[ind] = !showIndicators[ind];
        const btn = document.getElementById("ind-btn-" + ind);
        if (btn) {
          if (showIndicators[ind]) {
            btn.style.opacity = "1";
            btn.style.fontWeight = "bold";
          } else {
            btn.style.opacity = "0.4";
            btn.style.fontWeight = "normal";
          }
        }
        renderCandlestickChart();
      }
    }

    function renderCandlestickChart() {
      const canvas = document.getElementById("interactive-candlestick-canvas");
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * (window.devicePixelRatio || 1);
      canvas.height = rect.height * (window.devicePixelRatio || 1);
      const ctx = canvas.getContext("2d");
      ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);

      const w = rect.width;
      const h = rect.height;
      ctx.clearRect(0, 0, w, h);

      // Grid lines
      ctx.strokeStyle = "#151b24";
      ctx.lineWidth = 1;
      for (let y = 30; y < h - 20; y += 35) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      // Base price for current symbol
      const sym = (typeof currentSelectedSymbol === "string" && currentSelectedSymbol) ? currentSelectedSymbol : "RELIANCE";
      let base = 1300.0;
      if (sym === "NIFTY") base = 23960.60;
      else if (sym === "BANKNIFTY") base = 55913.60;
      else if (sym === "SENSEX") base = 77301.40;

      const numCandles = Math.min(36, Math.floor(w / 18));
      const candleWidth = Math.max(6, Math.floor(w / (numCandles * 2.2)));
      const spacing = w / (numCandles + 1);

      // Seed deterministic candle sequence
      let current = base * (currentTimeframe === "1M" ? 0.994 : currentTimeframe === "5M" ? 0.990 : 0.982);
      const candles = [];
      let cumVol = 0;
      let cumPriceVol = 0;

      for (let i = 0; i < numCandles; i++) {
        const trend = (i / numCandles) * 0.012;
        const noise = (Math.sin(i * 1.6) * 0.0035);
        const open = current;
        const close = open * (1.0 + trend + noise);
        const high = Math.max(open, close) * (1.0 + Math.abs(noise * 0.7) + 0.0018);
        const low = Math.min(open, close) * (1.0 - Math.abs(noise * 0.7) - 0.0018);
        const vol = Math.floor(15000 + Math.abs(Math.sin(i * 2.1)) * 45000);
        
        cumVol += vol;
        cumPriceVol += ((open + high + low + close) / 4) * vol;
        const vwapVal = cumPriceVol / cumVol;

        candles.push({ open, close, high, low, vol, vwap: vwapVal });
        current = close;
      }

      // Calculate 20-period EMA
      const emaPeriod = Math.min(20, candles.length);
      const k = 2 / (emaPeriod + 1);
      let emaCurrent = candles[0].close;
      candles.forEach((c, idx) => {
        if (idx === 0) {
          c.ema = emaCurrent;
        } else {
          emaCurrent = (c.close * k) + (emaCurrent * (1 - k));
          c.ema = emaCurrent;
        }
      });

      const allPrices = candles.flatMap(c => [c.high, c.low]);
      const minP = Math.min(...allPrices);
      const maxP = Math.max(...allPrices);
      const range = (maxP - minP) || 1;

      // Vertical price-to-Y mapping (top 75% for candles, bottom 25% for volume)
      const chartTop = 25;
      const chartBottom = h - 35;
      const getY = p => chartBottom - ((p - minP) / range) * (chartBottom - chartTop);

      // 1. Draw Volume Bars if enabled
      if (showIndicators.vol) {
        const maxVol = Math.max(...candles.map(c => c.vol)) || 1;
        const volHeightMax = h * 0.22;
        candles.forEach((c, idx) => {
          const x = (idx + 1) * spacing;
          const vH = (c.vol / maxVol) * volHeightMax;
          const isGreen = c.close >= c.open;
          ctx.fillStyle = isGreen ? "rgba(0, 255, 136, 0.25)" : "rgba(255, 68, 68, 0.25)";
          ctx.fillRect(x - candleWidth / 2, h - vH - 18, candleWidth, vH);
        });
      }

      // 2. Draw Candlesticks
      candles.forEach((c, idx) => {
        const x = (idx + 1) * spacing;
        const isGreen = c.close >= c.open;
        const color = isGreen ? "#00ff88" : "#ff4444";

        // Wick
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.4;
        ctx.beginPath();
        ctx.moveTo(x, getY(c.high));
        ctx.lineTo(x, getY(c.low));
        ctx.stroke();

        // Body
        const topY = getY(Math.max(c.open, c.close));
        const bottomY = getY(Math.min(c.open, c.close));
        const bodyH = Math.max(2, bottomY - topY);

        ctx.fillStyle = color;
        ctx.fillRect(x - candleWidth / 2, topY, candleWidth, bodyH);
      });

      // 3. Draw EMA 20 line if enabled
      if (showIndicators.ema && candles.length > 1) {
        ctx.strokeStyle = "#ffcc00";
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        candles.forEach((c, idx) => {
          const x = (idx + 1) * spacing;
          const y = getY(c.ema);
          if (idx === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.stroke();
      }

      // 4. Draw VWAP line if enabled
      if (showIndicators.vwap && candles.length > 1) {
        ctx.strokeStyle = "#00e5ff";
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        candles.forEach((c, idx) => {
          const x = (idx + 1) * spacing;
          const y = getY(c.vwap);
          if (idx === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.stroke();
      }

      // Legend overlay
      const last = candles[candles.length - 1];
      ctx.font = "10px monospace";
      let legendX = 10;
      if (showIndicators.ema) {
        ctx.fillStyle = "#ffcc00";
        ctx.fillText(`EMA(20): ₹${last.ema.toFixed(2)}`, legendX, 16);
        legendX += 130;
      }
      if (showIndicators.vwap) {
        ctx.fillStyle = "#00e5ff";
        ctx.fillText(`VWAP: ₹${last.vwap.toFixed(2)}`, legendX, 16);
        legendX += 120;
      }
      if (showIndicators.vol) {
        ctx.fillStyle = "#888";
        ctx.fillText(`VOL: ${(last.vol / 1000).toFixed(1)}k`, legendX, 16);
      }

      // Update OHLC banner
      const chgPct = ((last.close / candles[0].open - 1.0) * 100);
      const banner = document.getElementById("chart-ohlc-banner");
      if (banner) {
        banner.innerHTML = `<b>${sym} (${currentTimeframe})</b> · Open: ₹${last.open.toFixed(2)} · High: ₹${last.high.toFixed(2)} · Low: ₹${last.low.toFixed(2)} · Close: ₹${last.close.toFixed(2)} <span style="color:${chgPct >= 0 ? '#00ff88' : '#ff4444'}; font-weight:bold;">(${chgPct >= 0 ? '+' : ''}${chgPct.toFixed(2)}%)</span>`;
      }
    }
'''

# Replace renderCandlestickChart
pattern_chart = re.compile(r'// Interactive HTML5 Candlestick Chart Renderer\s+function renderCandlestickChart\(\) \{.*?function setTimeframe\(tf\) \{', re.DOTALL)
m_chart = pattern_chart.search(content)
if m_chart:
    print("Found renderCandlestickChart! Replacing...")
    content = content[:m_chart.start()] + candlestick_code.strip() + "\n\n    function setTimeframe(tf) {" + content[m_chart.end():]
    print("Replaced chart renderer with EMA/VWAP/VOL overlays")
else:
    print("Could not find renderCandlestickChart block via regex")

# Add loadOptionsIntelligence & update selectSymbol & onReasoningSymbolChange
options_intelligence_js = '''
    // UI-01: Dynamic Options Greeks & Intelligence Loader
    async function loadOptionsIntelligence(sym, strike, optType) {
      const s = (sym || currentSelectedSymbol || "RELIANCE").toUpperCase();
      const stk = strike || 0;
      const ot = optType || "CE";
      try {
        const resp = await fetch(`/api/options/intelligence?symbol=${s}&strike=${stk}&option_type=${ot}`);
        if (!resp || !resp.ok) return;
        const resJson = await resp.json();
        const data = resJson.data || resJson;
        
        // Update Title
        const titleEl = document.getElementById("options-intel-card-title");
        if (titleEl) {
          titleEl.textContent = `Options Intelligence - ${s} ${stk ? stk + ' ' + ot : ''}`;
        }
        
        // Update PCR & IV
        const pcrEl = document.getElementById("opt-pcr-val");
        if (pcrEl && data.pcr !== undefined) pcrEl.textContent = Number(data.pcr).toFixed(2);
        
        const ivEl = document.getElementById("opt-iv-val");
        if (ivEl && data.iv !== undefined) ivEl.textContent = Number(data.iv).toFixed(1) + "%";
        
        // Update Greeks
        const g = data.greeks || {};
        const deltaEl = document.getElementById("opt-delta-val");
        if (deltaEl && g.delta !== undefined) {
          deltaEl.textContent = (g.delta >= 0 ? '+' : '') + Number(g.delta).toFixed(3);
          deltaEl.className = g.delta >= 0 ? "up" : "dn";
        }
        
        const gammaEl = document.getElementById("opt-gamma-val");
        if (gammaEl && g.gamma !== undefined) gammaEl.textContent = Number(g.gamma).toFixed(4);
        
        const thetaEl = document.getElementById("opt-theta-val");
        if (thetaEl && g.theta !== undefined) {
          thetaEl.textContent = Number(g.theta).toFixed(2);
          thetaEl.className = g.theta >= 0 ? "up" : "dn";
        }
        
        const vegaEl = document.getElementById("opt-vega-val");
        if (vegaEl && g.vega !== undefined) vegaEl.textContent = Number(g.vega).toFixed(2);
        
        const maxPainEl = document.getElementById("opt-maxpain-val");
        if (maxPainEl && data.max_pain !== undefined) {
          maxPainEl.textContent = "₹" + Number(data.max_pain).toLocaleString('en-IN', {minimumFractionDigits:2});
        }
        
        const oiChgEl = document.getElementById("opt-oichg-val");
        if (oiChgEl && data.oi_change_pct !== undefined) {
          oiChgEl.textContent = (data.oi_change_pct >= 0 ? '+' : '') + Number(data.oi_change_pct).toFixed(2) + "%";
          oiChgEl.className = data.oi_change_pct >= 0 ? "up" : "dn";
        }
      } catch (err) {
        console.warn("loadOptionsIntelligence error:", err);
      }
    }

    function selectOptionStrike(sym, strike, optType) {
      loadOptionsIntelligence(sym, strike, optType);
    }
'''

# Inject loadOptionsIntelligence before selectSymbol
if "function selectSymbol(sym)" in content and "loadOptionsIntelligence" not in content:
    content = content.replace("function selectSymbol(sym) {", options_intelligence_js + "\n    function selectSymbol(sym) {")
    print("Injected loadOptionsIntelligence and selectOptionStrike")

# Update selectSymbol to call loadOptionsIntelligence and renderCandlestickChart
old_select_symbol = '''      const optTitle = document.getElementById("options-intel-card-title");
      if (optTitle) optTitle.textContent = `Options Intelligence - ${currentSelectedSymbol}`;
      // Update L2 Book data
      loadOrderBook();'''

new_select_symbol = '''      const optTitle = document.getElementById("options-intel-card-title");
      if (optTitle) optTitle.textContent = `Options Intelligence - ${currentSelectedSymbol}`;
      // Update L2 Book data & Dynamic Greeks
      loadOrderBook();
      loadOptionsIntelligence(currentSelectedSymbol);
      renderCandlestickChart();'''

if old_select_symbol in content:
    content = content.replace(old_select_symbol, new_select_symbol)
    print("Updated selectSymbol to call loadOptionsIntelligence and renderCandlestickChart")

# Update onReasoningSymbolChange for UI-03 visual bar chart customization
reasoning_fn_old = '''    function onReasoningSymbolChange(sym) {
      const info = SYMBOL_REASONING[sym] || SYMBOL_REASONING["RELIANCE"];
      const v = document.getElementById("reason-alpha-vector");
      if (v) v.textContent = info.alpha;
      const d = document.getElementById("reason-desc");
      if (d) d.textContent = info.desc;
      const oi = document.getElementById("reason-oi-iv");
      if (oi) oi.textContent = info.oi;
      const sl = document.getElementById("reason-stoploss");
      if (sl) sl.textContent = info.stoploss;'''

reasoning_fn_new = '''    function onReasoningSymbolChange(sym) {
      const s = (sym || "RELIANCE").toUpperCase();
      const info = SYMBOL_REASONING[s] || SYMBOL_REASONING["RELIANCE"];
      const v = document.getElementById("reason-alpha-vector");
      if (v) v.textContent = info.alpha;
      const d = document.getElementById("reason-desc");
      if (d) d.textContent = info.desc;
      const oi = document.getElementById("reason-oi-iv");
      if (oi) oi.textContent = info.oi;
      const sl = document.getElementById("reason-stoploss");
      if (sl) sl.textContent = info.stoploss;
      const tgt = document.getElementById("reason-target");
      if (tgt) tgt.textContent = info.target;
      const sh = document.getElementById("reason-sharpe");
      if (sh) sh.textContent = info.sharpe;
      const badge = document.getElementById("reason-signal-badge");
      if (badge) badge.textContent = `SIGNAL: ${info.score} CONFIDENCE`;

      // Update Visual Feature Weights Bars per Asset
      const weights = {
        "RELIANCE": [ {w:"28%", txt:"28% (Bullish +1.42σ)", bar:"88%"}, {w:"24%", txt:"24% (OFI Delta +68.4%)", bar:"82%"}, {w:"20%", txt:"20% (IV: 22.0% Co-int)", bar:"74%"}, {w:"16%", txt:"16% (Volume +34.2%)", bar:"65%"}, {w:"12%", txt:"12% (Beta: 1.14)", bar:"58%"} ],
        "NIFTY": [ {w:"30%", txt:"30% (Breadth +1.68σ)", bar:"92%"}, {w:"26%", txt:"26% (PCR 1.60 Sweep)", bar:"85%"}, {w:"18%", txt:"18% (IV: 13.8% Low)", bar:"70%"}, {w:"14%", txt:"14% (Volume Basket +42%)", bar:"62%"}, {w:"12%", txt:"12% (Macro Adv: 54%)", bar:"55%"} ],
        "BANKNIFTY": [ {w:"29%", txt:"29% (Banking Momentum)", bar:"89%"}, {w:"25%", txt:"25% (54,800 PE Floor)", bar:"84%"}, {w:"21%", txt:"21% (IV: 16.4%)", bar:"76%"}, {w:"15%", txt:"15% (HDFC+ICICI Volume)", bar:"64%"}, {w:"10%", txt:"10% (Beta: 1.32)", bar:"52%"} ],
        "TCS": [ {w:"27%", txt:"27% (Mean-Reversion)", bar:"80%"}, {w:"24%", txt:"24% (Call Accumulation)", bar:"78%"}, {w:"22%", txt:"22% (IV Contracting)", bar:"72%"}, {w:"15%", txt:"15% (Foreign Flow +18%)", bar:"60%"}, {w:"12%", txt:"12% (USD/INR Hedge)", bar:"50%"} ],
        "INFY": [ {w:"26%", txt:"26% (Lower Channel Bounce)", bar:"78%"}, {w:"25%", txt:"25% (1540 Call Buildup)", bar:"76%"}, {w:"21%", txt:"21% (Dark Pool Volume)", bar:"70%"}, {w:"16%", txt:"16% (Tech Sector Inflow)", bar:"62%"}, {w:"12%", txt:"12% (Beta: 0.98)", bar:"48%"} ]
      };
      const wList = weights[s] || weights["RELIANCE"];
      for (let i = 1; i <= 5; i++) {
        const wtEl = document.getElementById("feat-wt-" + i);
        const barEl = document.getElementById("feat-bar-" + i);
        if (wtEl && wList[i-1]) wtEl.textContent = wList[i-1].txt;
        if (barEl && wList[i-1]) barEl.style.width = wList[i-1].bar;
      }'''

if reasoning_fn_old in content:
    content = content.replace(reasoning_fn_old, reasoning_fn_new)
    print("Updated onReasoningSymbolChange to dynamically animate feature weights bars")
else:
    print("Could not match reasoning_fn_old exactly")

html_path.write_text(content, encoding="utf-8")
print("Saved all premium.html JavaScript enhancements successfully!")
