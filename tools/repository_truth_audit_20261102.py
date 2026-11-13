from __future__ import annotations
import ast,os,re,json,csv,subprocess
from collections import Counter,defaultdict
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(r"C:\Genesis_System3_clean")
OUT=ROOT/"reports"/"data_truth_recovery_20261102"
OUT.mkdir(parents=True,exist_ok=True)
SKIP={".git",".venv","venv","node_modules","__pycache__",".pytest_cache",".agents","reports","evidence","state","logs","cache","backups","dist","build",".secrets","site-packages",".github"}
EX={".py",".js",".jsx",".ts",".tsx",".html",".sh",".ps1",".yaml",".yml",".toml"}
regexes={
"csv_read":r"\b(read_csv|DictReader|csv\.reader|genfromtxt|loadtxt)\s*\(",
"csv_write":r"\b(to_csv|DictWriter|csv\.writer|savetxt)\s*\(",
"csv_filename":r"\.csv\b",
"storage_live":r"storage[/\\]live|['\"]live['\"]",
"storage_ref":r"\bstorage[/\\]|['\"]storage['\"]",
"option_chain":r"option[_-]?chain|optionchain|chain[_-]?cache|fetch_chains_for_segments",
"feed_candidate":r"dhanhq|api\.dhan\.co|marketfeed|websocket|on_tick|subscribe",
"simulated":r"\b(mock|fake|synthetic|simulated|demo|placeholder|dummy|random_walk)\b",
"fallback":r"\b(fallback|stale|cached|last_good|previous_close)\b",
"provenance":r"\b(source_timestamp|exchange_timestamp|sha256|verified|provenance)\b",
"file_emit":r"\b(to_parquet|write_parquet|write_text|json\.dump|INSERT INTO|redis\.set)\b",
}
patterns={k:re.compile(v,re.I) for k,v in regexes.items()}
hits=[];files=[];counts=Counter();source_rows=[];imports=[];skips=[]
for basedir,dirs,names in os.walk(ROOT):
    dirs[:]=[z for z in dirs if z not in SKIP]
    for name in names:
        path=Path(basedir)/name
        if path.suffix.lower() not in EX:continue
        rel=path.relative_to(ROOT).as_posix()
        try:
            if path.stat().st_size>4194304:
                skips.append((rel,"oversize"));continue
            content=path.read_text(encoding="utf-8")
        except (OSError,UnicodeError):
            skips.append((rel,"unreadable"));continue
        files.append(rel)
        flags=Counter()
        for n,line in enumerate(content.splitlines(),1):
            if len(line)>10000:continue
            for kind,reg in patterns.items():
                if reg.search(line):
                    flags[kind]+=1;counts[kind]+=1
                    hits.append({"file":rel,"line":n,"keyword":kind})
        if flags["option_chain"] or flags["feed_candidate"] or flags["csv_read"]:
            kind=("OPTION_CHAIN_SOURCE_OR_CONSUMER_CANDIDATE" if flags["option_chain"] else "FEED_CANDIDATE" if flags["feed_candidate"] else "CSV_READER_CANDIDATE")
            source_rows.append({"file":rel,"category":kind,"csv_read_hits":flags["csv_read"],"option_chain_hits":flags["option_chain"],"feed_hits":flags["feed_candidate"],"provenance_status":"UNKNOWN","raw_receipt":"NONE_IN_THIS_AUDIT"})
        if path.suffix==".py":
            try:
                tree=ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node,ast.Import):
                        for alias in node.names:imports.append({"file":rel,"line":node.lineno,"module":alias.name})
                    elif isinstance(node,ast.ImportFrom) and node.module:
                        imports.append({"file":rel,"line":node.lineno,"module":node.module})
            except SyntaxError:
                skips.append((rel,"syntax_error"))
def writetable(filename,rows,fields):
    with (OUT/filename).open("w",encoding="utf-8-sig",newline="") as file:
        writer=csv.DictWriter(file,fieldnames=fields,extrasaction="ignore")
        writer.writeheader()
        for row in rows:writer.writerow(row)
writetable("STATIC_KEYWORD_HITS.csv",hits,["file","line","keyword"])
writetable("SOURCE_CLASSIFICATION.csv",source_rows,["file","category","csv_read_hits","option_chain_hits","feed_hits","provenance_status","raw_receipt"])
writetable("IMPORT_EDGES.csv",imports,["file","line","module"])
writetable("CSV_RUNTIME_INVENTORY.csv",[
 {"file":h["file"],"line":h["line"],"direction":"READ_CANDIDATE" if h["keyword"]=="csv_read" else "WRITE_OR_EXPORT_CANDIDATE","verified_runtime_read":"NO","review":"REQUIRED"}
 for h in hits if h["keyword"] in ("csv_read","csv_write")],
 ["file","line","direction","verified_runtime_read","review"])
