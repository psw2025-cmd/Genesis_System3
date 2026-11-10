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

function brokerStatusBlob(brokerStatus?: any): string {
  return [
    brokerStatus?.error,
    brokerStatus?.upstream_classification,
    brokerStatus?.auth_classification,
    brokerStatus?.upstream_code,
  ].map((value) => String(value ?? '')).join(' ').toUpperCase()
}

export function isNonAuthBrokerRejection(brokerStatus?: any): boolean {
  const blob = brokerStatusBlob(brokerStatus)
  const code = Number(brokerStatus?.upstream_code)
  if (code === 906 || blob.includes('DHAN_REQUEST_REJECTED_906')) return true
  if (code === 805 || code === 904 || blob.includes('DHAN_RATE_LIMITED') || blob.includes('HTTP_429')) return true
  if (code === 810 || blob.includes('CLIENT_ID_INVALID')) return true
  return false
}

export function brokerReliabilityPass(brokerStatus?: any, marketDataProven?: boolean): boolean {
  if (brokerStatus?.connected !== true) return false
  if (isNonAuthBrokerRejection(brokerStatus)) return false
  return marketDataProven === true
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
