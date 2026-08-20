/**
 * Market Hours Detection for Indian Stock Market (Frontend)
 * Authoritative wall-clock calculations are always performed in Asia/Kolkata,
 * independent of the browser/runner local timezone.
 */

const MARKET_OPEN_HOUR = 9
const MARKET_OPEN_MINUTE = 15
const MARKET_CLOSE_HOUR = 15
const MARKET_CLOSE_MINUTE = 30
const IST_ZONE = 'Asia/Kolkata'

type IstParts = {
  year: number
  month: number
  day: number
  weekday: number
  hour: number
  minute: number
}

const WEEKDAY: Record<string, number> = {
  Sun: 0,
  Mon: 1,
  Tue: 2,
  Wed: 3,
  Thu: 4,
  Fri: 5,
  Sat: 6,
}

function getIstParts(now: Date = new Date()): IstParts {
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone: IST_ZONE,
    weekday: 'short',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  })
  const parts = Object.fromEntries(
    formatter.formatToParts(now).map((part) => [part.type, part.value]),
  )
  return {
    year: Number(parts.year),
    month: Number(parts.month),
    day: Number(parts.day),
    weekday: WEEKDAY[parts.weekday] ?? -1,
    hour: Number(parts.hour),
    minute: Number(parts.minute),
  }
}

function minutesOfDay(parts: IstParts): number {
  return parts.hour * 60 + parts.minute
}

function istOpenInstant(year: number, month: number, day: number): Date {
  // 09:15 IST = 03:45 UTC. Date.UTC normalizes month/day rollover safely.
  return new Date(Date.UTC(year, month - 1, day, 3, 45, 0, 0))
}

/**
 * Check if market is currently open.
 * Optional `now` makes the logic deterministic for tests/proofs.
 */
export function isMarketOpen(now: Date = new Date()): boolean {
  const parts = getIstParts(now)
  if (parts.weekday === 0 || parts.weekday === 6 || parts.weekday < 0) return false

  const current = minutesOfDay(parts)
  const open = MARKET_OPEN_HOUR * 60 + MARKET_OPEN_MINUTE
  const close = MARKET_CLOSE_HOUR * 60 + MARKET_CLOSE_MINUTE
  return current >= open && current <= close
}

export function getMarketStatus(now: Date = new Date()): {
  isOpen: boolean
  reason: string
  nextOpen?: string
} {
  const parts = getIstParts(now)
  const current = minutesOfDay(parts)
  const open = MARKET_OPEN_HOUR * 60 + MARKET_OPEN_MINUTE
  const close = MARKET_CLOSE_HOUR * 60 + MARKET_CLOSE_MINUTE

  if (parts.weekday === 0 || parts.weekday === 6 || parts.weekday < 0) {
    return {
      isOpen: false,
      reason: `Market closed: Weekend (${parts.weekday === 0 ? 'Sunday' : parts.weekday === 6 ? 'Saturday' : 'Unknown'})`,
    }
  }
  if (current < open) {
    return { isOpen: false, reason: 'Market closed: Before market hours (opens at 09:15 AM IST)' }
  }
  if (current > close) {
    return { isOpen: false, reason: 'Market closed: After market hours (closed at 15:30 IST)' }
  }
  return { isOpen: true, reason: 'Market open' }
}

export function getNextMarketOpen(now: Date = new Date()): Date {
  const parts = getIstParts(now)
  const current = minutesOfDay(parts)
  const open = MARKET_OPEN_HOUR * 60 + MARKET_OPEN_MINUTE

  if (parts.weekday >= 1 && parts.weekday <= 5 && current < open) {
    return istOpenInstant(parts.year, parts.month, parts.day)
  }

  const cursor = new Date(Date.UTC(parts.year, parts.month - 1, parts.day))
  for (let days = 1; days <= 10; days += 1) {
    const candidate = new Date(cursor)
    candidate.setUTCDate(candidate.getUTCDate() + days)
    const weekday = candidate.getUTCDay()
    if (weekday >= 1 && weekday <= 5) {
      return istOpenInstant(candidate.getUTCFullYear(), candidate.getUTCMonth() + 1, candidate.getUTCDate())
    }
  }

  throw new Error('Unable to determine next market open')
}
