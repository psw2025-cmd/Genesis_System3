from pathlib import Path
from datetime import datetime,timezone
import shutil, ast
root=Path(r"C:\content\app")
app=root/"app.py"; ui=root/"templates"/"premium.html"
a=app.read_text(encoding="utf-8");h=ui.read_text(encoding="utf-8")
if "S3_VERIFIED_GATE_V2" in a or "id=\"verified-gate-v2\"" in h:
    raise SystemExit("Already installed: no changes")
if not (root/"verified_market.py").is_file():raise SystemExit("Verified market adapter missing")
ast.parse(a)
if not h.rstrip().endswith("</html>"):raise SystemExit("Unexpected dashboard markup")
newa=a+"\n\n# S3_VERIFIED_GATE_V2 — authenticated read-only market data, never broker orders.\nfrom verified_market import router as _verified_market_router\napp.include_router(_verified_market_router)\n"
ast.parse(newa)
panel=""" 
<style>
body:not(.truth-demo) .ticker-overview-bar,body:not(.truth-demo) .command-grid{display:none!important}
#verified-gate-v2{background:#080f12;border:1px solid #3c5360;border-radius:10px;margin:16px;padding:20px;color:#e4f2f7;font:13px/1.5 system-ui,sans-serif}
#verified-gate-v2 h2{color:#ffcf39;margin:0 0 7px;font-size:18px}
#verified-gate-v2 .vmeta{color:#a6b9c4;margin:6px 0 14px}
#verified-gate-v2 .vgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:11px}
#verified-gate-v2 .vcard{border:1px solid #234656;background:#0c1b22;border-radius:8px;padding:13px;min-height:98px}
#verified-gate-v2 .vlabel{font-size:11px;color:#a9c3ce}
#verified-gate-v2 .vvalue{font-size:23px;font-weight:750;margin:6px 0;color:#f3f7f9}
#verified-gate-v2 .vnote{font-size:11px;color:#e6b76c}
#verified-gate-v2 button{cursor:pointer;padding:8px 12px;color:#ffcf6a;background:#192129;border:1px solid #94672b;border-radius:6px}
#verified-gate-v2 a{color:#8ad7fa}
</style>
<section id="verified-gate-v2" aria-label="Verified exchange data dashboard">
  <h2>VERIFIED MARKET SOURCE — READ-ONLY</h2>
  <p class="vmeta" id="vm-state">Checking authenticated data provider. Unverified prices are hidden.</p>
  <div class="vgrid">
    <div class="vcard"><div class="vlabel">NIFTY 50 · NSE</div><div class="vvalue" id="vm-nifty">—</div><div class="vnote" id="vm-nifty-note">Awaiting verified tick</div></div>
    <div class="vcard"><div class="vlabel">NIFTY BANK · NSE</div><div class="vvalue" id="vm-bank">—</div><div class="vnote" id="vm-bank-note">Awaiting verified tick</div></div>
    <div class="vcard"><div class="vlabel">SENSEX · BSE</div><div class="vvalue" id="vm-sensex">—</div><div class="vnote" id="vm-sensex-note">Awaiting verified tick</div></div>
    <div class="vcard"><div class="vlabel">Provider symbol master</div><div class="vvalue" id="vm-master">—</div><div class="vnote">Listed in Dhan master; not equivalent to subscribed live feed</div></div>
  </div>
  <p class="vmeta" id="vm-provenance">Prices only appear when authenticated Dhan quotes include credible original last-trade timestamps. Never use random-walk or hardcoded values as live.</p>
  <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
    <button id="vm-demo" type="button">Show SIMULATED dashboard preview</button>
    <a href="https://www.nseindia.com/market-data/live-market-indices" target="_blank" rel="noopener">Official NSE</a>
    <a href="https://www.bseindia.com/" target="_blank" rel="noopener">Official BSE</a>
    <a href="https://dhanhq.co/docs/v2/market-quote/" target="_blank" rel="noopener">Dhan quote documentation</a>
  </div>
</section>
<script>
(function(){
  "use strict";
  var entries=[["NIFTY","vm-nifty","vm-nifty-note"],["BANKNIFTY","vm-bank","vm-bank-note"],["SENSEX","vm-sensex","vm-sensex-note"]];
  function put(id,value){var el=document.getElementById(id);if(el)el.textContent=String(value);}
  async function load(){
    try{
      var response=await fetch("/api/verified-market",{cache:"no-store"});
      if(!response.ok)throw Error("Source status unavailable: HTTP "+response.status);
      var d=await response.json();
      var meta=d.instrument_master||{};
      put("vm-master",typeof meta.rows==="number"?meta.rows.toLocaleString("en-IN"):"—");
      put("vm-state","Provider: Dhan marketfeed/quote | Session: "+d.market_session+" | Status: "+d.state);
      put("vm-provenance",d.reason+" | Checked UTC: "+d.checked_at_utc+" | Prices without valid exchange timestamps stay hidden.");
      entries.forEach(function(entry){
        var q=(d.quotes||{})[entry[0]];
        if(q && typeof q.price==="number" && q.price>0 && q.last_trade_ist){
          put(entry[1],"₹"+q.price.toLocaleString("en-IN",{maximumFractionDigits:2,minimumFractionDigits:2}));
          put(entry[2],q.status+" | last trade "+q.last_trade_ist);
        }else{
          put(entry[1],"—");
          put(entry[2],q?(q.status||"UNVERIFIED"):"NO VERIFIED BROKER QUOTE");
        }
      });
    }catch(err){put("vm-state","SOURCE UNAVAILABLE — no verified prices");put("vm-provenance","Read-only source check failed; simulated prices remain hidden.");}
  }
  document.getElementById("vm-demo").addEventListener("click",function(){
    var active=document.body.classList.toggle("truth-demo");
    this.textContent=active?"Hide SIMULATED preview — return to verified data":"Show SIMULATED dashboard preview";
  });
  load();setInterval(load,30000);
})();
</script>
"""
newh=h.replace("</body>",panel+"\n</body>",1)
if newh==h:raise SystemExit("No closing body tag")
stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
bk=root/"truth_backups"/("verified_gate_"+stamp)
bk.mkdir(parents=True,exist_ok=False)
shutil.copy2(app,bk/"app.py");shutil.copy2(ui,bk/"premium.html")
app.write_text(newa,encoding="utf-8")
ui.write_text(newh,encoding="utf-8")
print("VERIFIED_GATE_INSTALLED",stamp,"BACKUP",bk)
print("PENDING_ISOLATED_API_UI_TESTS_AND_SERVER_RESTART")
