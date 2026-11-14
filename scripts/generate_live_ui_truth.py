#!/usr/bin/env python3
"""Create fresh, read-only SVG + Mermaid UI truth maps from current evidence.

Run in a Genesis checkout:
  python3 scripts/generate_live_ui_truth.py --live-url "$GENESIS_LIVE_URL"

Every run reads the current checkout, current GitHub Actions job and optional
current /api/deploy/info response. It overwrites only its own output files.
"""
import argparse, datetime as dt, html, json, os, re, shutil, subprocess, urllib.request
from pathlib import Path

def call(cmd, cwd):
    try:
        p=subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30)
        return p.returncode,p.stdout.strip()
    except Exception:return 1,""
def git(root,*x):
    rc,out=call(["git",*x],root);return out if rc==0 else None
def api(root,path):
    if not shutil.which("gh"):return None
    rc,out=call(["gh","api",path],root)
    try:return json.loads(out) if rc==0 else None
    except json.JSONDecodeError:return None
def state(x):return {"success":"PASS","failure":"FAIL"}.get(x,"UNKNOWN")
def source(root):
    patterns=("PAPER_MODE","LIVE_ORDER_AUTHORITY","REAL_BROKER_ORDERS","/api/deploy/info","/api/health","/api/positions")
    found={}
    for p in root.rglob("*"):
        if not p.is_file() or any(a in p.parts for a in (".git","node_modules",".venv","dist","build")):continue
        if p.suffix not in (".py",".js",".jsx",".ts",".tsx",".html",".yml",".yaml",".json"):continue
        try:t=p.read_text(errors="ignore")
        except OSError:continue
        for x in patterns:
            if x in t:found[x]=True
    locks=all(found.get(x) for x in patterns[:3])
    return {"status":"PASS" if locks else "UNKNOWN","locks":locks,
            "apis":sum(bool(found.get(x)) for x in patterns[3:])}
def actions(root,slug):
    unknown={"status":"UNKNOWN","tab":"UNKNOWN","sha":"UNKNOWN","run":{},"job":{},"reason":"GitHub Actions evidence unavailable"}
    if not slug:return unknown
    w=api(root,"repos/"+slug+"/actions/workflows?per_page=100") or {}
    wf=next((x for x in w.get("workflows",[]) if "frontend-runtime-smoke" in x.get("path","")),None)
    if not wf:unknown["reason"]="Frontend runtime workflow not found";return unknown
    runs=(api(root,"repos/"+slug+"/actions/workflows/"+str(wf["id"])+"/runs?per_page=5") or {}).get("workflow_runs",[])
    if not runs:unknown["reason"]="No current smoke run";return unknown
    r=max(runs,key=lambda x:x.get("created_at",""))
    jobs=(api(root,"repos/"+slug+"/actions/runs/"+str(r["id"])+"/jobs?per_page=100") or {}).get("jobs",[])
    j=jobs[0] if jobs else {}
    tab=sha="UNKNOWN"
    for s in j.get("steps",[]):
        n=s.get("name","").lower()
        if "canonical tabs" in n or "23-tab" in n:tab=state(s.get("conclusion"))
        if "serving sha" in n or "deployment lineage" in n or "deploy info" in n:sha=state(s.get("conclusion"))
    return {"status":state(r.get("conclusion")),"tab":tab,"sha":sha,"run":r,"job":j,"reason":None}
def live(url):
    if not url:return {"status":"UNKNOWN","sha":None,"reason":"No live URL supplied"}
    try:
        with urllib.request.urlopen(url.rstrip("/")+"/api/deploy/info",timeout=12) as f:d=json.load(f)
        s=d.get("sha") or d.get("git_sha") or d.get("actual_sha") or d.get("commit_sha")
        return {"status":"PASS" if s else "UNKNOWN","sha":str(s) if s else None,"reason":None if s else "No deployed SHA in response"}
    except Exception as e:return {"status":"UNKNOWN","sha":None,"reason":type(e).__name__}
def esc(x):return html.escape(str(x))
def paint(status):return {"PASS":"#b8f2c8","FAIL":"#ffc7c7","UNKNOWN":"#ffe7a8"}[status]
def cell(x,y,title,status,items):
    a=[f'<rect x="{x}" y="{y}" width="410" height="130" rx="12" fill="{paint(status)}" stroke="#143f6b" stroke-width="2"/>',
       f'<text x="{x+15}" y="{y+30}" class="t">{esc(title)} — {status}</text>']
    a += [f'<text x="{x+15}" y="{y+57+20*i}" class="b">{esc(v)}</text>' for i,v in enumerate(items[:3])]
    return "\n".join(a)
