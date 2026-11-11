import re
from pathlib import Path

html_path = Path(r"C:\Genesis_System3_clean\content\app\templates\premium.html")
content = html_path.read_text(encoding="utf-8")

# 1. Update Tab 1 Chart Container to include interactive-candlestick-canvas and indicator buttons
tab1_old = '''          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div style="font-weight:bold; color:var(--text); font-size:12px;"><span id="inst-chart-header">RELIANCE 1M / 5M / 15M CANDLESTICK MATRIX & VOLATILITY CONTOUR</span></div>
            <div style="display:flex; gap:6px;">
              <button type="button" class="badge tf-btn" id="tf-btn-1m" onclick="setTimeframe('1M')" style="background:rgba(255,255,255,0.06); color:#aaa; font-size:10px; cursor:pointer; border:1px solid #333; border-radius:3px; padding:2px 8px;">1M</button>
              <button type="button" class="badge tf-btn active" id="tf-btn-5m" onclick="setTimeframe('5M')" style="background:rgba(0,255,136,0.2); color:var(--green); font-size:10px; cursor:pointer; border:1px solid var(--green); border-radius:3px; padding:2px 8px; font-weight:bold;">5M</button>
              <button type="button" class="badge tf-btn" id="tf-btn-15m" onclick="setTimeframe('15M')" style="background:rgba(255,255,255,0.06); color:#aaa; font-size:10px; cursor:pointer; border:1px solid #333; border-radius:3px; padding:2px 8px;">15M</button>
              <button type="button" class="badge tf-btn" id="tf-btn-1d" onclick="setTimeframe('1D')" style="background:rgba(255,255,255,0.06); color:#aaa; font-size:10px; cursor:pointer; border:1px solid #333; border-radius:3px; padding:2px 8px;">1D</button>
            </div>
          </div>
          <div style="height:220px; background:#080c14; border:1px solid rgba(255,255,255,0.06); border-radius:4px; padding:10px; position:relative; overflow:hidden;">
            <svg width="100%" height="100%" viewBox="0 0 700 200" preserveAspectRatio="none">'''

tab1_new = '''          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div style="font-weight:bold; color:var(--text); font-size:12px;"><span id="inst-chart-header">RELIANCE 1M / 5M / 15M CANDLESTICK MATRIX & VOLATILITY CONTOUR</span></div>
            <div style="display:flex; gap:6px; align-items:center;">
              <button type="button" class="badge tf-btn" id="tf-btn-1m" onclick="setTimeframe('1M')" style="background:rgba(255,255,255,0.06); color:#aaa; font-size:10px; cursor:pointer; border:1px solid #333; border-radius:3px; padding:2px 8px;">1M</button>
              <button type="button" class="badge tf-btn active" id="tf-btn-5m" onclick="setTimeframe('5M')" style="background:rgba(0,255,136,0.2); color:var(--green); font-size:10px; cursor:pointer; border:1px solid var(--green); border-radius:3px; padding:2px 8px; font-weight:bold;">5M</button>
              <button type="button" class="badge tf-btn" id="tf-btn-15m" onclick="setTimeframe('15M')" style="background:rgba(255,255,255,0.06); color:#aaa; font-size:10px; cursor:pointer; border:1px solid #333; border-radius:3px; padding:2px 8px;">15M</button>
              <button type="button" class="badge tf-btn" id="tf-btn-1d" onclick="setTimeframe('1D')" style="background:rgba(255,255,255,0.06); color:#aaa; font-size:10px; cursor:pointer; border:1px solid #333; border-radius:3px; padding:2px 8px;">1D</button>
              <span style="border-left:1px solid #333; height:14px; margin:0 4px;"></span>
              <button type="button" class="badge ind-btn active" id="ind-btn-vol" onclick="toggleIndicator('vol')" style="background:rgba(0,255,136,0.15); color:var(--green); font-size:10px; cursor:pointer; border:1px solid var(--green); border-radius:3px; padding:2px 8px; font-weight:bold;">VOL</button>
              <button type="button" class="badge ind-btn active" id="ind-btn-ema" onclick="toggleIndicator('ema')" style="background:rgba(255,204,0,0.15); color:var(--gold); font-size:10px; cursor:pointer; border:1px solid var(--gold); border-radius:3px; padding:2px 8px; font-weight:bold;">EMA 20</button>
              <button type="button" class="badge ind-btn active" id="ind-btn-vwap" onclick="toggleIndicator('vwap')" style="background:rgba(0,229,255,0.15); color:var(--cyan); font-size:10px; cursor:pointer; border:1px solid var(--cyan); border-radius:3px; padding:2px 8px; font-weight:bold;">VWAP</button>
            </div>
          </div>
          <div style="height:220px; background:#080c14; border:1px solid rgba(255,255,255,0.06); border-radius:4px; padding:4px; position:relative; overflow:hidden;">
            <canvas id="interactive-candlestick-canvas" style="width:100%; height:100%; display:block;"></canvas>
            <div style="position:absolute; bottom:6px; left:10px; font-size:10px; color:#888; background:rgba(0,0,0,0.6); padding:2px 6px; border-radius:3px;" id="chart-ohlc-banner">
              WebGL 60FPS Hardware Accelerated · Open: ₹1,298.00 · High: ₹1,304.50 · Low: ₹1,295.00 · Close: ₹1,300.00 (+1.21%)
            </div>
          </div>
          <div style="display:none;">
            <svg width="100%" height="100%" viewBox="0 0 700 200" preserveAspectRatio="none">'''

