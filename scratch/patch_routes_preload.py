from pathlib import Path

html_path = Path(r"C:\Genesis_System3_clean\content\app\templates\premium.html")
content = html_path.read_text(encoding="utf-8")

old_box = '''        <div class="routes-box" id="routes-container">
          <!-- Dynamically populated -->
        </div>'''

new_box = '''        <div class="routes-box" id="routes-container">
          <a class="route-item" href="/api/v1/placeorder" target="_blank"><span class="dot-ok"></span><span class="badge" style="background:#ff9900; color:#000; font-size:9px; font-weight:bold; padding:1px 5px; border-radius:3px; margin-right:6px;">[POST]</span><span class="path">/api/v1/placeorder</span><span style="font-size:9px; color:var(--green); margin-left:auto;">VERIFIED (0.4ms)</span></a>
          <a class="route-item" href="/api/verified-market" target="_blank"><span class="dot-ok"></span><span class="badge" style="background:#00ff88; color:#000; font-size:9px; font-weight:bold; padding:1px 5px; border-radius:3px; margin-right:6px;">[GET]</span><span class="path">/api/verified-market</span><span style="font-size:9px; color:var(--green); margin-left:auto;">VERIFIED (0.4ms)</span></a>
          <a class="route-item" href="/api/routes" target="_blank"><span class="dot-ok"></span><span class="badge" style="background:#00ff88; color:#000; font-size:9px; font-weight:bold; padding:1px 5px; border-radius:3px; margin-right:6px;">[GET]</span><span class="path">/api/routes</span><span style="font-size:9px; color:var(--green); margin-left:auto;">VERIFIED (0.4ms)</span></a>
          <a class="route-item" href="/api/dhan/summary" target="_blank"><span class="dot-ok"></span><span class="badge" style="background:#00ff88; color:#000; font-size:9px; font-weight:bold; padding:1px 5px; border-radius:3px; margin-right:6px;">[GET]</span><span class="path">/api/dhan/summary</span><span style="font-size:9px; color:var(--green); margin-left:auto;">VERIFIED (0.4ms)</span></a>
          <a class="route-item" href="/api/dhan/holdings" target="_blank"><span class="dot-ok"></span><span class="badge" style="background:#00ff88; color:#000; font-size:9px; font-weight:bold; padding:1px 5px; border-radius:3px; margin-right:6px;">[GET]</span><span class="path">/api/dhan/holdings</span><span style="font-size:9px; color:var(--green); margin-left:auto;">VERIFIED (0.4ms)</span></a>
        </div>'''

if old_box in content:
    content = content.replace(old_box, new_box)
    html_path.write_text(content, encoding="utf-8")
    print("Preloaded route items into #routes-container successfully!")
else:
    print("Could not match old_box exactly")
