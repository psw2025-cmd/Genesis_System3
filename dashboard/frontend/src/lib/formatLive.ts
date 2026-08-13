/** Honest live-value formatters. Missing data is an em dash, never a fake zero. */

export function formatInr(value: unknown): string {
  const n = Number(value)
  if (!Number.isFinite(n)) return '—'
  return `₹${n.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
}

export function formatIstStamp(value: unknown): string {
  if (value == null || value === '' || value === '--') return '—'
  const d = new Date(String(value))
  if (Number.isNaN(d.getTime())) return String(value)
  return d.toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    hour12: false,
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

export function formatAgeSec(value: unknown): string {
  const n = Number(value)
  if (!Number.isFinite(n) || n < 0) return '—'
  if (n < 60) return `${Math.round(n)}s`
  if (n < 3600) return `${Math.floor(n / 60)}m ${Math.round(n % 60)}s`
  return `${(n / 3600).toFixed(1)}h`
}

export function shortSha(value: unknown): string {
  const s = String(value || '').trim()
  return s ? s.slice(0, 7) : '—'
}

export function asFinite(value: unknown): number | undefined {
  const n = Number(value)
  return Number.isFinite(n) ? n : undefined
}
