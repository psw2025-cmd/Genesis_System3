/** Pick a still-future next-open stamp. Past 09:15 values are stale, not truth. */

const IST_STAMP = /^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::(\d{2}))?/

export function parseIstMarketStamp(raw: unknown): Date | null {
  const text = String(raw ?? '').trim()
  if (!text || text === '—' || text === '--' || text === '-') return null
  const cleaned = text.replace(/\s+IST$/i, '').trim()
  const match = cleaned.match(IST_STAMP)
  if (!match) return null
  const iso = `${match[1]}-${match[2]}-${match[3]}T${match[4]}:${match[5]}:${match[6] || '00'}+05:30`
  const parsed = new Date(iso)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

export function pickFutureNextOpen(candidates: unknown[], now: Date = new Date()): string {
  let bestLabel = ''
  let bestTs = Number.POSITIVE_INFINITY
  for (const candidate of candidates) {
    const label = String(candidate ?? '').trim()
    const parsed = parseIstMarketStamp(label)
    if (!parsed) continue
    const ts = parsed.getTime()
    if (ts <= now.getTime()) continue
    if (ts < bestTs) {
      bestTs = ts
      bestLabel = label
    }
  }
  return bestLabel || '—'
}
