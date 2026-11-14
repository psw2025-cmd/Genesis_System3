#!/usr/bin/env python3
"""Generate fresh, read-only Genesis UI truth diagrams.

Run from repository root:
  python3 scripts/generate_live_ui_truth.py --live-url "$GENESIS_LIVE_URL"

Inputs are re-read on every execution: current checkout, current Actions jobs,
and the optional current /api/deploy/info response. Generated files are replaced
on every execution and are never used as input.
"""
from __future__ import annotations
import argparse, datetime as dt, html, json, os, re, shutil, subprocess, urllib.request
from pathlib import Path

TABS=("Broker","Data Integrity","Dashboard","Overview","Prediction Audit","ML Model",
      "Performance","Multibagger","Risk & Scenarios","Alerts","System Readiness",
      "Live Gate","Sim Live","Paper Trading","Truth Control","Genesis Brain","E2E Proof")
MARKERS=("frontend runtime smoke","browser runtime smoke","23-tab")

def command(args, root):
    try:
        p=subprocess.run(args,cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                         timeout=30,check=False)
        return p.returncode,p.stdout.strip()
    except (OSError,subprocess.TimeoutExpired): return 127,""

def git(root,*args):
    rc,out=command(["git",*args],root); return out if rc==0 else None

def gh(root,path):
    if not shutil.which("gh"): return None
    rc,out=command(["gh","api",path],root)
    try: return json.loads(out) if rc==0 else None
    except json.JSONDecodeError: return None

def status(value):
    return "PASS" if value=="success" else "FAIL" if value=="failure" else "UNKNOWN"

def source_truth(root):
    text=""; paths=[]
    for p in root.rglob("*"):
        if any(x in p.parts for x in (".git","node_modules",".venv","dist","build")) or not p.is_file():
            continue
        if p.suffix.lower() not in (".py",".js",".jsx",".ts",".tsx",".html",".yml",".yaml",".json"): continue
        try:
            s=p.read_text(encoding="utf-8",errors="ignore")
            if len(s)<2_000_000: text+="\n"+s; paths.append(str(p.relative_to(root)))
        except OSError: pass
    low=text.lower()
    return {"tabs_found":[x for x in TABS if x.lower() in low],
            "api_contracts":[x for x in ("/api/deploy/info","/api/health","/api/scheduler/health",
                 "/api/ml/performance","/api/paper/pipeline/status","/api/positions") if x in low],
            "safety_locks":{k:bool(re.search(k+r"[^\n]{0,100}(?:0|false)",text,re.I))
                for k in ("PAPER_MODE","LIVE_ORDER_AUTHORITY","REAL_BROKER_ORDERS")}}

def actions_truth(root,slug):
    base={"status":"UNKNOWN","run":None,"job":None,"tab_check":"UNKNOWN","sha_check":"UNKNOWN",
          "reason":"GitHub CLI authenticated evidence is unavailable"}
    if not slug: base["reason"]="Repository has no GitHub origin"; return base
    workflows=gh(root,"repos/"+slug+"/actions/workflows?per_page=100") or {}
    wf=next((x for x in workflows.get("workflows",[]) if any(m in (x.get("name","")+" "+x.get("path","")).lower() for m in MARKERS)),None)
    if not wf: base["reason"]="Browser-runtime workflow not found"; return base
    data=gh(root,"repos/"+slug+"/actions/workflows/"+str(wf["id"])+"/runs?per_page=10") or {}
    runs=data.get("workflow_runs",[])
    if not runs: base["reason"]="No workflow run returned"; return base
    run=max(runs,key=lambda x:x.get("created_at","")); base.update(status=status(run.get("conclusion")),run=run)
    jobs=gh(root,"repos/"+slug+"/actions/runs/"+str(run["id"])+"/jobs?per_page=100") or {}
    job=next(iter(jobs.get("jobs",[])),None); base["job"]=job
    for step in (job or {}).get("steps",[]):
        n=step.get("name","").lower(); s=status(step.get("conclusion"))
        if "canonical tabs" in n or "23-tab" in n or "23 tab" in n: base["tab_check"]=s
        if "serving sha" in n or "deployment lineage" in n or "deploy info" in n: base["sha_check"]=s
    return base

def live_truth(url):
    if not url: return {"status":"UNKNOWN","sha":None,"reason":"No --live-url / GENESIS_LIVE_URL"}
    try:
        with urllib.request.urlopen(url.rstrip("/")+"/api/deploy/info",timeout=12) as r: d=json.load(r)
        sha=d.get("sha") or d.get("git_sha") or d.get("actual_sha") or d.get("commit_sha")
        return {"status":"PASS" if sha else "UNKNOWN","sha":str(sha) if sha else None,
                "reason":None if sha else "Endpoint returned no deployed SHA"}
    except Exception as e: return {"status":"UNKNOWN","sha":None,"reason":type(e).__name__}

