import { expect, it } from 'vitest'
import { parseIstMarketStamp, pickFutureNextOpen } from './nextMarketOpen'

const AFTER_HOURS = new Date('2026-09-16T17:14:07+05:30')

it('parses banner IST stamps including the omitted-seconds form', () => {
  const withSeconds = parseIstMarketStamp('2026-09-17 09:15:00 IST')
  const withoutSeconds = parseIstMarketStamp('2026-09-15 09:15 IST')
  expect(withSeconds?.toISOString()).toBe('2026-09-17T03:45:00.000Z')
  expect(withoutSeconds?.toISOString()).toBe('2026-09-15T03:45:00.000Z')
})

it('drops today 09:15 after the 15:30 close and keeps the next session', () => {
  const shown = pickFutureNextOpen(
    ['2026-09-16 09:15:00 IST', '2026-09-17 09:15:00 IST'],
    AFTER_HOURS,
  )
  expect(shown).toBe('2026-09-17 09:15:00 IST')
})

it('does not display a past next-open when every candidate has already occurred', () => {
  expect(pickFutureNextOpen(['2026-09-16 09:15:00 IST'], AFTER_HOURS)).toBe('—')
})
