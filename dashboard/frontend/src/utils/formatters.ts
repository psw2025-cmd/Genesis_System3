/**
 * Defensive Multi-Validation Formatters for Financial Metrics
 * Ensures 100% zero-crash resilience against null, undefined, NaN, Infinity, or unparsed JSON strings.
 */

export function safeNumber(value: unknown, fallback: number = 0): number {
  if (value === null || value === undefined || value === '') return fallback
  const num = Number(value)
  return Number.isFinite(num) ? num : fallback
}

export function safeMoney(
  value: unknown,
  options?: {
    fallback?: string
    showSign?: boolean
    decimals?: number
  }
): string {
  const { fallback = '₹0.00', showSign = false, decimals = 2 } = options || {}
  if (value === null || value === undefined || value === '') return fallback
  const num = Number(value)
  if (!Number.isFinite(num)) return fallback

  const sign = showSign && num > 0 ? '+' : ''
  const formatted = Math.abs(num).toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })

  return num < 0 ? `-₹${formatted}` : `${sign}₹${formatted}`
}

export function safePct(
  value: unknown,
  options?: {
    fallback?: string
    showSign?: boolean
    decimals?: number
  }
): string {
  const { fallback = '0.00%', showSign = false, decimals = 2 } = options || {}
  if (value === null || value === undefined || value === '') return fallback
  const num = Number(value)
  if (!Number.isFinite(num)) return fallback

  const sign = showSign && num > 0 ? '+' : num < 0 ? '-' : ''
  const formatted = Math.abs(num).toFixed(decimals)
  return `${sign}${formatted}%`
}

export function safeText(value: unknown, fallback: string = '—'): string {
  if (value === null || value === undefined) return fallback
  const str = String(value).trim()
  return str.length > 0 ? str : fallback
}

export function safeArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? value : []
}

export function safeObject<T extends object>(value: unknown, fallback: T = {} as T): T {
  return value !== null && typeof value === 'object' && !Array.isArray(value) ? (value as T) : fallback
}
