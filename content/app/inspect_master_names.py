import json
from pathlib import Path
rows=json.loads(Path(r"C:\Genesis_System3_clean\storage\instruments\OpenAPIScripMaster.json").read_text(encoding="utf-8"))
for needle in ("NIFTY","RELIANCE","SENSEX"):
 m=[r for r in rows if str(r.get("name") or "").strip().upper()==needle]
 print("NAME",needle,"COUNT",len(m))
 keys=("name","symbol","token","instrumenttype","exch_seg","description","expiry")
 for r in m[:5]: print({k:str(r.get(k,""))[:60] for k in keys})
