import json,datetime
from pathlib import Path
p=Path(r"C:\Genesis_System3_clean\storage\instruments\OpenAPIScripMaster.json")
d=json.loads(p.read_text(encoding="utf-8"))
rows=d if isinstance(d,list) else d.get("rows",[])
print("MASTER_ROWS",len(rows),"KEYS",list(rows[0])[:30] if rows else [])
for needle in ("NIFTY","BANKNIFTY","SENSEX","RELIANCE"):
    m=[r for r in rows if str(r.get("name") or "").strip().upper()==needle and str(r.get("instrumenttype") or "").upper() in ("INDEX","EQUITY","EQ")]
    print("LOOKUP",needle,"MATCHES",len(m))
    for r in m[:3]:
        print("FIELDS",{k:str(r.get(k,''))[:80] for k in ("name","symbol","token","instrumenttype","exch_seg","segment","description","expiry")})