def col(s): return {"PASS":"#b7efc5","FAIL":"#ffc5c5","UNKNOWN":"#ffe5a3"}.get(s,"#e5e7eb")
def esc(x): return html.escape(str(x))
def box(x,y,title,s,lines):
    z=[f'<rect x="{x}" y="{y}" width="390" height="122" rx="12" fill="{col(s)}" stroke="#163d67" stroke-width="2"/>',
       f'<text x="{x+14}" y="{y+28}" class="title">{esc(title)} — {esc(s)}</text>']
    z += [f'<text x="{x+14}" y="{y+53+i*18}" class="body">{esc(line)}</text>' for i,line in enumerate(lines[:3])]
    return "\n".join(z)

def render(report):
    a,l,r=report["actions"],report["live"],report["repo"]; expected=report["git_sha"] or "unknown"; deployed=l["sha"] or "unknown"
    match="UNKNOWN" if "unknown" in (expected,deployed) else ("PASS" if expected.startswith(deployed[:7]) or deployed.startswith(expected[:7]) else "FAIL")
    run=a["run"] or {}; job=a["job"] or {}; runurl=run.get("html_url","not available")
    cells=[
      (55,155,"Safety locks","PASS" if all(r["safety_locks"].values()) else "UNKNOWN",[f"{k}: {'off' if v else 'not proven'}" for k,v in r["safety_locks"].items()]),
      (55,330,"Current source contracts","PASS" if r["tabs_found"] else "UNKNOWN",[f"tabs found: {len(r['tabs_found'])}",f"API contracts: {len(r['api_contracts'])}","Source presence is not runtime proof"]),
      (555,155,"Browser runtime smoke",a["status"],[f"run: {run.get('id','unknown')}",f"commit: {run.get('head_sha','unknown')[:12]}",f"run link: {runurl}"]),
      (555,330,"23-tab browser check",a["tab_check"],["canonical tab render step","per-tab visual artifact in Actions",f"job: {job.get('html_url','unknown')}"]),
      (1055,155,"Serving-SHA gate",a["sha_check"],["separate release-proof workflow step",a.get("reason") or "current Actions job queried","never promoted from unknown"]),
      (1055,330,"Live deployment identity",match,[f"expected: {expected[:12]}",f"deployed: {deployed[:12]}",l.get("reason") or "read-only endpoint probe"]),
    ]
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="700">',
      '<style>.title{font:700 18px Arial;fill:#102a43}.body{font:14px Arial;fill:#243b53}.head{font:700 28px Arial;fill:#fff}.small{font:14px Arial;fill:#d9e2ec}</style>',
      '<rect width="1500" height="700" fill="#f7fbff"/><rect x="18" y="16" width="1464" height="82" rx="14" fill="#0b3769"/>',
      '<text x="45" y="53" class="head">GENESIS SYSTEM3 — LIVE UI TRUTH MAP</text>',
      f'<text x="45" y="79" class="small">Fresh evidence generated {esc(report["generated_at"])} · generated output is never reused as input</text>',
      '<text x="55" y="130" class="title">CORE FILES</text><text x="555" y="130" class="title">GITHUB ACTIONS</text><text x="1055" y="130" class="title">LIVE UI / DEPLOYMENT</text>']
    svg += [box(*x) for x in cells]
    svg += ['<path d="M445 216H555M945 216H1055M445 390H555M945 390H1055" stroke="#4a5568" stroke-width="3" fill="none"/>',
      '<rect x="55" y="525" width="1385" height="105" rx="12" fill="#e6f4ff" stroke="#163d67"/>',
      '<text x="75" y="558" class="title">SAFE READ-ONLY NEXT STEP</text>',
      f'<text x="75" y="590" class="body">{esc("Open the run/job link and inspect the failed step only; do not deploy, merge, or alter cloud state." if a["status"]=="FAIL" else "Review the current run evidence before any change; all probes are read-only.")}</text>',
      '</svg>']
    return "\n".join(svg)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--repo",type=Path,default=Path.cwd()); p.add_argument("--live-url",default=os.getenv("GENESIS_LIVE_URL")); p.add_argument("--output",type=Path,default=Path("audit_results/live_ui_truth")); args=p.parse_args()
    root=args.repo.resolve(); out=(root/args.output).resolve() if not args.output.is_absolute() else args.output; out.mkdir(parents=True,exist_ok=True)
    for name in ("genesis_ui_live_truth.svg","genesis_ui_live_truth.mmd","genesis_ui_live_truth.json"): (out/name).unlink(missing_ok=True)
    origin=git(root,"config","--get","remote.origin.url") or ""; m=re.search(r"github\.com[:/]([^/]+/[^/.]+)(?:\.git)?$",origin)
    report={"generated_at":dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),"git_sha":git(root,"rev-parse","HEAD"),"repo":source_truth(root),"actions":actions_truth(root,m.group(1) if m else None),"live":live_truth(args.live_url)}
    (out/"genesis_ui_live_truth.json").write_text(json.dumps(report,indent=2)+"\n")
    (out/"genesis_ui_live_truth.mmd").write_text("flowchart LR\n  A[Current source] --> B[Browser smoke: "+report["actions"]["status"]+"]\n  B --> C[23-tab: "+report["actions"]["tab_check"]+"]\n  B --> D[Serving SHA: "+report["actions"]["sha_check"]+"]\n")
    (out/"genesis_ui_live_truth.svg").write_text(render(report))
    print(out/"genesis_ui_live_truth.svg")
if __name__=="__main__": main()
