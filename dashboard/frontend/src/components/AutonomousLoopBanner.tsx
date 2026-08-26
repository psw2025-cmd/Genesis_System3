import { useEffect, useMemo, useState } from 'react'
import { useStore } from '../store'
import { shortSha } from '../lib/formatLive'

const IST_FMT = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Asia/Kolkata',
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hour12: false,
})

/** Temporary until all proof gates are genuinely READY (never faked). */
export const AUTONOMOUS_LOOP_BANNER_ENABLED = true

const QUICK_TABS: { id: string; label: string }[] = [
  { id: 'decision-intel', label: 'Decision' },
  { id: 'chain', label: 'Option Chain' },
  { id: 'options-intel', label: 'Options Intel' },
  { id: 'broker', label: 'Broker' },
  { id: 'data-integrity', label: 'Data Integrity' },
  { id: 'truth', label: 'Truth Control' },
  { id: 'prediction-audit', label: 'Prediction Audit' },
  { id: 'system', label: 'System' },
]

function Chip({
  label,
  value,
  tone,
}: {
  label: string
  value: string
  tone: 'ok' | 'warn' | 'bad' | 'mut'
}) {
  const color =
    tone === 'ok' ? 'var(--up)' : tone === 'warn' ? 'var(--amber)' : tone === 'bad' ? 'var(--down)' : 'var(--text-mut)'
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        padding: '4px 10px',
        borderRadius: 6,
        border: `1px solid ${color}`,
        background: 'rgba(0,0,0,.25)',
        fontFamily: 'var(--font-mono)',
        fontSize: 11,
        whiteSpace: 'nowrap',
      }}
    >
      <span style={{ color: 'var(--text-mut)', fontWeight: 600 }}>{label}</span>
      <span style={{ color, fontWeight: 800 }}>{value}</span>
    </span>
  )
}

