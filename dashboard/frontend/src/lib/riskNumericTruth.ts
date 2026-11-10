// Only explicitly supplied finite numeric values can become risk metrics.
// Number(null), Number(false), Number('') and Number([]) are zero in JS,
// but none of them establish an independently observed risk value.
const DECIMAL = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/

export function numberOrUndefined(value: unknown): number | undefined {
  if (typeof value === 'number') return Number.isFinite(value) ? value : undefined
  if (typeof value !== 'string') return undefined
  const raw = value.trim()
  if (!DECIMAL.test(raw)) return undefined
  const parsed = Number(raw)
  return Number.isFinite(parsed) ? parsed : undefined
}