def draw(d):
    a,l,s=d["actions"],d["live"],d["source"]; expected=d["commit"] or "unknown"; deployed=l["sha"] or "unknown"
    match="UNKNOWN" if "unknown" in (expected,deployed) else ("PASS" if expected.startswith(deployed[:7]) or deployed.startswith(expected[:7]) else "FAIL")
    r=a["run"];j=a["job"]
    cells=[(50,150,"Safety locks in source",s["status"],["PAPER_MODE / LIVE_ORDER_AUTHORITY / REAL_BROKER_ORDERS",f"API contracts found: {s['apis']}","source presence is not runtime proof"]),
      (545,150,"Browser runtime smoke",a["status"],[f"run: {r.get('id','unknown')}",f"commit: {r.get('head_sha','unknown')[:12]}",r.get("html_url","link unavailable")]),
      (545,350,"23-tab render proof",a["tab"],["canonical tab step",j.get("html_url","job link unavailable"),"visual proof artifact is in this run"]),
      (1040,150,"Serving-SHA gate",a["sha"],["release proof gate",a.get("reason") or "current job evidence","does not treat missing SHA as PASS"]),
      (1040,350,"Deployed identity",match,[f"expected: {expected[:12]}",f"deployed: {deployed[:12]}",l.get("reason") or "read-only deploy-info probe"])]
    o=['<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="660"><style>.t{font:700 18px Arial;fill:#102a43}.b{font:14px Arial;fill:#243b53}.h{font:700 28px Arial;fill:#fff}.q{font:14px Arial;fill:#d9e2ec}</style><rect width="1500" height="660" fill="#f7fbff"/><rect x="18" y="16" width="1464" height="80" rx="14" fill="#0b3769"/><text x="45" y="52" class="h">GENESIS SYSTEM3 — LIVE UI TRUTH MAP</text>',
       f'<text x="45" y="78" class="q">Freshly generated {esc(d["time"])} UTC · current inputs only · PASS/FAIL/UNKNOWN</text>']
    o += [cell(*c) for c in cells]
    o += ['<rect x="50" y="540" width="1400" height="70" rx="12" fill="#e8f4ff" stroke="#143f6b"/><text x="70" y="570" class="t">SAFE READ-ONLY NEXT STEP</text>',
          f'<text x="70" y="595" class="b">{esc("Open the displayed Actions run/job and inspect the failed step; do not deploy or change state." if a["status"]=="FAIL" else "Review the displayed current Actions evidence before making any change.")}</text></svg>']
    return "\n".join(o)
def main():
    p=argparse.ArgumentParser();p.add_argument("--repo",type=Path,default=Path.cwd());p.add_argument("--live-url",default=os.getenv("GENESIS_LIVE_URL"));p.add_argument("--output",type=Path,default=Path("audit_results/live_ui_truth"));x=p.parse_args()
    root=x.repo.resolve();out=(root/x.output).resolve() if not x.output.is_absolute() else x.output;out.mkdir(parents=True,exist_ok=True)
    for n in ("genesis_ui_live_truth.svg","genesis_ui_live_truth.mmd","genesis_ui_live_truth.json"):(out/n).unlink(missing_ok=True)
    origin=git(root,"config","--get","remote.origin.url") or "";m=re.search(r"github\.com[:/]([^/]+/[^/.]+)(?:\.git)?$",origin)
    d={"time":dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),"commit":git(root,"rev-parse","HEAD"),"source":source(root),"actions":actions(root,m.group(1) if m else None),"live":live(x.live_url)}
    (out/"genesis_ui_live_truth.json").write_text(json.dumps(d,indent=2)+"\n")
    (out/"genesis_ui_live_truth.mmd").write_text("flowchart LR\n A[Current source] --> B[Browser smoke: "+d["actions"]["status"]+"]\n B --> C[23-tab: "+d["actions"]["tab"]+"]\n B --> D[Serving SHA: "+d["actions"]["sha"]+"]\n")
    (out/"genesis_ui_live_truth.svg").write_text(draw(d));print(out/"genesis_ui_live_truth.svg")
if __name__=="__main__":main()
