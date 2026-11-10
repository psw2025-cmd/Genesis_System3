/** Separate live-readiness / LIVE_GATE records from operational alerts. */

function blob(alert: unknown): Record<string, unknown> {
  if (alert && typeof alert === 'object') {
    return alert as Record<string, unknown>
  }
  return {}
}

function upper(value: unknown): string {
  return String(value ?? '').toUpperCase()
}

export function isLiveReadinessInfo(alert: unknown): boolean {
  const item = blob(alert)
  const type = upper(item.type ?? item.category)
  const code = upper(item.code)
  const id = upper(item.id)
  const title = upper(item.title)
  const message = upper(item.message ?? item.detail)

  if (type === 'LIVE_GATE' || code === 'LIVE_GATE') return true
  if (id === 'OPS_LIVE_GATE' || id.includes('LIVE_GATE')) return true
  if (title.includes('LIVE TRADING CORRECTLY BLOCKED')) return true
  if (title.includes('LIVE TRADING REMAINS BLOCKED BY DESIGN')) return true
  if (message.includes('LIVE_TRADING_APPROVED') && message.includes('HUMAN_APPROVED')) return true
  if (message.includes('LIVE REMAINS BLOCKED BY DESIGN')) return true
  return false
}

export function splitAlertStream<T>(alerts: T[] | undefined | null): { liveReadinessInfo: T[]; activeAlerts: T[] } {
  const rows = Array.isArray(alerts) ? alerts : []
  return {
    liveReadinessInfo: rows.filter((alert) => isLiveReadinessInfo(alert)),
    activeAlerts: rows.filter((alert) => !isLiveReadinessInfo(alert)),
  }
}
