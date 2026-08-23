/** Fail-closed status color. Substring matches must not paint DISCONNECTED green. */

export type StatusTone = 'up' | 'down' | 'warn' | 'neutral'

export function statusTone(value: string): StatusTone {
  const s = String(value || '').trim().toUpperCase()
  if (!s) return 'neutral'
  if (
    s === 'DISCONNECTED' ||
    s.includes('NOT_READY') ||
    s.includes('FAIL') ||
    s.includes('ERROR') ||
    s.includes('OFFLINE') ||
    s === 'CLOSED / POLL' ||
    s.startsWith('CLOSED')
  ) {
    return 'down'
  }
  if (s === 'WAITING' || s === 'LOCKED' || s === 'RESPONDED') return 'warn'
  if (s === 'CONNECTED' || s === 'PASS' || s === 'HEALTHY' || s === 'OPEN') return 'up'
  if (s.includes('LIVE FLAG')) return 'down'
  return 'neutral'
}

export function statusToneCss(value: string): string {
  const tone = statusTone(value)
  if (tone === 'up') return 'var(--up)'
  if (tone === 'down') return 'var(--down)'
  if (tone === 'warn') return 'var(--amber)'
  return 'var(--text-pri)'
}
