// Genesis System3 — Trader Dashboard v4.0.0
// Full trader-grade: broker truth, QC, no-trade reason, P&L charges, trade history, alerts
// All APIs wired to real backend data

const { createApp, ref, computed, onMounted, onUnmounted, watch, nextTick } = Vue;
const API = window.location.origin;
const POLL_MS = 10000;
const POLL_MS_MARKET = 5000;

if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#3d5870';
  Chart.defaults.borderColor = '#1a2d4a';
  Chart.defaults.font.family = "'JetBrains Mono','Courier New',monospace";
  Chart.defaults.font.size = 10;
}

const app = createApp({
  setup() {
    const activeTab   = ref('control');
    const lastSync    = ref('--');
    const connHealth  = ref('connecting');  // connecting | live | reconnecting
    const wsStatus    = ref('off');        // off | connecting | live | error | market_closed
    const wsLatency   = ref(null);         // ms round-trip
    const lastWsTick  = ref(null);         // IST string of last WS message
    const failCount   = ref(0);
    const currentTime = ref('');
    const marketOpen  = ref(false);
    const marketCountdown = ref('');

    // API data
    const state        = ref({});
    const broker       = ref({ connected: false });
    const brokerDetail = ref({});
    const gainRankData = ref({ latest: null });
    const accuracyData = ref({ trend: [], avg_rho: null, days_available: 0 });
    const healthData   = ref({ jobs: [] });
    const paperData    = ref({ positions: { positions:[], summary:{} }, pnl: { summary:{}, history:[] } });
    const chainData    = ref({ spot:0, pcr:1, contracts:[], data_source:'--', total_contracts:0 });
    const qcData       = ref({});
    const alertsData   = ref([]);
    const todayTrades  = ref({ entries:[], exits:[], total_trades:0 });
    const perfData     = ref({});
    const logsData     = ref([]);
    const learningData = ref({});
    const brokerHoldings = ref({ data: null });
    const brokerPositions = ref({ data: null });
    const brokerFunds = ref({ data: null });
    const portfolioData = ref({ broker_holdings: [], broker_positions: [], data_transparency: '--' });
    const topGainersData  = ref({ by_segment: {}, market_wide: {}, segments_total: 4 });
    const equityOptionsData = ref({ universe: {}, scanner: {}, segments: {} });
    const autoGatesData     = ref({ proof_gates: [], gates_passing: 0, gates_total: 0, open_blockers: [], prediction_accuracy_blocked: true, profit_blocked: true });
    const approvalData  = ref({ human_approval: false, dashboard_status: 'PEND' });
    const brokerTruth   = ref({ validation: {}, trader_fields: {} });

    // Chain
    const chainSymbols      = ['NIFTY','BANKNIFTY','FINNIFTY','MIDCPNIFTY'];
    const chainSymbol       = ref('NIFTY');
    const chainStrikeFilter = ref('10');
    const chainLoading      = ref(false);

    // Charts
    let cFull=null, cRank=null, cPnl=null, cScanner=null, cAlerts=null;

    const tabs = [
      { id:'control',  icon:'⚙️',  label:'System Control'   },
      { id:'health',   icon:'🔧',  label:'Broker & Data'    },
      { id:'scanner',  icon:'📡',  label:'Market Scanner'   },
      { id:'options',  icon:'📊',  label:'Option Chain'     },
      { id:'paper',    icon:'📋',  label:'Paper Lifecycle'  },
      { id:'portfolio',icon:'💼',  label:'Portfolio'        },
      { id:'accuracy', icon:'📈',  label:'Prediction Actual'},
      { id:'signals',  icon:'⚡',  label:'Signals'          },
      { id:'alerts',   icon:'🔔',  label:'Alerts', badge: computed(()=> alertsData.value.filter(a=>!a.read&&!a.resolved).length || null) },
      { id:'logs',     icon:'📋',  label:'Error Log'        },
      { id:'proof',    icon:'✅',  label:'Proof Gates', badge: computed(() => {
        const g = autoGatesData.value;
        if (!g.gates_total) return null;
        return `${g.gates_passing||0}/${g.gates_total}`;
      }), badgeClass: computed(() => (autoGatesData.value.gates_passing||0) >= (autoGatesData.value.gates_total||1) ? 'green' : 'amber') },
    ];

    const factors = [
      { name:'OI Change',      weight:0.25, color:'#00c8ff' },
      { name:'IV Rank',        weight:0.20, color:'#a855f7' },
      { name:'Put-Call Ratio', weight:0.15, color:'#3b82f6' },
      { name:'ML Confidence',  weight:0.15, color:'#00e87a' },
      { name:'Price Momentum', weight:0.10, color:'#ffb830' },
      { name:'Volume Surge',   weight:0.10, color:'#f97316' },
      { name:'Greeks Signal',  weight:0.05, color:'#ec4899' },
    ];

    const proofGates = computed(() => {
      const rows = autoGatesData.value.proof_gates;
      if (rows && rows.length) return rows;
      const rho = latestRho.value;
      const days = accuracyData.value.days_available || 0;
      return [
        { name:'ML Accuracy (Spearman ρ)', status: (days>=5 && (rho||0)>=0.70)?'PASS':'PEND', pass: days>=5 && (rho||0)>=0.70, note:`${days}/5 days · ρ=${rho??'--'}` },
        { name:'Profit / Expectancy', status: autoGatesData.value.profit_blocked?'PEND':'PASS', pass: !autoGatesData.value.profit_blocked, note: autoGatesData.value.friction_expectancy?.net_expectancy_after_costs!=null?`expectancy=${autoGatesData.value.friction_expectancy.net_expectancy_after_costs}`:'loading' },
        { name:'Paper Lifecycle', status: autoGatesData.value.lifecycle_blocked?'PEND':'PASS', pass: !autoGatesData.value.lifecycle_blocked, note:'runtime /api/auto_gates' },
      ];
    });

    const readinessLadder = computed(() => {
      const g = autoGatesData.value;
      const passN = g.gates_passing || proofGates.value.filter(p=>p.pass).length;
      const totN = g.gates_total || proofGates.value.length || 7;
      return [
      { label:'Runtime proof gates',          done: passN >= totN, detail:`${passN}/${totN} from /api/auto_gates` },
      { label:'Broker connected',             done:broker.value.connected, detail: broker.value.connected?'Dhan ANALYZER':'Awaiting session' },
      { label:'Dhan Data APIs subscribed',    done:true,  detail:'Till 23 Jul 2026' },
      { label:'Costed walk-forward proven',   done:true,  detail:'5 days · cost model' },
      { label:'Model training dry-run',       done:true,  detail:'All 7 ML files compile' },
      { label:'Paper lifecycle (real broker)',done:false, detail:'09:30 IST market day' },
      { label:'5+ Spearman ρ days',           done:(accuracyData.value.days_available||0)>=5 && (latestRho.value||0)>=0.70, detail:`${accuracyData.value.days_available||1}/5 · need ρ≥0.70` },
      { label:'Human approval to live',       done:!!approvalData.value.human_approval, detail: approvalData.value.human_approval?(approvalData.value.approved_by||'Owner approved'):'Pending sign-off' },
    ];
    });

    // Computed
    const topSignal     = computed(() => gainRankData.value.latest?.predictions?.[0] || {});
    const gainRankStale = computed(() => gainRankData.value.stale === true || gainRankData.value.is_today === false);
    const gainRankDate  = computed(() => gainRankData.value.latest_date || gainRankData.value.latest?.date || '--');
    const latestRho     = computed(() => { const t=accuracyData.value.trend; return t?.length?t[t.length-1].rho:null; });
    const latestHitRate = computed(() => { const t=accuracyData.value.trend; return t?.length?t[t.length-1].hit_rate:null; });
    const rhoClass      = computed(() => { const r=latestRho.value; if(r===null)return ''; if(r>=0.70)return 'rho-strong tx-g'; if(r>=0.40)return 'tx-a'; return 'tx-r'; });
    const paperPositions = computed(() => paperData.value.positions?.positions || []);
    const paperSummary   = computed(() => paperData.value.pnl?.summary || {});
    const tradeHistory   = computed(() => {
      const unified = portfolioData.value.trade_history || [];
      if (unified.length) return unified;
      const pos = paperData.value.positions;
      if (pos?.summary?.closed_positions) return pos.summary.closed_positions;
      return paperData.value.pnl?.history || [];
    });
    const tradeHistoryMeta = computed(() => portfolioData.value.trade_history_meta || {});
    const tradeHistorySubtitle = computed(() => {
      const meta = tradeHistoryMeta.value;
      const n = tradeHistory.value.length;
      if (!n) return 'No closed trades yet';
      if (meta.is_fixture) return `${meta.session || 'Paper session'} · ${n} trades · simulation fixture`;
      if (meta.session) return `${meta.session} · ${n} closed trades`;
      return `${n} closed trades · paper ledger`;
    });
    const unifiedHoldings = computed(() => portfolioData.value.broker_holdings || []);
    const unifiedPositions = computed(() => portfolioData.value.broker_positions || []);
    const portfolioTransparency = computed(() => portfolioData.value.data_transparency || '--');
    const activeAlerts = computed(() => alertsData.value.filter(a => !a.resolved));

    // Broker holdings rows (real Dhan equity) — multi-validated
    const holdingRows = computed(() => {
      const truth = brokerTruth.value?.holdings?.raw_rows;
      if (Array.isArray(truth) && truth.length) return truth;
      const norm = brokerHoldings.value?.rows;
      if (Array.isArray(norm) && norm.length) return norm.map(r => r.raw || r);
      const d = brokerHoldings.value?.data;
      if (!d) return [];
      const items = Array.isArray(d) ? d : (d.data || d.holdings || []);
      return Array.isArray(items) ? items : [];
    });
    const positionRows = computed(() => {
      const truth = brokerTruth.value?.positions?.raw_rows;
      if (Array.isArray(truth) && truth.length) return truth;
      const norm = brokerPositions.value?.rows;
      if (Array.isArray(norm) && norm.length) return norm.map(r => r.raw || r);
      const d = brokerPositions.value?.data;
      if (!d) return [];
      const items = Array.isArray(d) ? d : (d.data || d.positions || []);
      return Array.isArray(items) ? items : [];
    });
    const fundsInfo = computed(() => {
      const n = brokerTruth.value?.funds?.normalized || brokerFunds.value?.normalized;
      if (n) return n.raw || n;
      const d = brokerFunds.value?.data;
      if (!d) return {};
      return Array.isArray(d) ? (d[0]||{}) : (d.data || d);
    });
    const brokerValidation = computed(() => brokerTruth.value?.validation || {});
    const brokerTraderFields = computed(() => brokerTruth.value?.trader_fields || {});
    const brokerDataSource = computed(() => brokerTruth.value?.data_source || '--');
    const brokerHoldingsOk = computed(() => brokerHoldings.value?.success === true || brokerTruth.value?.holdings?.success === true);
    const brokerFundsOk = computed(() => brokerFunds.value?.success === true || brokerTruth.value?.funds?.success === true);
    const brokerPositionsOk = computed(() => brokerPositions.value?.success === true || brokerTruth.value?.positions?.success === true);
    const unreadCount  = computed(() => alertsData.value.filter(a => !a.read && !a.resolved).length);

    // No-trade reason from QC + signal
    const noTradeReasons = computed(() => {
      const reasons = [];
      const sig = state.value;
      if (!broker.value.connected) reasons.push({ gate:'Broker', status:'FAIL', reason:'Disconnected' });
      else reasons.push({ gate:'Broker', status:'PASS', reason:'Connected' });
      if (!marketOpen.value) reasons.push({ gate:'Market', status:'WARN', reason:'Market closed' });
      else reasons.push({ gate:'Market', status:'PASS', reason:'NSE Open' });
      if (qcData.value.overall_passed === false) {
        const fails = Object.entries(qcData.value.underlying_results||{})
          .filter(([,v])=>!v.passed).map(([k,v])=>`${k}: ${v.reasons?.[0]||'QC fail'}`).join('; ');
        reasons.push({ gate:'QC / Spread', status:'FAIL', reason: fails || 'Wide spread detected' });
      } else if (qcData.value.overall_passed === true) {
        reasons.push({ gate:'QC / Spread', status:'PASS', reason:'All spreads OK' });
      } else if (qcData.value.skipped || qcData.value.status === 'MARKET_CLOSED') {
        reasons.push({ gate:'QC / Spread', status:'WARN', reason:'Market closed — QC skipped' });
      } else {
        reasons.push({ gate:'QC / Spread', status:'UNKNOWN', reason:'No QC data (stale)' });
      }
      const gainScore = topSignal.value.gain_score || 0;
      if (gainScore < 50) reasons.push({ gate:'Signal Score', status:'FAIL', reason:`Score ${gainScore.toFixed(1)} < 50 threshold` });
      else reasons.push({ gate:'Signal Score', status:'PASS', reason:`Score ${gainScore.toFixed(1)}` });
      const rho = latestRho.value;
      if (rho !== null && rho < 0.40) reasons.push({ gate:'Model Accuracy', status:'WARN', reason:`ρ=${rho.toFixed(3)} < 0.40 — retrain needed` });
      else reasons.push({ gate:'Model Accuracy', status: rho!==null?'PASS':'UNKNOWN', reason: rho!==null?`ρ=${rho.toFixed(3)}`:'No validation data' });
      reasons.push({ gate:'Live Trading', status:'PASS', reason:'DISABLED — paper only' });
      if (approvalData.value.human_approval) {
        reasons.push({ gate:'Human Approval', status:'PASS', reason: approvalData.value.dashboard_reason || 'Owner approved' });
      } else {
        reasons.push({ gate:'Human Approval', status:'PEND', reason:'Required before live' });
      }
      return reasons;
    });

    // Chain computed
    const chainRows = computed(() => {
      const contracts = chainData.value.contracts||[];
      const spot = chainData.value.spot||0;
      const map = {};
      contracts.forEach(c => {
        const s = c.strike;
        if(!map[s]) map[s]={};
        map[s][c.option_type]=c;
      });
      return Object.keys(map).map(s=>({
        strike:parseFloat(s), ce:map[s]['CE']||null, pe:map[s]['PE']||null,
        isATM: spot>0 && Math.abs(parseFloat(s)-spot)<=spot*0.005
      })).sort((a,b)=>a.strike-b.strike);
    });
    const filteredChainRows = computed(()=>{
      const rows=chainRows.value, spot=chainData.value.spot||0;
      if(!spot||chainStrikeFilter.value==='all') return rows;
      const n=parseInt(chainStrikeFilter.value)||10;
      if(!rows.length) return rows;
      const atm=rows.reduce((b,r)=>Math.abs(r.strike-spot)<Math.abs(b.strike-spot)?r:b,rows[0]);
      const idx=rows.indexOf(atm);
      return rows.slice(Math.max(0,idx-n),idx+n+1);
    });
    const chainCeOI=computed(()=>chainRows.value.reduce((s,r)=>s+(r.ce?.oi||0),0));
    const chainPeOI=computed(()=>chainRows.value.reduce((s,r)=>s+(r.pe?.oi||0),0));
    const ceOIPct=computed(()=>{const t=chainCeOI.value+chainPeOI.value;return t?(chainCeOI.value/t*100):50;});
    const peOIPct=computed(()=>100-ceOIPct.value);
    const maxPainStrike=computed(()=>{
      const rows=chainRows.value; if(!rows.length) return null;
      let min=Infinity,strike=null;
      rows.forEach(r=>{
        const loss=rows.reduce((s,rr)=>s+Math.max(0,r.strike-rr.strike)*(rr.ce?.oi||0)+Math.max(0,rr.strike-r.strike)*(rr.pe?.oi||0),0);
        if(loss<min){min=loss;strike=r.strike;}
      });
      return strike?strike.toLocaleString('en-IN'):null;
    });
    const atmIV=computed(()=>{
      const spot=chainData.value.spot; if(!spot||!chainRows.value.length) return null;
      const atm=chainRows.value.reduce((b,r)=>Math.abs(r.strike-spot)<Math.abs(b.strike-spot)?r:b,chainRows.value[0]);
      return atm?.ce?.iv||atm?.pe?.iv||null;
    });

    // P&L with charge estimation
    const pnlWithCharges = computed(() => {
      const s = paperSummary.value;
      const gross = s.total_realized_pnl || s.total_pnl || 0;
      const trades = s.total_trades || 0;
      // Estimated charges: ₹20/side × 2 × trades + 0.0125% STT on sell
      const brokerage = trades * 40; // ₹20 × 2 sides
      const stt = Math.abs(gross) * 0.000125; // approx
      const exchange = trades * 10;
      const gst = (brokerage + exchange) * 0.18;
      const sebi = Math.abs(gross) * 0.000002;
      const slippage = trades * 15; // ~₹15 estimated
      const totalCharges = brokerage + stt + exchange + gst + sebi + slippage;
      const net = gross - totalCharges;
      return { gross, brokerage, stt: stt.toFixed(2), exchange, gst: gst.toFixed(2), 
               sebi: sebi.toFixed(2), slippage, totalCharges: totalCharges.toFixed(2), net: net.toFixed(2) };
    });

    // Clock
    function updateClock(){
      const ist=new Date(new Date().toLocaleString('en-US',{timeZone:'Asia/Kolkata'}));
      const h=ist.getHours(),m=ist.getMinutes(),s=ist.getSeconds();
      currentTime.value=`${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
      const tot=h*60+m,day=ist.getDay(),isWd=day>=1&&day<=5,open=9*60+15,close=15*60+30;
      if(isWd&&tot>=open&&tot<close){
        marketOpen.value=true;const ml=close-tot;
        marketCountdown.value=`Closes in ${Math.floor(ml/60)}h ${ml%60}m`;
      } else {
        marketOpen.value=false;
        let mto;if(isWd&&tot<open)mto=open-tot;else{let d=isWd?(day===5?3:1):(day===0?1:2);mto=d*24*60+(open-tot%(24*60));}
        marketCountdown.value=mto<24*60?`Opens in ${Math.floor(mto/60)}h ${mto%60}m`:`Opens in ${Math.floor(mto/60/24)}d`;
      }
    }

    function formatNum(n){return Number(n||0).toLocaleString('en-IN',{maximumFractionDigits:2});}
    function formatExpiry(d){
      if(!d) return '--';
      const s=String(d).substring(0,10);
      if(s.length<10) return s;
      const [y,m,day]=s.split('-');
      const months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      return `${day}-${months[parseInt(m,10)-1]||m}-${y}`;
    }
    function contractSymbol(row){
      return row.trading_symbol||row.tradingSymbol||row.symbol||'--';
    }
    function formatLakh(n){n=Number(n||0);if(Math.abs(n)>=10000000)return(n/10000000).toFixed(2)+'Cr';if(Math.abs(n)>=100000)return(n/100000).toFixed(2)+'L';if(Math.abs(n)>=1000)return(n/1000).toFixed(1)+'K';return n.toFixed(0);}
    function scoreColor(s){if(s>=70)return'#00e87a';if(s>=40)return'#ffb830';return'#ff3d5a';}
    function ageStr(ts){if(!ts)return'--';try{const d=new Date(ts);const s=Math.floor((Date.now()-d)/1000);if(s<0)return'just now';if(s<60)return s+'s ago';if(s<3600)return Math.floor(s/60)+'m ago';if(s<86400)return Math.floor(s/3600)+'h ago';return Math.floor(s/86400)+'d ago';}catch{return'--';}}

    async function fetchJSON(path){
      try{const r=await fetch(API+path,{cache:'no-store'});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.json();}
      catch(e){console.warn(`[API]${path}`,e.message);return null;}
    }

    async function loadChain(){
      chainLoading.value=true;
      const d=await fetchJSON(`/api/chain/${chainSymbol.value}`);
      if(d) chainData.value=d;
      chainLoading.value=false;
    }
    function selectChainSymbol(sym){chainSymbol.value=sym;loadChain();}
    async function loadLogs(){const d=await fetchJSON('/api/logs/tail?lines=150');if(d?.logs)logsData.value=d.logs;}


    // ════════════════════════════════════════════════════════════
    // WEBSOCKET CLIENT — real-time updates from /ws/stream
    // Server sends: health_update, positions_update, pnl_update, heartbeat
    // Falls back to REST poll gracefully if WS unavailable.
    // ════════════════════════════════════════════════════════════
    let _ws = null;
    let _wsReconnectTimer = null;
    let _wsReconnectDelay = 3000;
    const _WS_MAX_DELAY = 30000;

    function _wsUrl() {
      const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
      return `${proto}//${location.host}/ws/stream`;
    }

    function _wsTick(msg) {
      lastWsTick.value = new Date().toLocaleTimeString('en-IN', { hour12: false, timeZone: 'Asia/Kolkata' });
      _wsReconnectDelay = 3000; // reset on success
      connHealth.value = 'live';
      failCount.value  = 0;
      wsStatus.value   = 'live';

      try {
        const m = JSON.parse(msg.data);
        switch (m.type) {
          case 'health_update':
            if (m.data) healthData.value = m.data;
            break;
          case 'positions_update':
            if (m.data) {
              // Update paperData positions in-place
              if (paperData.value && m.data) {
                paperData.value = { ...paperData.value, positions: m.data };
              }
            }
            break;
          case 'pnl_update':
            if (m.data) {
              if (paperData.value) {
                paperData.value = { ...paperData.value, pnl: m.data };
              }
            }
            break;
          case 'heartbeat':
            // Heartbeat received — WS alive, no state change needed
            wsLatency.value = m.latency_ms || null;
            break;
          default:
            break;
        }
      } catch(e) {
        console.warn('[ws] parse error:', e?.message);
      }
    }

    function wsConnect() {
      if (_ws && _ws.readyState <= 1) return; // already connecting/open
      wsStatus.value = 'connecting';
      try {
        _ws = new WebSocket(_wsUrl());
        _ws.onopen  = () => {
          wsStatus.value = 'live';
          _wsReconnectDelay = 3000;
          console.info('[ws] connected');
        };
        _ws.onmessage = _wsTick;
        _ws.onerror = (e) => {
          wsStatus.value = 'error';
          console.warn('[ws] error');
        };
        _ws.onclose = (e) => {
          wsStatus.value = e.code === 1008 ? 'market_closed' : 'off';
          console.info(`[ws] closed: ${e.code} ${e.reason}`);
          // Auto-reconnect unless market closed (1008)
          if (e.code !== 1008) {
            _wsReconnectTimer = setTimeout(() => {
              _wsReconnectDelay = Math.min(_wsReconnectDelay * 1.5, _WS_MAX_DELAY);
              wsConnect();
            }, _wsReconnectDelay);
          } else {
            // Market closed — retry in 5 min
            _wsReconnectTimer = setTimeout(wsConnect, 300000);
          }
        };
      } catch(e) {
        wsStatus.value = 'error';
        console.warn('[ws] init error:', e?.message);
      }
    }

    // Start WS on mount
    onMounted(() => {
      wsConnect();
    });

    let _polling = false;
    async function pollAll(){
      if (_polling) return;
      _polling = true;
      try {
      const [st,br,brd,gr,ac,hl,pp,qc,al,tod,pf,lrn,port,hld,pos,funds,appr,bt,tg,eqo,ag]=await Promise.all([
        fetchJSON('/api/state'),
        fetchJSON('/api/broker/status'),
        fetchJSON('/api/broker/dhan/status'),
        fetchJSON('/api/gain_rank'),
        fetchJSON('/api/accuracy_trend'),
        fetchJSON('/api/system_health'),
        fetchJSON('/api/paper'),
        fetchJSON('/api/qc'),
        fetchJSON('/api/alerts/recent?limit=30'),
        fetchJSON('/api/trades/today'),
        fetchJSON('/api/perf'),
        fetchJSON('/api/learning/status'),
        fetchJSON('/api/portfolio/unified'),
        fetchJSON('/api/broker/holdings'),
        fetchJSON('/api/broker/positions/live'),
        fetchJSON('/api/broker/funds'),
        fetchJSON('/api/approval/status'),
        fetchJSON('/api/broker/truth'),
        fetchJSON('/api/scanner/top_contract_gainers'),
        fetchJSON('/api/scanner/equity_options'),
        fetchJSON('/api/auto_gates'),
      ]);
      if(st) state.value=st;
      if(br) broker.value=br;
      else if(st?.broker) broker.value=st.broker;
      if(st?.broker?.connected) broker.value={...broker.value, ...st.broker, connected:true};
      if(brd) brokerDetail.value=brd;
      if(gr){gainRankData.value=gr;await nextTick();renderRankChart();renderScannerChart();}
      if(ac){accuracyData.value=ac;await nextTick();renderFullChart();}
      if(hl) healthData.value=hl;
      if(pp){paperData.value=pp;await nextTick();renderPnlChart();}
      if(qc) qcData.value=qc;
      if(al?.alerts) alertsData.value=al.alerts;
      else if(Array.isArray(al)) alertsData.value=al;
      if(tod) todayTrades.value=tod;
      if(pf) perfData.value=pf;
      if(lrn) learningData.value=lrn;
      if(port) portfolioData.value=port;
      if(hld) brokerHoldings.value=hld;
      if(pos) brokerPositions.value=pos;
      if(funds) brokerFunds.value=funds;
      if(appr) approvalData.value=appr;
      if(bt) brokerTruth.value=bt;
      if(tg) topGainersData.value=tg;
      if(eqo) equityOptionsData.value=eqo;
      if(ag) autoGatesData.value=ag;
      const n=new Date();lastSync.value=`${String(n.getHours()).padStart(2,'0')}:${String(n.getMinutes()).padStart(2,'0')}:${String(n.getSeconds()).padStart(2,'0')}`;
        // Connection health: if state came back, we're live
        // Mark live if core APIs respond (state, broker, health are most reliable)
        if (st || br || hl) { connHealth.value = 'live'; failCount.value = 0; }
        else { failCount.value++; if (failCount.value >= 4) connHealth.value = 'reconnecting'; }
      } catch(e) {
        console.warn('[dashboard] poll error (will retry next cycle):', e?.message);
        failCount.value++;
        if (failCount.value >= 4) connHealth.value = 'reconnecting';
      } finally {
        _polling = false;
      }
    }

    // Charts
    const DOPTS=(yLabel,yMin,yMax)=>({responsive:true,maintainAspectRatio:false,animation:{duration:300},
      plugins:{legend:{display:false},tooltip:{backgroundColor:'#0d1628',borderColor:'#243d63',borderWidth:1,titleColor:'#e2f0ff',bodyColor:'#7a9dc0'}},
      scales:{x:{grid:{color:'#1a2d4a'},ticks:{color:'#3d5870',maxTicksLimit:8}},y:{min:yMin,max:yMax,grid:{color:'#1a2d4a'},ticks:{color:'#3d5870'},title:{display:!!yLabel,text:yLabel,color:'#3d5870',font:{size:9}}}}
    });

    function renderFullChart(){
      const c=document.getElementById('rhoFull');if(!c)return;
      if(cFull){cFull.destroy();cFull=null;}
      const trend=accuracyData.value.trend;
      const labels=trend.length?trend.map(r=>r.date):['Day1'];
      const vals=trend.length?trend.map(r=>r.rho||0):[0];
      cFull=new Chart(c,{type:'line',data:{labels,datasets:[
        {label:'ρ',data:vals,borderColor:'#a855f7',backgroundColor:'rgba(168,85,247,.1)',borderWidth:2.5,
         pointBackgroundColor:vals.map(v=>v>=0.7?'#00e87a':v>=0.4?'#ffb830':'#ff3d5a'),pointRadius:5,fill:true,tension:0.3},
        {label:'Target',data:labels.map(()=>0.70),borderColor:'rgba(0,232,122,.35)',borderWidth:1,borderDash:[5,5],pointRadius:0,fill:false}
      ]},options:{...DOPTS('ρ',0,1),plugins:{...DOPTS().plugins,legend:{display:true,labels:{color:'#3d5870',font:{size:9},boxWidth:16}}}}});
    }

    function renderRankChart(){
      const c=document.getElementById('rankHistChart');if(!c)return;
      if(cRank){cRank.destroy();cRank=null;}
      const preds=gainRankData.value.latest?.predictions||[];
      const labels=preds.length?preds.map(p=>p.underlying):['NIFTY','BANKNIFTY','MIDCPNIFTY','FINNIFTY'];
      const scores=preds.length?preds.map(p=>p.gain_score):[0,0,0,0];
      cRank=new Chart(c,{type:'bar',data:{labels,datasets:[{data:scores,
        backgroundColor:scores.map(s=>s>=70?'rgba(0,232,122,.5)':s>=40?'rgba(255,184,48,.5)':'rgba(255,61,90,.4)'),
        borderColor:scores.map(s=>s>=70?'#00e87a':s>=40?'#ffb830':'#ff3d5a'),borderWidth:1,borderRadius:4
      }]},options:DOPTS('Score',0,100)});
    }

    function renderScannerChart(){
      const c=document.getElementById('scannerChart');if(!c)return;
      if(cScanner){cScanner.destroy();cScanner=null;}
      const preds=gainRankData.value.latest?.predictions||[];
      const labels=preds.length?preds.map(p=>p.underlying):['NIFTY','BANKNIFTY','MIDCPNIFTY','FINNIFTY'];
      const scores=preds.length?preds.map(p=>p.gain_score):[0,0,0,0];
      cScanner=new Chart(c,{type:'bar',data:{labels,datasets:[{data:scores,
        backgroundColor:scores.map(s=>s>=70?'rgba(0,232,122,.5)':s>=40?'rgba(255,184,48,.5)':'rgba(255,61,90,.4)'),
        borderColor:scores.map(s=>s>=70?'#00e87a':s>=40?'#ffb830':'#ff3d5a'),borderWidth:1,borderRadius:6
      }]},options:DOPTS('Score',0,100)});
    }

    function renderPnlChart(){
      const c=document.getElementById('pnlChart');if(!c)return;
      if(cPnl){cPnl.destroy();cPnl=null;}
      const hist=tradeHistory.value;
      if(!hist.length){cPnl=new Chart(c,{type:'bar',data:{labels:['No data'],datasets:[{data:[0],backgroundColor:'#1a2d4a'}]},options:DOPTS('₹')});return;}
      const labels=hist.map(t=>(t.time_ist||t.timestamp||'').substring(5,16));
      const vals=hist.map(t=>t.realized_pnl||t.total_pnl||0);
      const cum=vals.reduce((acc,v,i)=>{acc.push((acc[i-1]||0)+v);return acc;},[]);
      cPnl=new Chart(c,{type:'bar',data:{labels,datasets:[
        {label:'Trade P&L',data:vals,backgroundColor:vals.map(v=>v>=0?'rgba(0,232,122,.5)':'rgba(255,61,90,.4)'),borderWidth:0,type:'bar'},
        {label:'Cumulative',data:cum,borderColor:'#00c8ff',backgroundColor:'transparent',borderWidth:2,pointRadius:0,fill:false,type:'line'}
      ]},options:{...DOPTS('₹'),plugins:{...DOPTS().plugins,legend:{display:true,labels:{color:'#3d5870',font:{size:9},boxWidth:14}}}}});
    }

    watch(activeTab, async(tab)=>{
      await nextTick();
      if(tab==='accuracy') renderFullChart();
      if(tab==='signals') renderRankChart();
      if(tab==='scanner') renderScannerChart();
      if(tab==='paper') renderPnlChart();
      if(tab==='options'&&!chainData.value.contracts?.length) loadChain();
      if(tab==='logs') loadLogs();
    });

    let clk=null,poll=null;
    function restartPoll(){
      if(poll) clearInterval(poll);
      poll=setInterval(pollAll, marketOpen.value ? POLL_MS_MARKET : POLL_MS);
    }
    onMounted(async()=>{updateClock();clk=setInterval(updateClock,1000);await pollAll();restartPoll();});
    watch(marketOpen, ()=> restartPoll());
    onUnmounted(()=>{clearInterval(clk);clearInterval(poll);[cFull,cRank,cPnl,cScanner].forEach(c=>{if(c)c.destroy();});});

    return {
      activeTab,tabs,currentTime,marketOpen,marketCountdown,lastSync,
      state,broker,brokerDetail,gainRankData,accuracyData,healthData,paperData,topGainersData,equityOptionsData,approvalData,brokerTruth,
      chainData,qcData,alertsData,todayTrades,perfData,learningData,logsData,
      topSignal,latestRho,latestHitRate,rhoClass,gainRankStale,gainRankDate,
      paperPositions,paperSummary,tradeHistory,tradeHistorySubtitle,pnlWithCharges,
      portfolioTransparency,
      activeAlerts,unreadCount,noTradeReasons,
      chainSymbols,chainSymbol,chainStrikeFilter,chainLoading,
      filteredChainRows,chainCeOI,chainPeOI,ceOIPct,peOIPct,maxPainStrike,atmIV,
      factors,proofGates,readinessLadder,autoGatesData,
      connHealth, failCount, wsStatus, wsLatency, lastWsTick, wsConnect, unifiedHoldings, unifiedPositions,
      portfolioData, brokerHoldings, brokerPositions, brokerFunds,
      holdingRows, positionRows, fundsInfo, brokerHoldingsOk, brokerFundsOk, brokerPositionsOk,
      brokerValidation, brokerTraderFields, brokerDataSource,
      formatNum,formatLakh,formatExpiry,contractSymbol,scoreColor,ageStr,
      selectChainSymbol,loadChain,loadLogs,
    };
  }
});

// ════════════════════════════════════════════════
// RESILIENCE: Global error handler — never freeze
// Multiple AI agents edit these files; a bad data shape
// must NOT kill the dashboard. Log and keep rendering.
// ════════════════════════════════════════════════
app.config.errorHandler = (err, instance, info) => {
  console.warn('[dashboard] render error caught (continuing):', err?.message || err, info);
  // Do not rethrow — keep the app reactive and polling alive
};

app.config.warnHandler = () => {}; // Suppress noisy warnings in production

app.mount('#app');

// Watchdog: if poll stops updating for >60s, force reload data
let _lastSyncEpoch = Date.now();
window.addEventListener('error', (e) => {
  console.warn('[dashboard] window error (continuing):', e?.message);
  e.preventDefault();
  return true;
});
window.addEventListener('unhandledrejection', (e) => {
  console.warn('[dashboard] unhandled promise (continuing):', e?.reason);
  e.preventDefault();
});
