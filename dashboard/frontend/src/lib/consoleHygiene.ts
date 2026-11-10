/**
 * Chrome extension noise filter.
 *
 * "Could not establish connection. Receiving end does not exist." and
 * chrome.runtime.lastError come from browser extensions (Gemini side panel,
 * Grammarly, password managers, etc.) — not from System3 app code.
 * Without this filter, DevTools shows 50+ red errors that look like app failures
 * and hide real regressions.
 */
const EXTENSION_NOISE =
  /Could not establish connection\. Receiving end does not exist|Unchecked runtime\.lastError|Receiving end does not exist/i

function isExtensionNoise(reason: unknown): boolean {
  if (reason == null) return false
  if (typeof reason === 'string') return EXTENSION_NOISE.test(reason)
  if (reason instanceof Error) return EXTENSION_NOISE.test(reason.message || '')
  try {
    return EXTENSION_NOISE.test(String(reason))
  } catch {
    return false
  }
}

export function installConsoleHygiene(): void {
  if (typeof window === 'undefined') return
  const w = window as Window & { __system3ConsoleHygiene?: boolean }
  if (w.__system3ConsoleHygiene) return
  w.__system3ConsoleHygiene = true

  window.addEventListener(
    'unhandledrejection',
    (event) => {
      if (isExtensionNoise(event.reason)) {
        event.preventDefault()
        event.stopImmediatePropagation()
      }
    },
    true,
  )

  window.addEventListener(
    'error',
    (event) => {
      if (isExtensionNoise(event.message) || isExtensionNoise(event.error)) {
        event.preventDefault()
        event.stopImmediatePropagation()
      }
    },
    true,
  )
}
