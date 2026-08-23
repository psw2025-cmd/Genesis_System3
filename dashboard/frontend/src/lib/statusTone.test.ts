import { describe, expect, it } from 'vitest'
import { statusTone } from './statusTone'

describe('statusTone', () => {
  it('does not treat DISCONNECTED as CONNECTED', () => {
    expect(statusTone('DISCONNECTED')).toBe('down')
    expect(statusTone('CONNECTED')).toBe('up')
  })

  it('does not treat LIVE FLAG as healthy', () => {
    expect(statusTone('LIVE FLAG')).toBe('down')
    expect(statusTone('LOCKED')).toBe('warn')
  })

  it('keeps closed market amber/down, not green', () => {
    expect(statusTone('CLOSED / POLL')).toBe('down')
  })
})
