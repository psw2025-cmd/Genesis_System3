import { useStore } from '../store'
import { brokerPermissionLabel, liveTradingOn, orderAllowedValue, PENDING_LIFECYCLE_BANNER } from '../lib/lifecycleTruth'
import { resolveFeedQuality } from '../lib/feedQuality'
import { ValidationChecklist, showField, type ChecklistItem } from './ValidationChecklist'

function checklistOf(payload: any): ChecklistItem[] | null | undefined {
  if (!payload) return null
  return payload.validations_checklist || payload.performance?.validations_checklist
}

function blockerLines(payload: any): string[] {
  if (!payload) return []
  const lines: string[] = []
  if (payload.blocker_reason) lines.push(String(payload.blocker_reason))
  const list = payload.blocker_reasons || payload.performance?.blocker_reasons
  if (Array.isArray(list)) {
    for (const item of list) {
      if (!item) continue
      if (typeof item === 'string') lines.push(item)
      else if (item.blocker_reason) lines.push(`${item.model ? `${item.model}: ` : ''}${item.blocker_reason}`)
    }
  }
  return lines
}

export function PendingLifecycleBanner() {
  const { mlPerformance: payload, state, health, brokerStatus, brokerConnected, marketOpen, wsStatus } = useStore()
  const reportedProofStatus = String(payload?.proof_status || payload?.performance?.status || payload?.status || '').toUpperCase()
  const readyFlag = payload?.ready_for_live === true || payload?.performance?.ready_for_live === true
  const ready = readyFlag && reportedProofStatus !== '' && reportedProofStatus !== 'BLOCKED'
  const checklist = checklistOf(payload)
  const scriptItem = checklist?.find((item) => item.id === 'paper_validation_script')
  const showScriptLine = !ready && (scriptItem == null || scriptItem.pass !== true)
  const proofStatus = reportedProofStatus || null
  const blockers = blockerLines(payload)
  const reason = payload?.ready_for_live_reason || payload?.performance?.ready_for_live_reason
  const marketValidation = checklist?.find((item) => /market[_ -]?validation/i.test(`${item.id || ''} ${item.label || ''}`))
  const marketValidationStatus = marketValidation?.pass === true ? 'REPORTED PASS'
    : marketValidation?.pass === false ? 'NO'
      : 'NOT REPORTED'
  const feed = resolveFeedQuality({
    marketOpen,
    wsStatus,
    tickAgeSec: state?.last_tick_age_sec ?? state?.tick_health?.last_tick_age_sec,
    dataSource: state?.data_source || health?.data_source,
    brokerConnected,
  })
  const transport = wsStatus === 'live' ? 'CONNECTED'
    : wsStatus === 'connecting' ? 'CONNECTING'
      : wsStatus === 'error' ? 'ERROR' : 'DISCONNECTED'
  const orderAllowed = orderAllowedValue(state, brokerStatus)
  const orderGate = liveTradingOn(state, brokerStatus, health) || orderAllowed === true
    ? 'FLAG DETECTED · REVIEW REQUIRED'
    : orderAllowed === false ? 'BLOCKED · PAPER ONLY' : 'NOT PROVEN · PAPER ONLY'
  const title = !payload ? 'FORWARD MODEL EVIDENCE NOT LOADED'
    : ready ? 'FORWARD MODEL VALIDATION REPORTED'
      : showScriptLine ? PENDING_LIFECYCLE_BANNER : 'FORWARD MODEL EVIDENCE INCOMPLETE'

  return (
    <div
      data-testid="pending-lifecycle-banner"
      style={{
        marginBottom: 12,
        padding: '10px 12px',
        borderRadius: 8,
        border: '1px solid rgba(245,158,11,.55)',
        background: 'rgba(245,158,11,.12)',
        color: '#fbbf24',
        fontSize: 12,
        lineHeight: 1.45,
      }}
    >
      <div style={{ fontWeight: 900 }}>
        {title}
      </div>
      <div className="lifecycle-status-grid" style={{ marginTop: 8 }}>
        <div data-testid="forward-model-proof-status">
          <b>Forward-model evidence:</b> {payload ? (ready ? 'REPORTED PASS' : `NOT READY (${showField(proofStatus)})`) : 'NOT LOADED'}
        </div>
        <div data-testid="market-validation-status">
          <b>Stored market-validation evidence:</b> {marketValidationStatus}
          {marketValidation?.detail ? ` · ${marketValidation.detail}` : ''}
        </div>
        <div data-testid="market-feed-status">
          <b>Market data:</b> {feed.label.toUpperCase()} · {feed.detail}
        </div>
        <div data-testid="websocket-transport-status">
          <b>WebSocket transport:</b> {transport} (connection only)
        </div>
        <div data-testid="broker-permission-status">
          <b>Broker permission:</b> {brokerPermissionLabel({ brokerConnected, brokerStatus, health, state })}
        </div>
        <div data-testid="order-gate-status">
          <b>Order gate:</b> {orderGate}
        </div>
      </div>
      <div style={{ marginTop: 8 }}>
        Model API fields only: proof_status={showField(proofStatus)} · ready_for_live={showField(payload?.ready_for_live ?? payload?.performance?.ready_for_live)}
        {reason ? ` · ${reason}` : ''}
      </div>
      <div style={{ marginTop: 4 }}>Model blockers: {blockers.length ? blockers.join(' | ') : 'none reported'}</div>
      <div style={{ marginTop: 6, fontWeight: 700 }}>Model proof does not prove this session's market validation or authorize orders.</div>
      <div style={{ marginTop: 8, color: 'var(--text-pri)' }}>
        <ValidationChecklist items={checklist} />
      </div>
    </div>
  )
}
