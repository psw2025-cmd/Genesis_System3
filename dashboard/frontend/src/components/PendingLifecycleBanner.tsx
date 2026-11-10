import { useStore } from '../store'
import { PENDING_LIFECYCLE_BANNER } from '../lib/lifecycleTruth'
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
  const payload = useStore((s) => s.mlPerformance)
  const ready = payload?.ready_for_live === true || payload?.performance?.ready_for_live === true
  const checklist = checklistOf(payload)
  const scriptItem = checklist?.find((item) => item.id === 'paper_validation_script')
  const showScriptLine = !ready && (scriptItem == null || scriptItem.pass !== true)
  const proofStatus = payload?.proof_status || payload?.performance?.status || payload?.status
  const blockers = blockerLines(payload)
  const reason = payload?.ready_for_live_reason || payload?.performance?.ready_for_live_reason

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
        {showScriptLine ? PENDING_LIFECYCLE_BANNER : 'Lifecycle payload'}
      </div>
      <div style={{ marginTop: 6 }}>
        proof_status={showField(proofStatus)} · ready_for_live={showField(payload?.ready_for_live ?? payload?.performance?.ready_for_live)}
        {reason ? ` · ${reason}` : ''}
      </div>
      <div style={{ marginTop: 4 }}>
        blockers: {blockers.length ? blockers.join(' | ') : 'null'}
      </div>
      <div style={{ marginTop: 8, color: 'var(--text-pri)' }}>
        <ValidationChecklist items={checklist} />
      </div>
    </div>
  )
}
