from pathlib import Path
from datetime import datetime, timezone
import urllib.request,csv,hashlib,os,json
source="https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
folder=Path(r"C:\content\app\verified_sources")
folder.mkdir(parents=True,exist_ok=True)
target=folder/"dhan_instrument_master_detailed.csv"
temp=folder/"dhan_instrument_master_detailed.csv.pending"
if temp.exists(): temp.unlink()
count=0
try:
    req=urllib.request.Request(source,headers={"User-Agent":"Genesis-Data-Provenance-Checker/1.0"})
    with urllib.request.urlopen(req,timeout=30) as r,temp.open("wb") as f:
        while True:
            chunk=r.read(1024*1024)
            if not chunk:break
            count+=len(chunk)
            if count>100*1024*1024:raise ValueError("Oversized response")
            f.write(chunk)
    with temp.open("r",encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream)
        keys=list(reader.fieldnames or [])
        rows=sum(1 for _ in reader)
    if rows<10000 or not any("SECURITY_ID" in x for x in keys):
        raise ValueError("Invalid master header or row count")
    checksum=hashlib.sha256(temp.read_bytes()).hexdigest()
    os.replace(temp,target)
    meta={"downloaded_at_utc":datetime.now(timezone.utc).isoformat(),"url":source,"sha256":checksum,"bytes":count,"rows":rows,"header":keys}
    (folder/"master_manifest.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    print("MASTER_DOWNLOAD_PASS", "ROWS",rows,"BYTES",count,"SHA256",checksum,"COLUMN_NAMES",",".join(keys[:20]))
except Exception as e:
    if temp.exists():temp.unlink()
    print("MASTER_DOWNLOAD_BLOCKED",type(e).__name__,str(e)[:180])
    raise
