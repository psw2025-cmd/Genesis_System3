/**
 * Single-source quantum-dense truth hydration for the dashboard.
 * All live banners/footers read Zustand after applyTruthBundle — no duplicate SHA bindings.
 */
import { API_HEADERS } from '../config'

export type StreamHealth = 'live' | 'degraded' | 'stale' | 'offline'
export type DataMode = 'live' | 'replay' | 'historical'

export interface TruthBundle {
  deployInfo: Record<string, unknown> | null
  health: Record<string, unknown> | null
  state: Record<string, unknown> | null
  brokerStatus: Record<string, unknown> | null
  brokerFunds: Record<string, unknown> | null
  brokerHoldings: Record<string, unknown> | null
  fetchedAt: string
  streamHealth: StreamHealth
  shaSynced: boolean | null
  circuitOpen: boolean
  dataMode: DataMode
}

export interface TruthHydrationMeta {
  streamHealth: StreamHealth
  shaSynced: boolean | null
  lastHydratedAt: string | null
  circuitOpen: boolean
  dataMode: DataMode
}

type FetchResult = { ok: true; data: unknown } | { ok: false; status: number }

const CIRCUIT_FAIL_THRESHOLD = 3
const CIRCUIT_COOLDOWN_MS = 30_000
const STALE_MS = 45_000

const breaker = { failures: 0, openUntil: 0 }

let dataMode: DataMode = 'live'

export function getDataMode(): DataMode {
  return dataMode
}

export function setDataMode(mode: DataMode): void {
  dataMode = mode
}

function circuitAllowsFetch(): boolean {
  return Date.now() >= breaker.openUntil
}

function recordSuccess(): void {
  breaker.failures = 0
  breaker.openUntil = 0
}

function recordFailure(): void {
  breaker.failures += 1
  if (breaker.failures >= CIRCUIT_FAIL_THRESHOLD) {
    breaker.openUntil = Date.now() + CIRCUIT_COOLDOWN_MS
  }
}

async function fetchJSON(base: string, path: string, timeoutMs = 12_000): Promise<FetchResult> {
  const ctrl = new AbortController()
  const timer = window.setTimeout(() => ctrl.abort(), timeoutMs)
  try {
    const url = `${base.replace(/\/+$/, '')}${path}`
    const r = await fetch(url, {
      credentials: 'include',
      headers: { Accept: 'application/json', ...API_HEADERS },
      signal: ctrl.signal,
    })
    if (!r.ok) return { ok: false, status: r.status }
    return { ok: true, data: await r.json() }
  } catch {
    return { ok: false, status: 0 }
  } finally {
    window.clearTimeout(timer)
  }
}

/** Embedded build SHA from Vite (optional — set at build time). */
export function embeddedBuildSha(): string | null {
  const sha = import.meta.env.VITE_GIT_SHA
  return sha && String(sha).trim() ? String(sha).trim() : null
}

export function validateShaSync(deploySha: unknown): boolean | null {
  const serving = String(deploySha || '').trim()
  if (!serving) return null
  const embedded = embeddedBuildSha()
  if (!embedded) return null
  return embedded.startsWith(serving.slice(0, 7)) || serving.startsWith(embedded.slice(0, 7))
}

function computeStreamHealth(
  results: FetchResult[],
  lastGoodAt: number | null,
): StreamHealth {
  const okCount = results.filter((r) => r.ok).length
  if (okCount === 0) return 'offline'
  if (okCount < results.length) return 'degraded'
  if (lastGoodAt && Date.now() - lastGoodAt > STALE_MS) return 'stale'
  return 'live'
}

let lastGoodHydrationAt: number | null = null

export async function fetchTruthBundle(base: string): Promise<TruthBundle> {
  const fetchedAt = new Date().toISOString()
  const circuitOpen = !circuitAllowsFetch()

  if (circuitOpen) {
    return {
      deployInfo: null,
      health: null,
      state: null,
      brokerStatus: null,
      brokerFunds: null,
      brokerHoldings: null,
      fetchedAt,
      streamHealth: 'offline',
      shaSynced: null,
      circuitOpen: true,
      dataMode,
    }
  }

  const paths =
    dataMode === 'historical'
      ? ['/api/deploy/info', '/api/health']
      : [
          '/api/deploy/info',
          '/api/health',
          '/api/state',
          '/api/broker/status',
          '/api/funds',
          '/api/holdings',
        ]

  const settled = await Promise.all(paths.map((p) => fetchJSON(base, p)))
  const anyOk = settled.some((r) => r.ok)
  if (anyOk) {
    recordSuccess()
    lastGoodHydrationAt = Date.now()
  } else {
    recordFailure()
  }

  const pick = (idx: number) => (settled[idx]?.ok ? (settled[idx] as { ok: true; data: unknown }).data as Record<string, unknown> : null)

  const deployInfo = pick(0)
  const health = pick(1)
  const state = dataMode === 'historical' ? null : pick(2)
  const brokerStatus = dataMode === 'historical' ? null : pick(3)
  const brokerFunds = dataMode === 'historical' ? null : pick(4)
  const brokerHoldings = dataMode === 'historical' ? null : pick(5)

  const streamHealth = computeStreamHealth(settled, lastGoodHydrationAt)
  const shaSynced = validateShaSync(deployInfo?.git_sha)

  return {
    deployInfo,
    health,
    state,
    brokerStatus,
    brokerFunds,
    brokerHoldings,
    fetchedAt,
    streamHealth,
    shaSynced,
    circuitOpen: false,
    dataMode,
  }
}

export interface TruthStoreSink {
  setDeployInfo: (d: unknown) => void
  setHealth: (d: unknown) => void
  setState: (d: unknown) => void
  setBrokerStatus: (d: unknown) => void
  setBrokerFunds: (d: unknown) => void
  setBrokerHoldings: (d: unknown) => void
  setTruthMeta: (d: TruthHydrationMeta) => void
}

/** Apply bundle to Zustand — single write path for truth banners. */
export function applyTruthBundle(bundle: TruthBundle, sink: TruthStoreSink): void {
  if (bundle.deployInfo) sink.setDeployInfo(bundle.deployInfo)
  if (bundle.health) sink.setHealth(bundle.health)
  if (bundle.state) sink.setState(bundle.state)
  if (bundle.brokerStatus) sink.setBrokerStatus(bundle.brokerStatus)
  if (bundle.brokerFunds) sink.setBrokerFunds(bundle.brokerFunds)
  if (bundle.brokerHoldings) sink.setBrokerHoldings(bundle.brokerHoldings)
  sink.setTruthMeta({
    streamHealth: bundle.streamHealth,
    shaSynced: bundle.shaSynced,
    lastHydratedAt: bundle.fetchedAt,
    circuitOpen: bundle.circuitOpen,
    dataMode: bundle.dataMode,
  })
}

/** Duplication guard — component names that must bind SHA only via hydration. */
export const TRUTH_SHA_BINDING_ALLOWLIST = [
  'TruthStrip',
  'DeploymentTruthFooter',
  'AutonomousLoopBanner',
  'DataIntegrity',
] as const

export function flagDuplicateShaBinding(componentName: string): boolean {
  return !TRUTH_SHA_BINDING_ALLOWLIST.includes(componentName as (typeof TRUTH_SHA_BINDING_ALLOWLIST)[number])
}