stamp=datetime.now(timezone.utc).isoformat()
git=lambda *args:subprocess.run(["git",*args],cwd=ROOT,capture_output=True,text=True).stdout.strip()
sha=git("rev-parse","HEAD");branch=git("branch","--show-current")
summary={"generated_utc":stamp,"branch":branch,"sha":sha,"files_scanned":len(files),"excluded_partial_count":len(skips),"category_hits":dict(counts),"candidate_source_modules":len(source_rows),"import_edges":len(imports),"independent_market_receipts":0,"verdict":"STATIC_AUDIT_ONLY_NOT_CERTIFIED"}
(OUT/"SUMMARY.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
def leaders(kind,limit=25):
    ranked=Counter(h["file"] for h in hits if h["keyword"]==kind).most_common(limit)
    return "\n".join("| "+str(file)+" | "+str(n)+" |" for file,n in ranked)
(OUT/"DEPENDENCY_GRAPH.md").write_text(
"# Dependency graph — source-only audit\n\nGenerated UTC: "+stamp+"\n\nBranch: "+branch+"\nGit SHA: "+sha+
"\nPython import edges in IMPORT_EDGES.csv: "+str(len(imports))+
"\n\n## CSV reader candidates\n\n| File | Match count |\n|---|---:|\n"+leaders("csv_read")+
"\n\n## Option chain candidates\n\n| File | Match count |\n|---|---:|\n"+leaders("option_chain")+
"\n\n## Feed candidates\n\n| File | Match count |\n|---|---:|\n"+leaders("feed_candidate")+
"\n\nStatic matches show code locations, not live execution or verified exchange provenance.\n",encoding="utf-8")
(OUT/"DATAFLOW_GRAPH.md").write_text(
"# Data-flow graph — REQUIRED design, not yet observed end-to-end\n\n"+
"Authorized Dhan data -> raw authenticated receipt -> identity + timestamp + freshness validation -> hot cache -> durable columnar events -> Parquet snapshots -> analytical query -> signal/paper engine -> API -> truthful UI.\n\n"+
"On missing provider receipt, unknown source, stale exchange timestamp, incomplete contract identity or schema mismatch: show DATA UNAVAILABLE and do not backfill from demo/cached CSV as LIVE.\n\n"+
"CSV remains valid for exchange-provided instrument master, exports, audits, tests and offline training. Only verified runtime CSV callsites should be migrated.\n\n"+
"Every edge requires evidence: provider, segment, security_id, exchange timestamp, ingest timestamp, run_id, schema version, payload checksum, data status.\n",encoding="utf-8")
(OUT/"OPTION_CHAIN_PRODUCER_CONSUMER.md").write_text(
"# Option chain producer/consumer validation\n\n"+
"Candidate source modules: "+str(len(source_rows))+". Source-level matches do not prove producer availability.\n\n"+
"Producer acceptance: authorized Dhan response, current expiry/strike security ID, data plan entitlement, response timestamp, raw sanitized artifact and receipt hash.\n"+
"Consumer acceptance: live chain dataset ID, source/age/status, option-side symmetry, bid-ask, LTP, OI and expiry validation; trace to scanner/API/visible UI row.\n"+
"Failure gate: no verified producer -> NO VERIFIED LIVE DATA; no fallback CSV presented as fresh exchange response.\n"+
"See SOURCE_CLASSIFICATION.csv and STATIC_KEYWORD_HITS.csv for candidate file/line locations.\n",encoding="utf-8")
(OUT/"FORENSIC_REALITY_REPORT.md").write_text(
"# Genesis System3 forensic source reality audit\n\nUTC: "+stamp+"\nGit: "+branch+" "+sha+
"\nSource files scanned: "+str(len(files))+"\nPartial/unreadable/oversized: "+str(len(skips))+"\n"+
"\n## Static reference counts (not runtime execution)\n"+
"\n".join("- "+kind+": "+str(counts[kind]) for kind in regexes)+
"\n\n## Limitations\n"+
"Any UNKNOWN source must remain BLOCKED for production certification; only explicit source receipts support REAL_VERIFIED.\n"+
"Hits for mock, fake, demo, fallback can be tests and safety checks. Review actual function and context before calling them defects.\n"+
"CSV read/write match might be offline training or export rather than runtime ingestion.\n"+
"No authenticated exchange packet, consumer-run trace, model evidence, or cloud deployment observed in this audit.\n"+
"Do not use historical 1872/1872 self-generated PASS marks for independent certification.\n"+
"\n## Required next work\n"+
"1. Match live option-chain API producer to exact entrypoint, cache contract, scanner and dashboard consumers.\n"+
"2. Implement fail-closed provenance contract and test stale/unknown source handling.\n"+
"3. Migrate one proved live CSV reader at a time after benchmark and rollback tests.\n"+
"4. Compare actual storage/live paths, schema, timestamps, symbol IDs and market-close data.\n"+
"5. Capture reproducible provider->API->UI receipts and only then certify.\n",encoding="utf-8")
(OUT/"STORAGE_MIGRATION_PLAN.md").write_text(
"# Storage migration control plan\n\n"+
"Do not delete every CSV. CSV is valid for exports, exchange instrument master, reports and historical/offline input.\n"+
"Use authenticated hot-cache TTL and a durable event/Parquet pipeline; choose DuckDB for controlled analytical workloads or ClickHouse if scalable concurrent ingestion is independently justified.\n"+
"Before changing source code: map read sites, owners and schema; test duplicate, out-of-order, missing fields and stale feeds; verify exact source IDs; migrate one consumer behind an adapter and retain rollback.\n"+
"Never certify a new database alone as proof of real market data.\n",encoding="utf-8")
print(json.dumps(summary,indent=2))
print("REPORT_DIRECTORY",OUT)
