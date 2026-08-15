import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

/**
 * One browser-wide resilience policy for read-only dashboard traffic.
 *
 * Guarantees:
 * - retries ONLY idempotent GET/HEAD requests;
 * - honors Retry-After (seconds or HTTP date);
 * - exponential backoff with full jitter for transient 429/502/503/504;
 * - shares cooldown state across every Axios/fetch caller in the tab;
 * - never retries POST/PUT/PATCH/DELETE (especially trading/mutation routes);
 * - caps retries so a rate-limit response cannot become a retry storm.
 */

const TRANSIENT = new Set([429, 502, 503, 504])
const MAX_RETRIES = 2
const BASE_BACKOFF_MS = 900
const MAX_BACKOFF_MS = 15_000
const MAX_SHARED_COOLDOWN_MS = 30_000

type RetryConfig = InternalAxiosRequestConfig & {
  __system3RetryCount?: number
  __system3CooldownWaited?: boolean
}

const routeCooldownUntil = new Map<string, number>()
let fetchInstalled = false
let axiosInstalled = false

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, Math.max(0, ms)))
}

function requestMethod(method?: string): string {
  return String(method || 'GET').toUpperCase()
}

function isRetryableMethod(method?: string): boolean {
  const value = requestMethod(method)
  return value === 'GET' || value === 'HEAD'
}

function routeKey(rawUrl: string): string {
  try {
    const url = new URL(rawUrl, window.location.origin)
    // Query timestamps/cache-busters must not create independent cooldown lanes.
    url.searchParams.delete('_ts')
    return `${url.origin}${url.pathname}`
  } catch {
    return rawUrl.split('?')[0]
  }
}

function retryAfterMs(value: string | null | undefined): number {
  if (!value) return 0
  const seconds = Number(value)
  if (Number.isFinite(seconds) && seconds >= 0) {
    return Math.min(MAX_SHARED_COOLDOWN_MS, seconds * 1000)
  }
  const at = Date.parse(value)
  return Number.isFinite(at) ? Math.min(MAX_SHARED_COOLDOWN_MS, Math.max(0, at - Date.now())) : 0
}

function jitterBackoffMs(attempt: number, retryAfter = 0): number {
  const cap = Math.min(MAX_BACKOFF_MS, BASE_BACKOFF_MS * 2 ** Math.max(0, attempt - 1))
  // Full jitter avoids synchronized browser tabs waking at the same millisecond.
  const jitter = Math.floor(Math.random() * Math.max(1, cap))
  return Math.max(retryAfter, jitter)
}

function recordCooldown(rawUrl: string, delayMs: number): void {
  const key = routeKey(rawUrl)
  const until = Date.now() + Math.min(MAX_SHARED_COOLDOWN_MS, Math.max(0, delayMs))
  routeCooldownUntil.set(key, Math.max(routeCooldownUntil.get(key) || 0, until))
}

async function awaitSharedCooldown(rawUrl: string): Promise<void> {
  const until = routeCooldownUntil.get(routeKey(rawUrl)) || 0
  if (until <= Date.now()) return
  const remaining = Math.min(MAX_SHARED_COOLDOWN_MS, until - Date.now())
  // Small random spread prevents a herd after a shared Retry-After expires.
  await sleep(remaining + Math.floor(Math.random() * 350))
}

export function getTrafficResilienceState() {
  const now = Date.now()
  const cooling = [...routeCooldownUntil.entries()]
    .filter(([, until]) => until > now)
    .map(([route, until]) => ({ route, remaining_ms: until - now }))
  return {
    cooling_routes: cooling,
    max_retries: MAX_RETRIES,
    retryable_methods: ['GET', 'HEAD'],
    mutation_retries: 0,
  }
}

function installAxiosPolicy(): void {
  if (axiosInstalled) return
  axiosInstalled = true

  axios.interceptors.request.use(async (config: RetryConfig) => {
    if (isRetryableMethod(config.method) && config.url) {
      await awaitSharedCooldown(config.url)
    }
    return config
  })

  axios.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const config = error.config as RetryConfig | undefined
      const status = Number(error.response?.status || 0)
      if (!config || !config.url || !isRetryableMethod(config.method) || !TRANSIENT.has(status)) {
        return Promise.reject(error)
      }

      const attempt = Number(config.__system3RetryCount || 0) + 1
      const retryAfter = retryAfterMs(String(error.response?.headers?.['retry-after'] || ''))
      const delayMs = jitterBackoffMs(attempt, retryAfter)
      recordCooldown(config.url, delayMs)

      if (attempt > MAX_RETRIES) {
        return Promise.reject(error)
      }

      config.__system3RetryCount = attempt
      await sleep(delayMs)
      return axios.request(config)
    },
  )
}

function installFetchPolicy(): void {
  if (fetchInstalled || typeof window.fetch !== 'function') return
  fetchInstalled = true
  const nativeFetch = window.fetch.bind(window)

  window.fetch = (async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const rawUrl = typeof input === 'string'
      ? input
      : input instanceof URL
        ? input.toString()
        : input.url
    const method = requestMethod(init?.method || (input instanceof Request ? input.method : 'GET'))

    // Mutations preserve native semantics and are never automatically retried.
    if (!isRetryableMethod(method)) {
      return nativeFetch(input, init)
    }

    await awaitSharedCooldown(rawUrl)
    let last: Response | null = null
    for (let attempt = 0; attempt <= MAX_RETRIES; attempt += 1) {
      const response = await nativeFetch(input, init)
      last = response
      if (!TRANSIENT.has(response.status)) return response

      const nextAttempt = attempt + 1
      const retryAfter = retryAfterMs(response.headers.get('retry-after'))
      const delayMs = jitterBackoffMs(nextAttempt, retryAfter)
      recordCooldown(rawUrl, delayMs)
      if (nextAttempt > MAX_RETRIES) return response
      await sleep(delayMs)
    }
    return last as Response
  }) as typeof window.fetch
}

export function installTrafficResilience(): void {
  installAxiosPolicy()
  installFetchPolicy()
}
