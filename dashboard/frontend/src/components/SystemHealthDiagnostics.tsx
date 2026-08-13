import { brokerIsConnected, paperModeActive, systemRuntimeOk } from '../lib/healthTruth'
import { useStore } from '../store'
import { shortSha } from '../lib/formatLive'

/** Engineering diagnostics for Data Integrity. Keep proof-bar test id for deploy contracts. */
export function SystemHealthDiagnostics({
  variant = 'panel',
}: {
  variant?: 'panel' | 'sr-only'
}) {
  const { autoGates, brokerConnected, health, wsStatus, deployInfo } = useStore()

  const gatesObj = (autoGates?.gates && typeof autoGates.gates === 'object') ? autoGates.gates : {}
  const proofList = Array.isArray(autoGates?.proof_gates) ? autoGates.proof_gates : []
  const mlGate = gatesObj.ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS || proofList.find((g: any) => /spearman|ml accuracy/i.test(String(g?.label || g?.gate_id || '')))
  const paperGate = gatesObj.REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF || proofList.find((g: any) => /paper lifecycle|provenance/i.test(String(g?.label || g?.gate_id || '')))

  const mlOk = Boolean(mlGate?.pass ?? mlGate?.ok)
  const paperGateOk = Boolean(paperGate?.pass ?? paperGate?.ok)
  const paperOk = paperGateOk || paperModeActive(health)
  const dhanOk = brokerIsConnected(health, brokerConnected)
  const runtimeOk = systemRuntimeOk(health)
  const wsTone: 'ok' | 'warn' | 'error' = wsStatus === 'live' ? 'ok' : wsStatus === 'error' ? 'error' : 'warn'
  const mlLabel = mlOk
    ? `ρ=${mlGate?.latest_rho ?? 'ok'}`
    : `${(mlGate?.days_recorded ?? 0)}/${(mlGate?.days_required ?? 5)}d`
  const wsLabel = wsStatus === 'live' ? 'Live' : String(wsStatus)

  const proofItems: Array<[string, string, 'ok' | 'warn' | 'error']> = [
    ['System', runtimeOk ? String(health?.mode || health?.status || 'OK') : 'Pending', runtimeOk ? 'ok' : 'error'],
    ['API', runtimeOk ? 'Responding' : 'Check', runtimeOk ? 'ok' : 'warn'],
    ['WebSocket', wsLabel, wsTone],
    ['Data', dhanOk ? 'Dhan' : 'Dhan required', dhanOk ? 'ok' : 'error'],
    ['ML', mlLabel, mlOk ? 'ok' : 'warn'],
    ['Paper', paperOk ? (paperGateOk ? 'Gate ok' : 'Mode on') : 'Pending', paperOk ? 'ok' : 'warn'],
    ['UI', 'Rendered', 'ok'],
    ['SHA', shortSha(deployInfo?.git_sha), deployInfo?.git_sha ? 'ok' : 'warn'],
  ]

  const toneColor = {
    ok: { bg: 'rgba(34,197,94,.10)', border: 'rgba(34,197,94,.28)', dot: '#22c55e', text: '#4ade80' },
    warn: { bg: 'rgba(245,158,11,.10)', border: 'rgba(245,158,11,.28)', dot: '#f59e0b', text: '#fbbf24' },
    error: { bg: 'rgba(239,68,68,.10)', border: 'rgba(239,68,68,.28)', dot: '#ef4444', text: '#fca5a5' },
  }

  if (variant === 'sr-only') {
    return (
      <div
        data-testid="production-proof-bar"
        className="sr-only-proof-bar"
        role="status"
        aria-live="polite"
        aria-label="Production proof status"
      >
        <span>SYSTEM3 GENESIS v2.0</span>
        {proofItems.map(([label, value]) => (
          <span key={label}>{label} {value}</span>
        ))}
      </div>
    )
  }

  return (
    <section
      data-testid="system-health-diagnostics"
      className="elevated-panel"
      style={{ padding: 16 }}
      aria-label="System health diagnostics"
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 15, fontWeight: 700 }}>System health</h2>
          <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--text-mut)' }}>
            Engineering diagnostics for deploy proofs and runtime checks. Hidden from the main trading workspace.
          </p>
        </div>
        <span className="feed-badge feed-badge-mut">Deploy diagnostics</span>
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {proofItems.map(([label, value, tone]) => {
          const colors = toneColor[tone]
          return (
            <div
              key={label}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '6px 10px',
                borderRadius: 8,
                background: colors.bg,
                border: `1px solid ${colors.border}`,
              }}
            >
              <span style={{ width: 6, height: 6, borderRadius: 99, background: colors.dot }} aria-hidden />
              <span style={{ fontSize: 11, color: 'var(--text-mut)' }}>{label}</span>
              <span className="num" style={{ fontSize: 12, fontWeight: 700, color: colors.text }}>{value}</span>
            </div>
          )
        })}
      </div>
    </section>
  )
}
