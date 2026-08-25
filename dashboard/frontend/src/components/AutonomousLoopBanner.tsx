import { useMemo } from 'react'
import { useStore } from '../store'
import { TruthStrip } from './TruthStrip'

/** Temporary until all proof gates are genuinely READY (never faked). */
export const AUTONOMOUS_LOOP_BANNER_ENABLED = true

export function AutonomousLoopBanner() {
  const { gainRank, chain, state, autoGates, brokerStatus } = useStore()

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
      className="autonomous-loop-banner truth-strip-neon"
      style={{
        borderBottom: '1px solid rgba(120,180,255,.3)',
        background: 'linear-gradient(90deg, rgba(10,36,64,.96), rgba(6,20,38,.98))',
      }}
    >
      <TruthStrip />
      <div
        style={{
          padding: '4px 14px 8px',
          fontFamily: 'var(--font-mono)',
          fontSize: 11,
          color: gatesOk ? 'var(--up)' : 'var(--amber)',
          fontWeight: 700,
          letterSpacing: '.03em',
        }}
      >
        Task: {task} | Progress: {resolved}/{total} | Gates: {passCount}/{proof.length || 7}
      </div>
    </div>
  )
}
