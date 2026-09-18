import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { installConsoleHygiene } from './consoleHygiene'

describe('consoleHygiene', () => {
  beforeEach(() => {
    delete (window as Window & { __system3ConsoleHygiene?: boolean }).__system3ConsoleHygiene
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('suppresses chrome extension receiving-end rejections', () => {
    installConsoleHygiene()
    const prevented: boolean[] = []
    const handler = (event: PromiseRejectionEvent) => {
      prevented.push(event.defaultPrevented)
    }
    window.addEventListener('unhandledrejection', handler)
    const event = new Event('unhandledrejection', { cancelable: true }) as PromiseRejectionEvent
    Object.defineProperty(event, 'reason', {
      value: new Error('Could not establish connection. Receiving end does not exist.'),
    })
    window.dispatchEvent(event)
    window.removeEventListener('unhandledrejection', handler)
    expect(prevented.some(Boolean) || event.defaultPrevented).toBe(true)
  })

  it('does not suppress unrelated rejections', () => {
    installConsoleHygiene()
    const event = new Event('unhandledrejection', { cancelable: true }) as PromiseRejectionEvent
    Object.defineProperty(event, 'reason', {
      value: new Error('Real System3 failure'),
    })
    window.dispatchEvent(event)
    expect(event.defaultPrevented).toBe(false)
  })
})
