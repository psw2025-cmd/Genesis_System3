import { useEffect, useState } from 'react'
import axios from 'axios'
import { API_BASE, API_HEADERS } from '../config'

type GenesisState = {
  brief?: any
  brain?: any
  lab?: any
  monitor?: any
  hunger?: any
  truth?: any
  health?: any
  system?: any
  final?: any
  control?: any
  loading: boolean
  error?: string
}

const card: React.CSSProperties = {
  background: 'var(--surface-2)',
  border: '1px solid var(--border)',
  borderRadius: 8,
  padding: 16,
}

const small: React.CSSProperties = { color: 'var(--text-mut)', fontSize: 12, lineHeight: 1.5 }
const title: React.CSSProperties = { color: 'var(--text-primary)', fontSize: 13, fontWeight: 800, marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.04em' }

async function getData(path: string) {
  const res = await axios.get(`${API_BASE}${path}`, { headers: API_HEADERS })
  return res.data?.data ?? res.data
}

function Metric({ label, value, tone }: { label: string; value: any; tone?: 'up' | 'down' | 'warn' | 'accent' }) {
  const color = tone === 'up' ? 'var(--up)' : tone === 'down' ? 'var(--down)' : tone === 'warn' ? 'var(--warn)' : tone === 'accent' ? 'var(--accent)' : 'var(--text-primary)'
  return (
    <div style={card}>
      <div style={{ ...small, textTransform: 'uppercase', fontWeight: 700 }}>{label}</div>
      <div className="num" style={{ color, fontSize: 24, fontWeight: 900, marginTop: 6 }}>{String(value ?? '--')}</div>
    </div>
  )
}

function Section({ heading, children }: { heading: string; children: React.ReactNode }) {
  return <section style={card}><div style={title}>{heading}</div>{children}</section>
}

function Checklist({ items }: { items: string[] }) {
  return <div style={{ display: 'grid', gap: 8 }}>{(items || []).map((x, i) => (
    <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', color: 'var(--text-primary)', fontSize: 13 }}>
      <span style={{ color: 'var(--up)', fontWeight: 900 }}>✓</span><span>{x}</span>
    </div>
  ))}</div>
}

function JsonBlock({ data }: { data: any }) {
  return <pre style={{ ...small, background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 6, padding: 12, overflow: 'auto', maxHeight: 240 }}>{JSON.stringify(data ?? {}, null, 2)}</pre>
}

export function GenesisTab() {
  const [state, setState] = useState<GenesisState>({ loading: true })

  const load = async () => {
    setState(s => ({ ...s, loading: true, error: undefined }))
    try {
      const [brief, brain, lab, monitor, hunger, truth, health, system, final] = await Promise.all([
        getData('/genesis-production-brief'),
        getData('/autonomous-brain'),
        getData('/hidden-secrets-lab'),
        getData('/never-die-monitor'),
        getData('/hunger-meter'),
        getData('/data-truth-score'),
        getData('/health'),
        getData('/api/system_health'),
        getData('/final-message'),
      ])
      setState({ brief, brain, lab, monitor, hunger, truth, health, system, final, loading: false })
    } catch (e: any) {
      setState({ loading: false, error: e?.response?.data?.detail || e?.message || 'Genesis APIs failed' })
    }
  }

  useEffect(() => { load() }, [])

  const requestControl = async () => {
    try {
      const res = await axios.post(`${API_BASE}/agent-full-control`, { requested_from_ui: true, source: 'react_ui' }, { headers: API_HEADERS })
      setState(s => ({ ...s, control: res.data?.data ?? res.data }))
    } catch (e: any) {
      setState(s => ({ ...s, control: { error: e?.message || 'request failed' } }))
    }
  }

  const speak = () => {
    try { window.speechSynthesis?.speak(new SpeechSynthesisUtterance('Alert: Genesis opportunity monitor is active.')) } catch {}
  }

  if (state.loading) return <div style={{ padding: 24, color: 'var(--text-mut)' }}>Genesis is loading production command intelligence...</div>
  if (state.error) return <div style={{ padding: 24 }}><div style={{ ...card, borderColor: 'var(--down)', color: 'var(--down)' }}>{state.error}</div></div>

  const marketOpen = state.health?.market_status === 'open' || state.health?.market?.is_open
  const sources = state.brief?.sources || []
  const secrets = state.lab?.items || []

  return (
    <div style={{ height: '100%', overflowY: 'auto', padding: 24, display: 'grid', gap: 18 }}>
      <div style={{ ...card, borderColor: 'var(--accent)', background: 'linear-gradient(135deg, rgba(245,158,11,0.12), var(--surface-2))' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
          <div>
            <div style={{ color: 'var(--accent)', fontSize: 12, fontWeight: 900, letterSpacing: '0.08em' }}>GENESIS PRODUCTION COMMAND CENTER</div>
            <h1 style={{ color: 'var(--text-primary)', margin: '6px 0 4px', fontSize: 28 }}>AI Options Automation Dashboard</h1>
            <div style={small}>One official UI for broker status, prediction quality, gain ranking, risk gates, research, and self-healing intelligence.</div>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button onClick={load} style={{ padding: '10px 14px', borderRadius: 6, border: '1px solid var(--border)', background: 'var(--surface-3)', color: 'var(--text-primary)', fontWeight: 800 }}>Refresh</button>
            <button onClick={speak} style={{ padding: '10px 14px', borderRadius: 6, border: '1px solid var(--accent)', background: 'transparent', color: 'var(--accent)', fontWeight: 800 }}>Voice Alert</button>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: 12 }}>
        <Metric label="Operating Mode" value={state.brief?.mode || (marketOpen ? 'MARKET OPEN' : 'OFF MARKET')} tone="accent" />
        <Metric label="Broker" value={state.health?.broker_status || '--'} tone={state.health?.broker_status === 'connected' ? 'up' : 'warn'} />
        <Metric label="Truth Score" value={`${state.truth?.truth_score ?? 0}%`} tone="warn" />
        <Metric label="Memory Events" value={state.brain?.memory_events ?? 0} tone="up" />
        <Metric label="Live Trading" value={state.health?.live_allowed ? 'ALLOWED' : 'BLOCKED'} tone="down" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 18 }}>
        <Section heading={marketOpen ? 'Market Open: Trader Must See' : 'Off-Market: Trader Must See'}>
          <Checklist items={marketOpen ? state.brief?.market_open_must_show : state.brief?.off_market_must_show} />
        </Section>

        <Section heading="Prediction Accuracy & Gain Rank Requirements">
          <div style={{ display: 'grid', gap: 10 }}>
            <Metric label="Accuracy Goal" value={`${state.hunger?.accuracy_goal_pct ?? 90}%`} tone="accent" />
            <div style={small}>Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.</div>
            <div style={{ color: 'var(--warn)', fontSize: 13, fontWeight: 700 }}>Current blocker: {state.hunger?.need_to_fix || 'Need multi-day proof rows.'}</div>
          </div>
        </Section>

        <Section heading="Global Research Sources Integrated">
          <div style={{ display: 'grid', gap: 10 }}>
            {sources.map((s: any, i: number) => (
              <a key={i} href={s.url} target="_blank" rel="noreferrer" style={{ color: 'var(--text-primary)', textDecoration: 'none', border: '1px solid var(--border)', borderRadius: 6, padding: 10, background: 'var(--surface)' }}>
                <div style={{ fontWeight: 800 }}>{s.name}</div>
                <div style={small}>{s.use}</div>
              </a>
            ))}
          </div>
        </Section>

        <Section heading="Hidden Secrets Lab">
          <div style={{ display: 'grid', gap: 10 }}>
            {secrets.map((item: any, idx: number) => (
              <div key={idx} style={{ border: '1px solid var(--border)', borderRadius: 6, padding: 10, background: 'var(--surface)' }}>
                <div style={{ color: 'var(--text-primary)', fontWeight: 800, fontSize: 13 }}>{item.secret}</div>
                <div style={small}>Verified: {String(item.verified)} | Impact: {item.profit_impact}</div>
              </div>
            ))}
          </div>
        </Section>

        <Section heading="Integration Map">
          <div style={{ display: 'grid', gap: 10 }}>
            {(state.brief?.integration_map || []).map((x: any, i: number) => (
              <div key={i} style={{ borderLeft: '3px solid var(--accent)', paddingLeft: 10 }}>
                <div style={{ color: 'var(--text-primary)', fontWeight: 900 }}>{x.layer}</div>
                <div style={small}>Current: {x.current}</div>
                <div style={small}>Next: {x.next}</div>
              </div>
            ))}
          </div>
        </Section>

        <Section heading="Never Die Monitor">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 10 }}>
            <Metric label="Uptime Seconds" value={state.monitor?.uptime_seconds ?? 0} />
            <Metric label="Last Self-Heal" value={state.monitor?.last_self_heal ?? '--'} tone="up" />
            <Metric label="Issues Fixed" value={state.monitor?.issues_fixed_without_human ?? 0} tone="up" />
          </div>
        </Section>
      </div>

      <Section heading="Truth, Compliance, And Control">
        <div style={{ display: 'grid', gap: 12 }}>
          <div style={{ color: 'var(--down)', fontWeight: 900 }}>Kill switch visible: live trading remains disabled until all proof gates pass.</div>
          <button onClick={requestControl} style={{ width: 260, padding: '12px 14px', borderRadius: 6, border: '1px solid var(--down)', background: 'rgba(255,77,109,0.12)', color: 'var(--down)', fontWeight: 900 }}>Let Agent Take Full Control</button>
          <JsonBlock data={state.control || state.final} />
        </div>
      </Section>
    </div>
  )
}
