"""Idempotent non-secret System3 configuration repair. No authentication/network/broker operations."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import os,shutil
base=Path(r"C:\Genesis_System3_clean")
src=base/".env"
secret=base/".secrets"/"dhan.env"
app=Path(r"C:\content\app")
dst=app/".env"
if not src.is_file() or not secret.is_file():
    raise SystemExit("CONFIG_BLOCKED: existing root .env or referenced secret file absent")
changes={
"SYSTEM3_MODE":"analyze",
"ANALYZE_MODE":"1",
"PAPER_MODE":"1",
"LIVE_TRADING_ENABLED":"0",
"SYSTEM3_LIVE_TRADING_ALLOWED":"0",
"AUTO_EXECUTE_TRADES":"0",
"LIVE_ORDER_AUTHORITY":"0",
"ORDER_PLACEMENT_ALLOWED":"false",
"ORDER_PLACEMENT_MODE":"PAPER",
"LIVE_MARKET_FEED":"false",
"DHAN_FEED_MODE":"LIVE",
"DATA_FEED_SOURCE":"DHAN_READ_ONLY_UNVERIFIED",
"DHAN_ENV_PATH":str(secret),
"DHAN_DATA_FETCH_ENABLED":"true",
"DHAN_LIVE_FEED_VERIFIED":"false",
"DATA_PROVENANCE_REQUIRED":"true",
}
old=src.read_text(encoding="utf-8-sig")
lines=old.splitlines()
existing={}
for i,line in enumerate(lines):
    s=line.strip()
    if not s or s.startswith("#") or "=" not in s:continue
    key,_=s.split("=",1);key=key.strip()
    if key in changes:
        if key in existing:raise SystemExit("CONFIG_BLOCKED: duplicate controlled setting "+key)
        existing[key]=i
for key,value in changes.items():
    line=f"{key}={value}"
    if key in existing:lines[existing[key]]=line
    else:lines.append(line)
result="\n".join(lines).rstrip()+"\n"
other=["# Genesis verified-only local service settings (NO ACCESS TOKEN HERE)"]+[f"{k}={v}" for k,v in changes.items()]
local="\n".join(other).rstrip()+"\n"
stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
backup_dir=base/".secrets"/"config_backups"
backup_dir.mkdir(parents=True,exist_ok=True)
if result!=old:
    backup=backup_dir/(".env."+stamp+".bak")
    shutil.copy2(src,backup)
    temp=src.with_name(".env.safe_pending")
    temp.write_text(result,encoding="utf-8")
    shutil.copymode(src,temp)
    os.replace(temp,src)
    print("ROOT_ENV_UPDATED",True,"BACKUP_KEPT",str(backup))
else:print("ROOT_ENV_UPDATED",False,"NO_CHANGE_NEEDED",True)
if dst.exists() and dst.read_text(encoding="utf-8-sig")!=local:
    backup=backup_dir/("local-app-env."+stamp+".bak")
    shutil.copy2(dst,backup)
    print("LOCAL_ENV_BACKUP_KEPT",str(backup))
if not dst.exists() or dst.read_text(encoding="utf-8-sig")!=local:
    temp=dst.with_name(".env.safe_pending")
    temp.write_text(local,encoding="utf-8")
    if dst.exists():shutil.copymode(dst,temp)
    os.replace(temp,dst)
print("LOCAL_APP_ENV_PRESENT",dst.exists())
print("SECRET_FILE_REFERENCED",secret.is_file())
print("SECRET_CONTENT_EXPOSED",False)
print("TRADING_LOCKS", {k:changes[k] for k in ("PAPER_MODE","LIVE_TRADING_ENABLED","LIVE_ORDER_AUTHORITY","SYSTEM3_LIVE_TRADING_ALLOWED","AUTO_EXECUTE_TRADES","ORDER_PLACEMENT_ALLOWED")})
print("LIVE_FEED_VERIFIED",False)
