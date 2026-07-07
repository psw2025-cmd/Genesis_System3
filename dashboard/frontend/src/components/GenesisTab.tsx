import { useEffect, useState } from 'react'
import axios from 'axios'
import { API_BASE, API_HEADERS } from '../config'

type ApiState = {
  brain?: any
  lab?: any
  monitor?: any
  hunger?: any
  truth?: any
  compliance?: any
  cost?: any
  final?: any
  control?: any
  error?: string
  loading: boolean
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="card p-5 space-y-3">
      <h3 className="text-sm font-semibold text-text-primary tracking-wide">{title}</h3>
      {children}
    </section>
  )
}

function Metric({ label, value, tone }: { label: string; value: any; tone?: 'up' | 'down' | 'warn' }) {
  const color = tone === 'up' ? 'text-up' : tone === 'down' ? 'text-down' : tone === 'warn' ? 'text-warn' : 'text-text-primary'
  return (
    <div className="rounded border border-border bg-surface-2 p-4 min-h-[88px]">
      <div className="text-xs uppercase text-text-muted mb-2">{label}</div>
      <div className={`num text-xl font-semibold ${color}`}>{String(value ?? '--')}</div>
    </div>
  )
}

function JsonBlock({ data }: { data: any }) {
  return (
    <pre className="text-xs text-text-muted bg-surface-2 border border-border rounded p-3 overflow-auto max-h-72">
      {JSON.stringify(data ?? {}, null, 2)}
    </pre>
  )
}

async function getData(path: string) {
  const res = await axios.get(`${API_BASE}${path}`, { headers: API_HEADERS })
  return res.data?.data ?? res.data
}

export function GenesisTab() {
  const [state, setState] = useState<ApiState>({ loading: true })

  const load = async () => {
    setState(s => ({ ...s, loading: true, error: undefined }))
    try {
      const [brain, lab, monitor, hunger, truth, compliance, cost, final] = await Promise.all([
        getData('/autonomous-brain'),
        getData('/hidden-secrets-lab'),
        getData('/never-die-monitor'),
        getData('/hunger-meter'),
        getData('/data-truth-score'),
        getData('/compliance-check'),
        getData('/cost-roi'),
        getData('/final-message'),
      ])
      setState({ brain, lab, monitor, hunger, truth, compliance, cost, final, loading: false })
    } catch (e: any) {
      setState({ loading: false, error: e?.response?.data?.detail || e?.message || 'Genesis API failed' })
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
    try {
      const text = 'Alert: New opportunity found. Genesis analyzer is active.'
      window.speechSynthesis?.speak(new SpeechSynthesisUtterance(text))
    } catch {}
  }

  if (state.loading) {
    return <div className="p-6 text-text-muted">Genesis is thinking...</div>
  }

  if (state.error) {
    return (
      <div className="p-6">
        <div className="card p-5 border-down text-down">{state.error}</div>
      </div>
    )
  }

  const secrets = Array.isArray(state.lab?.items) ? state.lab.items : []

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      <div className="card p-5 flex items-center justify-between gap-4">
        <div>
          <div className="text-xs uppercase text-text-muted">Autonomous Brain</div>
          <h2 className="text-xl font-bold text-text-primary">Genesis Command Intelligence</h2>
          <p className="text-sm text-text-muted mt-1">Analyzer/paper intelligence is active. Real-money execution remains blocked until proof gates pass.</p>
        </div>
        <button className="px-4 py-2 rounded bg-accent text-black font-semibold" onClick={load}>Refresh</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Metric label="Truth Score" value={`${state.truth?.truth_score ?? 0}%`} tone="warn" />
        <Metric label="Memory Events" value={state.brain?.memory_events ?? 0} tone="up" />
        <Metric label="Profit Goal" value="₹10L/month" />
        <Metric label="Live Trading" value={state.compliance?.live_trading_enabled === '1' ? 'ON' : 'OFF'} tone="down" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <Card title="What I Learned Today">
          <JsonBlock data={state.brain?.what_i_learned_today} />
          <div className="text-sm text-text-muted">Rule changed: {state.brain?.rule_i_changed ?? '--'}</div>
          <div className="text-sm text-warn">Profit claim: {state.brain?.profit_i_made_without_human ?? '--'}</div>
        </Card>

        <Card title="Hidden Secrets Lab">
          <div className="space-y-2">
            {secrets.map((item: any, idx: number) => (
              <div key={idx} className="border border-border rounded p-3 bg-surface-2">
                <div className="text-sm text-text-primary font-semibold">{item.secret}</div>
                <div className="text-xs text-text-muted mt-1">Verified: {String(item.verified)} | Impact: {item.profit_impact}</div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Never Die Monitor">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Metric label="Uptime Seconds" value={state.monitor?.uptime_seconds ?? 0} />
            <Metric label="Last Self-Heal" value={state.monitor?.last_self_heal ?? '--'} tone="up" />
            <Metric label="Issues Fixed" value={state.monitor?.issues_fixed_without_human ?? 0} tone="up" />
          </div>
          <JsonBlock data={state.monitor} />
        </Card>

        <Card title="Hunger Meter">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Metric label="Current Observed" value={`₹${state.hunger?.current_profit_observed ?? 0}`} />
            <Metric label="Accuracy Goal" value={`${state.hunger?.accuracy_goal_pct ?? 90}%`} />
          </div>
          <div className="text-sm text-warn">Need to fix: {state.hunger?.need_to_fix ?? '--'}</div>
          <JsonBlock data={state.cost} />
        </Card>
      </div>

      <Card title="Truth & Control">
        <div className="flex flex-wrap gap-3">
          <button className="px-4 py-2 rounded border border-border bg-surface-2" onClick={speak}>Voice Alert</button>
          <button className="px-4 py-2 rounded border border-down text-down bg-surface-2" onClick={requestControl}>Let Agent Take Full Control</button>
        </div>
        <div className="text-sm text-down">Kill switch visible: live trading remains disabled until proof gates pass.</div>
        <JsonBlock data={state.control ?? state.final} />
      </Card>
    </div>
  )
}
