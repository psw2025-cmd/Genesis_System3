import re
from pathlib import Path

p = Path(r"C:\content\app\templates\premium.html")
text = p.read_text(encoding="utf-8")

# 1. Update Header
target1 = """          <div class="card-header">
            <div class="card-title">Top CE / PE Gainer Movers</div>
            <span style="font-size:10px; color:var(--gold);">Dhan L2 Options</span>
          </div>"""

replacement1 = """          <div class="card-header">
            <div class="card-title">Top CE / PE Gainer Movers (Verified Equity & Index F&O)</div>
            <span class="badge" style="background:rgba(0,255,136,0.15); color:var(--green); font-size:10px;">80 VERIFIED CONTRACTS (60 IDX + 20 EQ F&O)</span>
          </div>"""

if target1 in text:
    text = text.replace(target1, replacement1)
    print("Updated card-header successfully.")
else:
    print("target1 not found in premium.html")

# 2. Update loop in loadOptionsMovers
old_loop_pattern = re.compile(
    r'all\.forEach\(c\s*=>\s*\{[\s\S]*?const oiText\s*=\s*c\.oi_change_pct[\s\S]*?rows\s*\+=\s*`[\s\S]*?<tr>[\s\S]*?<td[^>]*>\$\{c\.contract\}</td>[\s\S]*?</tr>[\s\S]*?`\s*;?\s*\}\);',
    re.MULTILINE
)

new_loop = """const indexSymbols = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX', 'BANKEX'];
      all.forEach(c => {
        const isUp = c.change_pct >= 0;
        const oiText = c.oi_change_pct == null || !Number.isFinite(Number(c.oi_change_pct)) ? '—' : (Number(c.oi_change_pct) >= 0 ? '+' : '') + c.oi_change_pct + '%';
        const isEq = !indexSymbols.includes(c.symbol);
        const tag = isEq
          ? '<span style="background:rgba(255,215,0,0.18); color:var(--gold); font-size:9px; font-weight:bold; padding:1px 5px; border-radius:3px; margin-right:6px; border:1px solid rgba(255,215,0,0.4);">EQ F&O</span>'
          : '<span style="background:rgba(0,180,255,0.18); color:var(--blue); font-size:9px; font-weight:bold; padding:1px 5px; border-radius:3px; margin-right:6px; border:1px solid rgba(0,180,255,0.4);">INDEX</span>';
        rows += `
          <tr>
            <td>${tag}<span style="font-weight:bold; color:var(--text);">${c.contract}</span></td>
            <td>₹${fmt(c.ltp)}</td>
            <td class="${isUp ? 'up' : 'dn'}">${isUp ? '+' : ''}${c.change_pct}%</td>
            <td class="${c.oi_change_pct >= 0 ? 'up' : 'dn'}">${oiText}</td>
          </tr>
        `;
      });"""

if old_loop_pattern.search(text):
    text = old_loop_pattern.sub(new_loop, text)
    print("Updated loadOptionsMovers loop successfully.")
else:
    print("old_loop_pattern not matched")

p.write_text(text, encoding="utf-8")
print("Saved premium.html successfully.")
