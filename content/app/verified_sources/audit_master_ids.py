import csv
from collections import Counter
from pathlib import Path
p=Path(r"C:\content\app\verified_sources\dhan_instrument_master_detailed.csv")
counts=Counter();targets={"NIFTY","NIFTY 50","NIFTY BANK","BANKNIFTY","SENSEX","RELIANCE"}
hits=[]
with p.open(encoding="utf-8-sig",newline="") as f:
 for row in csv.DictReader(f):
  seg=(row.get("EXCH_ID",""),row.get("SEGMENT",""),row.get("INSTRUMENT",""))
  counts[seg]+=1
  s=(row.get("SYMBOL_NAME") or "").upper().strip()
  if s in targets and row.get("INSTRUMENT") in ("INDEX","EQUITY"):
   hits.append({k:row.get(k) for k in ("EXCH_ID","SEGMENT","SECURITY_ID","SYMBOL_NAME","INSTRUMENT","DISPLAY_NAME")})
print("TOP_SEGMENTS",counts.most_common(12))
print("INDEX_CASH_TARGETS",hits[:25])
