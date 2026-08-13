/** Map live /api/health truth onto dashboard labels. Missing proof is not an outage. */

export type TruthTone = 'ok' | 'warn' | 'error'

export function brokerFromHealth(health: any): boolean | undefined {
  if (health?.broker?.connected === true) return true
  if (health?.broker?.connected === false) return false
  const status = String(health?.broker_status || health?.broker?.status || '').toLowerCase()
  if (status === 'connected' || status === 'ok') return true
  if (status === 'disconnected' || status === 'error' || status === 'failure') return false
  return undefined
}

export function brokerIsConnected(health: any, storeConnected: boolean, brokerStatus?: any): boolean {
  if (storeConnected === true || brokerStatus?.connected === true) return true
  return brokerFromHealth(health) === true
}

export function systemRuntimeOk(health: any): boolean {
  const status = String(health?.status || '').toLowerCase()
  return status === 'ok' || status === 'healthy' || Boolean(health?.mode)
}

export function paperModeActive(health: any): boolean {
  const mode = String(health?.mode || '').toUpperCase()
  return mode.includes('PAPER') || mode.includes('ANALYZER')
}

export function apiObservedOk(health: any, apiStatus?: any): boolean {
  if (String(health?.status || '').toLowerCase() === 'ok') return true
  if (String(apiStatus?.status || '').toLowerCase() === 'ok') return true
  return Boolean(health && !apiStatus?.status)
}