export function AutonomousLoopBanner() {
  const {
    deployInfo, brokerStatus, gainRank, chain, state, autoGates, marketOpen, health, setActiveTab,
  } = useStore()
  const [ist, setIst] = useState(() => `${IST_FMT.format(new Date()).replace(', ', ' ')} IST`)

  useEffect(() => {
    const t = window.setInterval(() => {
      setIst(`${IST_FMT.format(new Date()).replace(', ', ' ')} IST`)
    }, 1000)
    return () => window.clearInterval(t)
  }, [])

  const proof = Array.isArray(autoGates?.proof_gates) ? autoGates.proof_gates : []
  const passCount = proof.filter((g: any) => g?.pass === true || String(g?.status).toUpperCase() === 'PASS').length
  const rankings = gainRank?.latest?.rankings ?? gainRank?.rankings ?? []
  const top = Array.isArray(rankings) ? rankings.slice(0, 6) : []
  const spotsOk = top.length > 0 && top.every((row: any) => {
    const u = String(row?.underlying || '').toUpperCase()
    const spot = Number(row?.spot_price ?? chain?.[u]?.spot)
    return Number.isFinite(spot) && spot > 0
  })
  const brokerOk = brokerStatus?.connected === true
  const modelOk = Boolean(
    state?.signals
    && String(state.signals.status || '').toUpperCase() !== 'NO_TRADE'
    && (state.signals.directional_bias || state.signals.bias || state.signals.last_signal)
    && Number(state.signals.confidence) > 0,
  )
  const gatesOk = proof.length > 0 && passCount === proof.length

  const { resolved, total, task } = useMemo(() => {
    const flags = [
      { ok: brokerOk, name: 'Broker auth session' },
      { ok: spotsOk, name: 'Gain-rank authenticated spot bind' },
      { ok: modelOk, name: 'Model evidence / directional bias' },
      { ok: gatesOk, name: 'All proof gates READY' },
    ]
    const resolvedCount = flags.filter((f) => f.ok).length
    const active = flags.find((f) => !f.ok)?.name || 'Continuous verify'
    return { resolved: resolvedCount, total: flags.length, task: active }
  }, [brokerOk, spotsOk, modelOk, gatesOk])

  const qcStatus = String(state?.qc?.status || health?.qc_status || '—').toUpperCase()
  const qcReasons = Array.isArray(state?.qc?.reasons) ? state.qc.reasons.map(String) : []
  const marketReason = String(state?.market?.reason || health?.market?.reason || (marketOpen ? 'Market open' : 'Market closed'))
  const nextOpen = String(state?.market?.next_open || health?.market?.next_open || '—')
  const serving = shortSha(deployInfo?.git_sha)
  const liveOn = Boolean(deployInfo?.live_trading_enabled || health?.live_allowed)

  if (!AUTONOMOUS_LOOP_BANNER_ENABLED) return null

  return (
    <div
      data-testid="autonomous-loop-banner"
      role="status"
      aria-live="polite"
      className="emergency-truth-board"
      style={{
        borderBottom: '1px solid rgba(245,165,36,.45)',
        background: marketOpen
          ? 'linear-gradient(90deg, rgba(6,40,28,.98), rgba(6,20,38,.98))'
          : 'linear-gradient(90deg, rgba(48,28,8,.98), rgba(18,12,28,.98))',
        padding: '10px 14px 12px',
      }}
    >
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, alignItems: 'center' }}>
          <span
            data-testid="market-session-badge"
            style={{
              fontFamily: 'var(--font-mono)',
              fontWeight: 900,
              fontSize: 13,
              letterSpacing: '.06em',
              padding: '6px 12px',
              borderRadius: 8,
              color: marketOpen ? 'var(--up)' : 'var(--amber)',
              border: `1px solid ${marketOpen ? 'var(--up)' : 'var(--amber)'}`,
              background: marketOpen ? 'rgba(24,215,130,.12)' : 'rgba(245,165,36,.14)',
            }}
          >
            {marketOpen ? 'MARKET OPEN' : 'MARKET CLOSED'}
          </span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-pri)', fontWeight: 700 }}>
            {marketReason}
          </span>
          {!marketOpen && (
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-sec)' }}>
              Next open: <strong style={{ color: 'var(--accent-2)' }}>{nextOpen}</strong>
            </span>
          )}
        </div>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-mut)' }}>{ist}</span>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 10 }}>
        <Chip label="BROKER" value={brokerOk ? 'OK' : 'WAITING'} tone={brokerOk ? 'ok' : 'warn'} />
        <Chip label="QC" value={qcStatus} tone={qcStatus === 'PASS' ? 'ok' : 'warn'} />
        <Chip label="SERVING" value={serving} tone={serving !== '—' ? 'ok' : 'mut'} />
        <Chip label="LIVE" value={liveOn ? 'ON' : 'OFF'} tone={liveOn ? 'bad' : 'ok'} />
        <Chip label="GATES" value={`${passCount}/${proof.length || 7}`} tone={gatesOk ? 'ok' : 'warn'} />
        <Chip label="TASK" value={`${resolved}/${total}`} tone={resolved === total ? 'ok' : 'warn'} />
      </div>

      <div
        style={{
          marginTop: 10,
          fontFamily: 'var(--font-mono)',
          fontSize: 11,
          color: 'var(--amber)',
          lineHeight: 1.45,
        }}
      >
        <strong>[LIVE TRUTH]</strong>
        {' · '}
        Blocking: {task}
        {qcReasons.length > 0 && (
          <>
            {' · '}
            QC why: <strong>{qcReasons.join(', ')}</strong>
            {!marketOpen && qcReasons.includes('NO_VERIFIED_CONTRACTS') && (
              <span style={{ color: 'var(--text-sec)' }}> (expected after hours — contracts re-verify after 09:15 IST)</span>
            )}
          </>
        )}
        {' · '}
        Mode: Read-only / poll · LIVE trading locked OFF
      </div>

      <div
        data-testid="truth-quick-tabs"
        style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 10 }}
      >
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-mut)', alignSelf: 'center' }}>
          OPEN TABS:
        </span>
        {QUICK_TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 11,
              fontWeight: 700,
              padding: '4px 10px',
              borderRadius: 6,
              border: '1px solid var(--border-hi)',
              background: 'rgba(59,140,255,.12)',
              color: 'var(--accent-2)',
              cursor: 'pointer',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  )
}