if tab1_old in content:
    content = content.replace(tab1_old, tab1_new)
    print("1. Updated Tab 1 Chart Container with Canvas and Indicator toggles")
else:
    print("Could not match tab1_old exactly")

# 2. Update Options Intelligence Card with IDs
opt_old = '''      <!-- Options Intelligence -->
      <div class="card">
        <div class="card-header">
          <div class="card-title" id="options-intel-card-title">Options Intelligence - RELIANCE</div>
          <span style="font-size:10px; color:var(--cyan);">27-Nov-2026</span>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:8px;">
          <div style="background:#161616; padding:6px; border-radius:4px; text-align:center;">
            <div style="color:var(--text-muted); font-size:9.5px;">PCR</div>
            <div style="font-size:16px; font-weight:800; color:var(--gold);">0.92</div>
          </div>
          <div style="background:#161616; padding:6px; border-radius:4px; text-align:center;">
            <div style="color:var(--text-muted); font-size:9.5px;">IV / IV Rank</div>
            <div style="font-size:16px; font-weight:800; color:var(--green);">24.8%</div>
          </div>
        </div>
        <div class="kv-row"><span>Delta (Δ)</span><span class="up">0.54</span></div>
        <div class="kv-row"><span>Gamma (Γ)</span><span class="up">0.08</span></div>
        <div class="kv-row"><span>Theta (Θ)</span><span class="dn">-2.31</span></div>
        <div class="kv-row"><span>Vega (𝒱)</span><span>12.46</span></div>
        <div class="kv-row"><span>Max Pain Strike</span><span style="color:var(--gold);">₹1,300.00</span></div>
        <div class="kv-row"><span>OI Change %</span><span class="up">+8.24%</span></div>
      </div>'''

opt_new = '''      <!-- Options Intelligence -->
      <div class="card">
        <div class="card-header">
          <div class="card-title" id="options-intel-card-title">Options Intelligence - RELIANCE</div>
          <span style="font-size:10px; color:var(--cyan);" id="options-intel-expiry">27-Nov-2026</span>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:8px;">
          <div style="background:#161616; padding:6px; border-radius:4px; text-align:center;">
            <div style="color:var(--text-muted); font-size:9.5px;">PCR</div>
            <div style="font-size:16px; font-weight:800; color:var(--gold);" id="opt-pcr-val">0.92</div>
          </div>
          <div style="background:#161616; padding:6px; border-radius:4px; text-align:center;">
            <div style="color:var(--text-muted); font-size:9.5px;">IV / IV Rank</div>
            <div style="font-size:16px; font-weight:800; color:var(--green);" id="opt-iv-val">22.0%</div>
          </div>
        </div>
        <div class="kv-row"><span>Delta (Δ)</span><span class="up" id="opt-delta-val">0.521</span></div>
        <div class="kv-row"><span>Gamma (Γ)</span><span class="up" id="opt-gamma-val">0.0101</span></div>
        <div class="kv-row"><span>Theta (Θ)</span><span class="dn" id="opt-theta-val">-1.24</span></div>
        <div class="kv-row"><span>Vega (𝒱)</span><span id="opt-vega-val">0.72</span></div>
        <div class="kv-row"><span>Max Pain Strike</span><span style="color:var(--gold);" id="opt-maxpain-val">₹1,300.00</span></div>
        <div class="kv-row"><span>OI Change %</span><span class="up" id="opt-oichg-val">+8.24%</span></div>
      </div>'''

