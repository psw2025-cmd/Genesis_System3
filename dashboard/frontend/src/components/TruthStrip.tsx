import { useEffect, useMemo, useState } from 'react'
import { useStore } from '../store'
import { shortSha } from '../lib/formatLive'
import type { StreamHealth } from '../lib/hydration'

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

const STREAM_LABEL: Record<StreamHealth, string> = {
  live: 'LIVE',
  degraded: 'DEGRADED',
  stale: 'STALE',
  offline: 'OFFLINE',
}

const STREAM_COLOR: Record<StreamHealth, string> = {
  live: 'var(--up)',
  degraded: 'var(--amber)',
  stale: 'var(--warn)',
  offline: 'var(--down)',
}

export function TruthStrip({ compact = false }: { compact?: boolean }) {
  const { deployInfo, brokerStatus, state, truthMeta } = useStore()
  const [ist, setIst] = useState(() => `${IST_FMT.format(new Date()).replace(', ', ' ')} IST`)

  useEffect(() => {
    const t = window.setInterval(() => {
      setIst(`${IST_FMT.format(new Date()).replace(', ', ' ')} IST`)
    }, 1000)
    return () => window.clearInterval(t)
  }, [])

  const streamHealth = (truthMeta?.streamHealth || 'offline') as StreamHealth
  const shaSynced = truthMeta?.shaSynced
  const brokerOk = brokerStatus?.connected === true
  const qc = String(state?.qc?.status || '—')
  const serving = shortSha(deployInfo?.git_sha)

  const syncBadge = useMemo(() => {
    if (shaSynced === true) return { text: 'SHA SYNC', color: 'var(--up)' }
    if (shaSynced === false) return { text: 'SHA DRIFT', color: 'var(--down)' }
    return { text: 'SHA —', color: 'var(--text-mut)' }
  }, [shaSynced])

  return (
    <div
      data-testid="truth-strip"
      role="status"
      aria-live="polite"
      className="truth-strip-neon"
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: compact ? '6px 10px' : '8px 16px',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: compact ? '6px 12px' : '8px 14px',
        fontFamily: 'var(--font-mono)',
        fontSize: 11,
        color: 'var(--text-sec)',
      }}
    >
      <span className="truth-strip-glow" style={{ fontWeight: 800, letterSpacing: '.04em' }}>
        <span style={{ color: STREAM_COLOR[streamHealth] }}>[{STREAM_LABEL[streamHealth]}]</span>
        {' | '}
        <span style={{ color: syncBadge.color }}>{syncBadge.text}</span>
        {' | Serving: '}
        <span style={{ color: 'var(--accent-2)' }}>{serving}</span>
        {' | QC: '}
        <span style={{ color: qc === 'PASS' ? 'var(--up)' : 'var(--amber)' }}>{qc}</span>
        {' | Broker: '}
        <span style={{ color: brokerOk ? 'var(--up)' : 'var(--text-mut)' }}>{brokerOk ? 'OK' : '—'}</span>
        {' | LIVE OFF'}
        {truthMeta?.circuitOpen ? ' | CIRCUIT OPEN' : ''}
        {truthMeta?.dataMode && truthMeta.dataMode !== 'live' ? ` | MODE:${truthMeta.dataMode.toUpperCase()}` : ''}
      </span>
      {!compact && <span className="truth-strip-clock">{ist}</span>}
    </div>
  )
}
