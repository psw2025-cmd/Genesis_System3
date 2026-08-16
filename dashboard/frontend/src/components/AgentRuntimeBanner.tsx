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

function istNowLabel() {
  // en-CA yields YYYY-MM-DD, HH:mm:ss (comma variants normalized)
  return `${IST_FMT.format(new Date()).replace(', ', ' ')} IST`
}

type StepInfo = { step: number; total: number; task: string; tone: string }

function deriveStep(input: {
  brokerConnected: boolean
  brokerError?: string | null
  scannerSpotsOk: boolean
  modelEvidenceOk: boolean
  gatesReady: boolean
}): StepInfo {
  const total = 5
  if (!input.brokerConnected) {
    return {
      step: 1,
      total,
      task: `Broker auth lifecycle — ${input.brokerError || 'not connected'}`,
      tone: 'var(--down)',
    }
  }
  if (!input.scannerSpotsOk) {
    return { step: 2, total, task: 'Scanner / contract spot pipeline binding', tone: 'var(--amber)' }
  }
  if (!input.modelEvidenceOk) {
    return { step: 3, total, task: 'Model evidence / confidence / regime', tone: 'var(--amber)' }
  }
  if (!input.gatesReady) {
    return { step: 4, total, task: 'Proof-gate sequence (promotion still blocked)', tone: 'var(--amber)' }
  }
  return { step: 5, total, task: 'Local audit gate + continuous verify', tone: 'var(--up)' }
}

/**
 * Temporary live diagnostic banner for the 20-minute multi-agent cycle.
 * Steps are derived from live contracts — never invented PASS/READY.
 * Remove via DIAG_BANNER_ENABLED=false / component unmount after cycle.
 */
export const DIAG_BANNER_ENABLED = true

export function AgentRuntimeBanner() {
  const { deployInfo, brokerStatus, gainRank, chain, state, autoGates } = useStore()
  const [ist, setIst] = useState(istNowLabel)

  useEffect(() => {
    const t = window.setInterval(() => setIst(istNowLabel()), 1000)
    return () => window.clearInterval(t)
  }, [])

  const rankings = gainRank?.latest?.rankings ?? gainRank?.rankings ?? []
  const top = Array.isArray(rankings) ? rankings.slice(0, 6) : []
  const scannerSpotsOk = top.length > 0 && top.every((row: any) => {
    const u = String(row?.underlying || '').toUpperCase()
    const spot = row?.spot_price ?? chain?.[u]?.spot
    return Number(spot) > 0
  })
  const signals = state?.signals
  const modelEvidenceOk = Boolean(
    signals
    && String(signals.status || '').toUpperCase() !== 'NO_TRADE'
    && (signals.directional_bias || signals.bias || signals.last_signal)
    && Number(signals.confidence) > 0,
  )
  const proof = Array.isArray(autoGates?.proof_gates) ? autoGates.proof_gates : []
  const passCount = proof.filter((g: any) => g?.pass === true || String(g?.status).toUpperCase() === 'PASS').length
  const gatesReady = proof.length > 0 && passCount === proof.length

  const step = useMemo(
    () => deriveStep({
      brokerConnected: brokerStatus?.connected === true,
      brokerError: brokerStatus?.error,
      scannerSpotsOk,
      modelEvidenceOk,
      gatesReady,
    }),
    [brokerStatus?.connected, brokerStatus?.error, scannerSpotsOk, modelEvidenceOk, gatesReady],
  )

  const sha = shortSha(deployInfo?.git_sha) || 'SHA_PENDING'

  if (!DIAG_BANNER_ENABLED) return null

  return (
    <div
      data-testid="agent-runtime-banner"
      role="status"
      aria-live="polite"
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px 16px',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '8px 14px',
        background: 'linear-gradient(90deg, rgba(14,40,72,.95), rgba(8,22,40,.98))',
        borderBottom: '1px solid rgba(100,160,255,.28)',
        fontSize: 11,
        color: 'var(--text-sec)',
        fontFamily: 'var(--font-mono, ui-monospace, monospace)',
      }}
    >
      <span style={{ color: step.tone, fontWeight: 800, letterSpacing: '.04em' }}>
        [AGENT RUNTIME ACTIVE] | Step {step.step}/{step.total}: {step.task}
      </span>
      <span style={{ display: 'flex', flexWrap: 'wrap', gap: '10px 18px' }}>
        <span>IST {ist}</span>
        <span>UI Rendered SHA {sha}</span>
        <span>
          Gates {passCount}/{proof.length || 0}
          {gatesReady ? '' : ' · NOT_READY'}
        </span>
      </span>
    </div>
  )
}