if opt_old in content:
    content = content.replace(opt_old, opt_new)
    print("2. Updated Options Intelligence Card with dynamic IDs")
else:
    print("Could not match opt_old exactly")

# 3. Update Tab 3 Quantitative Model Visual Feature Weights Chart
tab3_old = '''        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-family:monospace; font-size:11.5px;">
          <div style="background:#05090f; padding:10px; border-radius:4px; border:1px solid #1f2937;">
            <div style="color:#888; font-size:10px; margin-bottom:4px;">ALPHA VECTOR / FACTOR WEIGHT MATRIX</div>
            <div style="color:var(--green); font-weight:bold; margin-bottom:6px;" id="reason-alpha-vector">Order-Flow Imbalance + Institutional Block Accumulation (OFI Delta: +68.4%)</div>
            <div style="color:#bbb; line-height:1.4;" id="reason-desc">Cross-Asset basis spread expanded +18.4 bps before morning discovery. Aggressive block trades detected at ₹1,295 - ₹1,300 with zero sell-side iceberg replenishment.</div>
          </div>
          <div style="background:#05090f; padding:10px; border-radius:4px; border:1px solid #1f2937;">
            <div style="color:#888; font-size:10px; margin-bottom:4px;">MICRO-REASONING EVIDENCE & RISK ENVELOPE</div>
            <div style="color:var(--gold); font-weight:bold; margin-bottom:6px;" id="reason-oi-iv">+8.7% Call OI Expansion paired with IV co-integration (IV: 27.04%)</div>
            <div style="color:#bbb; line-height:1.4;" id="reason-risk">FII Net Long drift confirmed. Dynamic VaR 95% stop-loss threshold: <strong style="color:#00ff88;" id="reason-stoploss">₹1,274.50</strong> | Intraday Target: <strong style="color:var(--gold);" id="reason-target">₹1,328.00</strong> | Expected Sharpe: <strong style="color:#00e5ff;" id="reason-sharpe">2.84</strong></div>
          </div>
        </div>'''

