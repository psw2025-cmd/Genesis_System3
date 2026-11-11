#!/bin/bash
# Genesis System3 - READ-ONLY forensic. Kuch badalta nahi. Output: /tmp/f2.txt
cd /workspaces/Genesis_System3 || { echo "repo folder nahi mila"; exit 1; }
source .venv312/bin/activate 2>/dev/null
export PATH="$PWD/google-cloud-sdk/bin:$PATH"
export P=system3-openalgo-safe R=asia-south1 S=genesis-system3-web
U=https://genesis-system3-web-doq2wplepa-el.a.run.app
EX="--exclude-dir=google-cloud-sdk --exclude-dir=.venv312 --exclude-dir=node_modules --exclude-dir=.git"
g(){ timeout 90 gcloud "$@"; }
mask(){ sed -E "s/eyJ[A-Za-z0-9._-]{20,}/<JWT>/g; s/((token|secret|password|pin)[\"': =]+)[^ ,\"']{8,}/\1<MASKED>/Ig"; }
sec(){ echo; echo "=================== $1 ==================="; }
export TOK=$(gcloud auth print-access-token 2>/dev/null)
{
sec "G0 BASICS"
date; pwd; which gcloud 2>&1; [ -x "$PWD/google-cloud-sdk/bin/gcloud" ] && echo "gcloud binary: OK" || echo "WARNING: google-cloud-sdk/bin/gcloud nahi mila"

sec "G1 GCLOUD LOGIN / PROJECT"
gcloud --version 2>&1 | head -2; g auth list 2>&1 | head -5; g config list 2>&1
g projects describe $P --format="value(projectId,lifecycleState)" 2>&1 | head -3

sec "G2 CLOUD RUN SERVICE (env ke naam, secret hidden)"
g run services describe $S --region $R --project $P --format=json > /tmp/svc.json 2> /tmp/svc.err
python3 - <<'PY'
import json,sys
try: d=json.load(open('/tmp/svc.json'))
except Exception as e:
    print('NO JSON:',e); print(open('/tmp/svc.err').read()[:1000]); sys.exit()
md=d.get('metadata',{}); sp=d.get('spec',{}); st=d.get('status',{})
print('service',md.get('name'),'| url',st.get('url'))
print('latestReady',st.get('latestReadyRevisionName'),'| latestCreated',st.get('latestCreatedRevisionName'))
for c in st.get('conditions',[]): print(' cond',c.get('type'),c.get('status'),str(c.get('message',''))[:200])
print('ingress',md.get('annotations',{}).get('run.googleapis.com/ingress'))
t=sp.get('template',{}); ta=t.get('metadata',{}).get('annotations',{})
print('template annotations:',{k:v for k,v in ta.items() if any(x in k for x in ('scaling','cpu','startup','execution','vpc','cloudsql'))})
ts=t.get('spec',{})
print('timeout',ts.get('timeoutSeconds'),'| concurrency',ts.get('containerConcurrency'),'| serviceAccount',ts.get('serviceAccountName'))
bad=('TOKEN','PIN','SECRET','KEY','PASSWORD','CLIENT')
for c in ts.get('containers',[]):
    print('image',c.get('image')); print('resources',c.get('resources')); print('command',c.get('command'),c.get('args'))
    for e in c.get('env',[]):
        n=e.get('name','')
        if 'valueFrom' in e: print(' ENV',n,'= <from secret>')
        elif any(b in n.upper() for b in bad): print(' ENV',n,'= <hidden len',len(e.get('value','')),'>')
        else: print(' ENV',n,'=',str(e.get('value'))[:120])
    print('volumeMounts',c.get('volumeMounts'))
print('traffic',st.get('traffic'))
PY

sec "G3 REVISIONS (kaunsa code deploy hai)"
g run revisions list --service $S --region $R --project $P --limit 6 2>&1
sec "G4 URL PUBLIC HAI YA LOCKED (IAM)"
g run services get-iam-policy $S --region $R --project $P 2>&1 | head -15

sec "G5 CLOUD RUN JOBS"
g run jobs list --region $R --project $P 2>&1
sec "G6 CLOUD SCHEDULER (auto-run yahin se hota hai)"
g scheduler jobs list --location $R --project $P --format=json > /tmp/sch.json 2> /tmp/sch.err
python3 - <<'PY'
import json
try: L=json.load(open('/tmp/sch.json'))
except Exception as e:
    print('NO JSON:',e); print(open('/tmp/sch.err').read()[:800]); raise SystemExit
print('total scheduler jobs:',len(L))
for j in L:
    print('-',j.get('name','').split('/')[-1],'| sched',j.get('schedule'),j.get('timeZone'),'| state',j.get('state'))
    print('   last',j.get('lastAttemptTime'),'| status',j.get('status'),'| target',(j.get('httpTarget') or {}).get('uri'))
PY

sec "G7a CLOUD LOGS: WARNING/ERROR (2 din)"
g logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$S AND severity>=WARNING" --project $P --freshness=2d --limit=60 --format="value(timestamp,severity,textPayload,jsonPayload.message)" 2>&1 | cut -c1-400
sec "G7b CLOUD LOGS: keyword (model, validation, firestore, token)"
g logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$S AND (textPayload:\"Traceback\" OR textPayload:\"_loss\" OR textPayload:\"paper_validation\" OR textPayload:\"retrain\" OR textPayload:\"irestore\" OR textPayload:\"DH-9\" OR textPayload:\"weights\")" --project $P --freshness=2d --limit=40 --format="value(timestamp,severity,textPayload)" 2>&1 | cut -c1-400
sec "G7c CLOUD LOGS: sabse naye 40 (startup kaisa hai)"
g logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$S" --project $P --limit=40 --format="value(timestamp,severity,textPayload,jsonPayload.message)" 2>&1 | cut -c1-300

sec "G8 FIRESTORE (state yahan save ho raha hai?)"
python3 - <<'PY'
import os,json,urllib.request
P=os.environ['P'];T=os.environ.get('TOK','')
def call(url,data=None):
    r=urllib.request.Request(url,data=data,headers={'Authorization':'Bearer '+T,'Content-Type':'application/json'})
    return json.load(urllib.request.urlopen(r,timeout=30))
base='https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents'%P
try: ids=call(base+':listCollectionIds',b'{}').get('collectionIds',[])
except Exception as e: print('FIRESTORE FAIL',e); raise SystemExit
print('collections',ids)
for c in ids:
    try:
        docs=call(base+'/'+c+'?pageSize=300&mask.fieldPaths=_x').get('documents',[])
        ts=sorted(d.get('updateTime','') for d in docs)
        print(c,'| docs>=',len(docs),'| newest',ts[-1] if ts else None,'| oldest',ts[0] if ts else None)
    except Exception as e: print(c,'ERR',e)
PY

sec "G9 SECRETS (sirf naam aur latest version ki date, value nahi)"
for s in $(g secrets list --project $P --format="value(name)" 2>/dev/null | head -15); do n=${s##*/}; echo "$n :: $(g secrets versions list $n --project $P --limit=1 --format='value(name,state,createTime)' 2>&1 | head -1)"; done
sec "G10 BUCKETS"
g storage buckets list --project $P --format="value(name,location)" 2>&1 | head

sec "G11 LIVE URL (Codespace se)"
for p in /health /api/health /api/system/status; do echo "$p anon -> $(curl -s -o /tmp/r.txt -m 25 -w '%{http_code}' $U$p) | $(head -c 300 /tmp/r.txt | tr '\n' ' ')"; done
ID=$(gcloud auth print-identity-token 2>/dev/null)
for p in /health /api/health /api/system/status; do echo "$p with-login -> $(curl -s -o /tmp/r.txt -m 25 -w '%{http_code}' -H "Authorization: Bearer $ID" $U$p) | $(head -c 300 /tmp/r.txt | tr '\n' ' ')"; done
sec "G12 API ROUTES (health/status/paper/ml)"
grep -rnE '@(app|router)\.(get|post)\("[^"]*(health|status|paper|validation|gate|ml)[^"]*"' dashboard/backend --include=*.py | cut -c1-160 | head -40

sec "G13 GIT: DEPLOYED SHA b732bf0"
git fetch --all --tags --prune 2>&1 | tail -3
git cat-file -t b732bf0 2>&1; git branch -a --contains b732bf0 2>&1 | head -5
git log -1 --format="HEAD %h %cd %s"; git log --oneline -8
sec "G14 BUILD / DEPLOY FILES"
cat cloudbuild.yaml; echo ----; cat cloudbuild.recovery.yaml; echo ----
ls dashboard/backend/Dockerfile* 2>&1; sed -n 1,70p dashboard/backend/Dockerfile 2>&1
echo ---- requirements; grep -iE "scikit|numpy|xgboost|lightgbm|catboost|joblib|torch|pandas|jsonschema|firestore" requirements.txt dashboard/backend/requirements*.txt 2>&1 | head -30
sed -n 1,60p deploy/runner/entrypoint.sh 2>&1

sec "G15 LOCAL ML: VERSION + LOAD ERROR"
python -c "import sys,sklearn,numpy,joblib;print('py',sys.version.split()[0],'sklearn',sklearn.__version__,'numpy',numpy.__version__,'joblib',joblib.__version__)" 2>&1
pip list 2>/dev/null | grep -iE "scikit|numpy|pandas|xgboost|lightgbm|catboost|joblib|torch|fastapi|uvicorn|jsonschema|google-cloud"
cat core/models/dhan_real_blended/NIFTY_model_blended_v3_meta.json 2>&1
strings core/models/dhan_real_blended/NIFTY_model_blended_v3.pkl | grep -iE "_loss|sklearn\.|_sklearn_version" | head -8
python - <<'PY'
import pickle,traceback
for f in ["core/models/dhan_real_blended/NIFTY_model_blended_v3.pkl","core/models/dhan/NIFTY_rf.pkl","core/models/dhan/NIFTY_model.pkl","core/models/dhan_ultra/NIFTY_ultra_model.pkl"]:
    try:
        pickle.load(open(f,"rb")); print("OK  ",f)
    except Exception:
        print("FAIL",f); print(traceback.format_exc()[-500:])
PY
ls -la models 2>&1 | head; find . -name "xgboost_v1*" $EX 2>/dev/null | head

sec "G16 CODE LOGIC (kahan se kya aata hai)"
echo "--- model load karne wala code"; grep -rn "dhan_real_blended\|_model_blended_v3\|NOT_TRAINED" . --include=*.py $EX | grep -v tests | cut -c1-170 | head -20
echo "--- options_ml file kahan se"; sed -n 8760,8790p dashboard/backend/app.py
echo "--- accuracy tracker prediction source"; grep -nE "def |glob|\.jsonl|\.json|reports" scripts/system3_model_accuracy_tracker.py | cut -c1-150 | head -50
echo "--- Signals tab ka ML confidence kahan banta hai"; grep -rnE "BUY BULLISH|Gap-Up|Multi-Model|ml_consensus|gap_runner" dashboard --include=*.py --include=*.js --include=*.jsx --include=*.ts --include=*.tsx $EX --exclude-dir=dist --exclude-dir=build | cut -c1-170 | head -15
echo "--- GATES 4/7 STALE"; grep -nE "STALE|stale|GATES" dashboard/backend/auto_gates_service.py | cut -c1-170 | head -30
echo "--- paper validation kaun chalata hai"; grep -rn "run_paper_validation" . --include=*.py --include=*.yml --include=*.yaml --include=*.sh $EX | cut -c1-170 | head -15
sed -n 1,70p scripts/run_paper_validation.py

sec "G17 LOCAL SCHEDULER / PROCESSES"
cat state/scheduler_daemon.pid 2>&1; ps -ef | grep -iE "scheduler|uvicorn|gunicorn|retrain" | grep -v grep | head
tail -20 state/watchdog_runtime_status.json 2>&1

sec "G18 TESTS (jsonschema wala file chhod ke)"
timeout 280 python -m pytest tests -q --maxfail=40 --ignore=tests/evals/test_autonomous_e2e_runbook_contract.py -p no:cacheprovider 2>&1 | tail -70
echo; echo "SCRIPT_COMPLETE"
} 2>&1 | mask > /tmp/f2.txt
echo "FINISHED: $(wc -c < /tmp/f2.txt) bytes, $(wc -l < /tmp/f2.txt) lines  -> /tmp/f2.txt"
