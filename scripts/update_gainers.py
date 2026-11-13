from pathlib import Path

app_path = Path(r"C:\content\app\app.py")
content = app_path.read_text(encoding="utf-8")

old_code = """    ce_movers.sort(key=lambda x: x["change_pct"], reverse=True)
    pe_movers.sort(key=lambda x: x["change_pct"], reverse=True)

    return make_envelope({
        "ce_gainers": ce_movers[:25],
        "pe_gainers": pe_movers[:25],"""

new_code = """    ce_movers.sort(key=lambda x: x["change_pct"], reverse=True)
    pe_movers.sort(key=lambda x: x["change_pct"], reverse=True)

    indices = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"}
    equity_fo = {"COLPAL", "RELIANCE"}
    ce_idx = [c for c in ce_movers if c.get("symbol") in indices]
    ce_eq = [c for c in ce_movers if c.get("symbol") in equity_fo]
    pe_idx = [c for c in pe_movers if c.get("symbol") in indices]
    pe_eq = [c for c in pe_movers if c.get("symbol") in equity_fo]
    top_ce = (ce_idx[:20] + ce_eq[:10]) if ce_eq else ce_movers[:30]
    top_pe = (pe_idx[:20] + pe_eq[:10]) if pe_eq else pe_movers[:30]

    return make_envelope({
        "ce_gainers": top_ce,
        "pe_gainers": top_pe,"""

if old_code in content:
    content = content.replace(old_code, new_code, 1)
    app_path.write_text(content, encoding="utf-8")
    print("SUCCESS: app.py updated with both index and equity F&O gainers.")
else:
    print("ERROR: old_code not found in app.py")