tab3_new = '''        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-family:monospace; font-size:11.5px;">
          <!-- Left: Quantitative Alpha Factor Weight Matrix Bar Chart -->
          <div style="background:#05090f; padding:12px; border-radius:4px; border:1px solid #1f2937;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
              <span style="color:#888; font-size:10px; font-weight:bold; letter-spacing:0.5px;">QUANTITATIVE ALPHA FACTOR WEIGHT MATRIX</span>
              <span style="color:var(--green); font-size:10px;" id="feature-calibration-score">CALIBRATION: 0.94 (NO DRIFT)</span>
            </div>
            
            <div style="display:flex; flex-direction:column; gap:8px;">
              <div>
                <div style="display:flex; justify-content:space-between; font-size:10.5px; margin-bottom:2px;">
                  <span>1. Momentum & RSI Velocity (14D)</span>
                  <strong style="color:var(--green);" id="feat-wt-1">28% (Bullish +1.42σ)</strong>
                </div>
                <div style="background:#111827; border-radius:2px; height:6px; overflow:hidden;">
                  <div id="feat-bar-1" style="background:#00ff88; width:88%; height:100%; transition:width 0.4s;"></div>
                </div>
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; font-size:10.5px; margin-bottom:2px;">
                  <span>2. Institutional PE/CE OI Shifts</span>
                  <strong style="color:var(--gold);" id="feat-wt-2">24% (OFI Delta +68.4%)</strong>
                </div>
                <div style="background:#111827; border-radius:2px; height:6px; overflow:hidden;">
                  <div id="feat-bar-2" style="background:#ffcc00; width:82%; height:100%; transition:width 0.4s;"></div>
                </div>
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; font-size:10.5px; margin-bottom:2px;">
                  <span>3. Volatility Smile & IV Skew</span>
                  <strong style="color:var(--cyan);" id="feat-wt-3">20% (IV: 22.0% / Co-integrated)</strong>
                </div>
                <div style="background:#111827; border-radius:2px; height:6px; overflow:hidden;">
                  <div id="feat-bar-3" style="background:#00e5ff; width:74%; height:100%; transition:width 0.4s;"></div>
                </div>
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; font-size:10.5px; margin-bottom:2px;">
                  <span>4. Realized Volume Trend & Iceberg Exhaustion</span>
                  <strong style="color:#a78bfa;" id="feat-wt-4">16% (Volume +34.2%)</strong>
                </div>
                <div style="background:#111827; border-radius:2px; height:6px; overflow:hidden;">
                  <div id="feat-bar-4" style="background:#a78bfa; width:65%; height:100%; transition:width 0.4s;"></div>
                </div>
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; font-size:10.5px; margin-bottom:2px;">
                  <span>5. Cross-Asset Sector Beta Covariance</span>
                  <strong style="color:#f472b6;" id="feat-wt-5">12% (Beta: 1.14 / Sector: Bullish)</strong>
                </div>
                <div style="background:#111827; border-radius:2px; height:6px; overflow:hidden;">
                  <div id="feat-bar-5" style="background:#f472b6; width:58%; height:100%; transition:width 0.4s;"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right: Quantitative Decision Tree & Risk Envelope -->
          <div style="background:#05090f; padding:12px; border-radius:4px; border:1px solid #1f2937; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="color:#888; font-size:10px; font-weight:bold; letter-spacing:0.5px;">QUANTITATIVE DECISION TREE OUTCOME</span>
                <span class="badge" style="background:rgba(0,255,136,0.15); color:var(--green); font-size:10px; padding:2px 6px;" id="reason-signal-badge">SIGNAL: BULLISH ACCUMULATION</span>
              </div>
              <div style="color:var(--green); font-weight:bold; font-size:12px; margin-bottom:6px;" id="reason-alpha-vector">Order-Flow Imbalance + Institutional Block Accumulation (OFI Delta: +68.4%)</div>
              <div style="color:#bbb; line-height:1.45; font-size:11px; margin-bottom:8px;" id="reason-desc">Cross-Asset basis spread expanded +18.4 bps before morning discovery. Aggressive block trades detected at ₹1,295 - ₹1,300 with zero sell-side iceberg replenishment.</div>
            </div>
            
            <div style="background:#090e17; border:1px solid #1f2937; border-radius:4px; padding:8px;">
              <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:8px; text-align:center;">
                <div>
                  <div style="color:#888; font-size:9.5px;">ENTRY ZONE</div>
                  <strong style="color:#fff; font-size:11.5px;" id="reason-entry">₹1,298.50</strong>
                </div>
                <div>
                  <div style="color:#888; font-size:9.5px;">STOP-LOSS</div>
                  <strong style="color:#ff4444; font-size:11.5px;" id="reason-stoploss">₹1,274.50</strong>
                </div>
                <div>
                  <div style="color:#888; font-size:9.5px;">TARGET (1:2.8)</div>
                  <strong style="color:var(--gold); font-size:11.5px;" id="reason-target">₹1,328.00</strong>
                </div>
                <div>
                  <div style="color:#888; font-size:9.5px;">EXP. SHARPE</div>
                  <strong style="color:var(--cyan); font-size:11.5px;" id="reason-sharpe">2.84</strong>
                </div>
              </div>
            </div>
          </div>
        </div>'''

if tab3_old in content:
    content = content.replace(tab3_old, tab3_new)
    print("3. Updated Tab 3 with Visual Feature Weights Bar Chart & Decision Tree")
else:
    print("Could not match tab3_old exactly")

html_path.write_text(content, encoding="utf-8")
print("Saved premium.html updates successfully!")
