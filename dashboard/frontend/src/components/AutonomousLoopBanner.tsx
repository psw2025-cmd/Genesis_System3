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

export function AutonomousLoopBanner() {
  const { deployInfo, brokerStatus, gainRank, chain, state, autoGates } = useStore()
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

  if (!AUTONOMOUS_LOOP_BANNER_ENABLED) return null

  return (
    <div
      data-testid="autonomous-loop-banner"
      role="status"
      aria-live="polite"
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px 16px',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '8px 14px',
        borderBottom: '1px solid rgba(120,180,255,.3)',
        background: 'linear-gradient(90deg, rgba(10,36,64,.96), rgba(6,20,38,.98))',
        fontFamily: 'var(--font-mono, ui-monospace, monospace)',
        fontSize: 11,
        color: 'var(--text-sec)',
      }}
    >
      <span style={{ fontWeight: 800, color: gatesOk ? 'var(--up)' : 'var(--amber)', letterSpacing: '.03em' }}>
        [AUTONOMOUS LOOP] | Active Task: {task} | Progress: {resolved}/{total} | Gates: {passCount}/{proof.length || 7} | Build: {shortSha(deployInfo?.git_sha) || 'SHA_PENDING'}
      </span>
      <span>IST {ist}</span>
    </div>
  )
}
