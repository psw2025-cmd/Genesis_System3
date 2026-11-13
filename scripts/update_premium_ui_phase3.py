import re

path = r"C:\Genesis_System3_clean\content\app\templates\premium.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add connection banner after </header> if not present
banner_html = '''
  <!-- DYNAMIC CONNECTION LOST BANNER -->
  <div id="connection-lost-banner" style="display:none; background:#d32f2f; color:#ffffff; font-weight:bold; text-align:center; padding:10px 16px; font-size:13px; letter-spacing:0.5px; border-bottom:2px solid #b71c1c; box-shadow:0 4px 12px rgba(211,47,47,0.5); z-index:9999;">
    ⚠️ CONNECTION LOST: BACKEND OR DHAN BROKER UNREACHABLE — LIVE DATA STREAM HALTED
  </div>
'''

if 'id="connection-lost-banner"' not in content:
    content = content.replace("</header>", "</header>" + banner_html, 1)

# 2. Replace hardcoded ticker values
content = re.sub(r'<span class="t-price" id="t-nifty-val">[^<]+</span>', '<span class="t-price" id="t-nifty-val">—</span>', content)
content = re.sub(r'<span class="up" id="t-nifty-chg">[^<]+</span>', '<span class="up" id="t-nifty-chg">—</span>', content)
content = re.sub(r'<span class="t-price" id="t-bank-val">[^<]+</span>', '<span class="t-price" id="t-bank-val">—</span>', content)
content = re.sub(r'<span class="up" id="t-bank-chg">[^<]+</span>', '<span class="up" id="t-bank-chg">—</span>', content)
content = re.sub(r'<span class="t-price" id="t-sensex-val">[^<]+</span>', '<span class="t-price" id="t-sensex-val">—</span>', content)
content = re.sub(r'<span class="up" id="t-sensex-chg">[^<]+</span>', '<span class="up" id="t-sensex-chg">—</span>', content)
content = re.sub(r'<span class="t-price" id="t-reliance-val">[^<]+</span>', '<span class="t-price" id="t-reliance-val">—</span>', content)
content = re.sub(r'<span class="up" id="t-reliance-chg">[^<]+</span>', '<span class="up" id="t-reliance-chg">—</span>', content)

# 3. Replace institutional strip hardcoded values
content = re.sub(
    r'<div><span style="color:#888;">NIFTY 50:</span> <strong style="color:var\(--gold\);">[^<]+</strong> <span style="color:var\(--green\); font-weight:bold;">[^<]+</span></div>',
    '<div><span style="color:#888;">NIFTY 50:</span> <strong id="inst-nifty-val" style="color:var(--gold);">—</strong> <span id="inst-nifty-chg" style="color:var(--green); font-weight:bold;">—</span></div>',
    content
)
content = re.sub(
    r'<div><span style="color:#888;">BANKNIFTY:</span> <strong style="color:var\(--gold\);">[^<]+</strong> <span style="color:var\(--green\); font-weight:bold;">[^<]+</span></div>',
    '<div><span style="color:#888;">BANKNIFTY:</span> <strong id="inst-bank-val" style="color:var(--gold);">—</strong> <span id="inst-bank-chg" style="color:var(--green); font-weight:bold;">—</span></div>',
    content
)
content = re.sub(
    r'<div><span style="color:#888;">SENSEX:</span> <strong style="color:var\(--gold\);">[^<]+</strong> <span style="color:var\(--green\); font-weight:bold;">[^<]+</span></div>',
    '<div><span style="color:#888;">SENSEX:</span> <strong id="inst-sensex-val" style="color:var(--gold);">—</strong> <span id="inst-sensex-chg" style="color:var(--green); font-weight:bold;">—</span></div>',
    content
)
content = re.sub(
    r'<div><span style="color:#888;">RELIANCE:</span> <strong style="color:var\(--gold\);">[^<]+</strong> <span style="color:var\(--green\); font-weight:bold;">[^<]+</span></div>',
    '<div><span style="color:#888;">RELIANCE:</span> <strong id="inst-reliance-val" style="color:var(--gold);">—</strong> <span id="inst-reliance-chg" style="color:var(--green); font-weight:bold;">—</span></div>',
    content
)

# 4. Insert helper functions in JS
js_helpers = '''
    function showConnectionBanner(msg) {
      var b = document.getElementById("connection-lost-banner");
      if (b) {
        if (msg) b.textContent = "⚠️ " + msg;
        b.style.display = "block";
      }
    }
    function hideConnectionBanner() {
      var b = document.getElementById("connection-lost-banner");
      if (b) b.style.display = "none";
    }
'''

if "function showConnectionBanner" not in content:
    content = content.replace('"use strict";', '"use strict";\n' + js_helpers, 1)

# 5. Update fetchAPI to show banner on failure and hide on success
old_fetch = '''    async function fetchAPI(url) {
      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
      } catch (e) {
        console.warn("fetch error for", url, e);
        return null;
      }
    }'''

new_fetch = '''    async function fetchAPI(url) {
      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        hideConnectionBanner();
        return await res.json();
      } catch (e) {
        console.warn("fetch error for", url, e);
        showConnectionBanner("CONNECTION LOST: API " + url + " unreachable (" + e.message + ")");
        return null;
      }
    }'''

content = content.replace(old_fetch, new_fetch)

# 6. Update catch in load()
old_load_catch = '    }catch(err){put("vm-state","SOURCE UNAVAILABLE — no verified prices");put("vm-provenance","Read-only source check failed; simulated prices remain hidden.");}'
new_load_catch = '''    }catch(err){
      put("vm-state","SOURCE UNAVAILABLE — no verified prices");
      put("vm-provenance","Read-only source check failed; simulated prices remain hidden.");
      if (typeof showConnectionBanner === "function") showConnectionBanner("CONNECTION LOST: Verified market source unavailable (" + err.message + ")");
    }'''
content = content.replace(old_load_catch, new_load_catch)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Applied UI fixes successfully.")
