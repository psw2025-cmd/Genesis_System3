/** Honest feed-quality labels. Never claim Live when market is closed or data is stale. */

export type FeedQuality =
  | 'Live'
  | 'Delayed'
  | 'Stale'
  | 'Reconnecting'
  | 'Disconnected'
  | 'Mock'

export type FeedTone = 'ok' | 'warn' | 'error' | 'mut'

const STALE_TICK_SEC = 120

function isMockSource(source: unknown): boolean {
  return /(mock|synthetic|fake|csv|yahoo|fallback)/i.test(String(source || ''))
}

export function resolveFeedQuality(input: {
  marketOpen?: boolean
  wsStatus?: string
  tickAgeSec?: number | null
  dataSource?: string | null
  brokerConnected?: boolean
}): { label: FeedQuality; tone: FeedTone; detail: string } {
  const marketOpen = Boolean(input.marketOpen)
  const ws = String(input.wsStatus || '').toLowerCase()
  const tickAge = Number(input.tickAgeSec)
  const hasTickAge = Number.isFinite(tickAge)
  const source = input.dataSource || ''

  if (isMockSource(source)) {
    return { label: 'Mock', tone: 'mut', detail: 'Non-production or fallback source' }
  }

  if (ws === 'error' || ws === 'off') {
    if (input.brokerConnected === false && !marketOpen) {
      return { label: 'Disconnected', tone: 'error', detail: 'Feed unavailable' }
    }
    if (ws === 'error') {
      return { label: 'Disconnected', tone: 'error', detail: 'WebSocket error' }
    }
  }

  if (ws === 'connecting') {
    return { label: 'Reconnecting', tone: 'warn', detail: 'Reconnecting to stream' }
  }

  if (hasTickAge && tickAge > STALE_TICK_SEC) {
    return {
      label: 'Stale',
      tone: 'warn',
      detail: `Last tick ${Math.round(tickAge)}s ago`,
    }
  }

  if (!marketOpen) {
    return {
      label: 'Delayed',
      tone: 'warn',
      detail: ws === 'live' ? 'Market closed · poll / snapshot' : 'Market closed · delayed poll',
    }
  }

  if (ws === 'live' && (!hasTickAge || tickAge <= STALE_TICK_SEC)) {
    return { label: 'Live', tone: 'ok', detail: 'Market hours · stream' }
  }

  return { label: 'Delayed', tone: 'warn', detail: 'Polling for updates' }
}

export function humanizeContractReason(reason: unknown): string {
  const raw = String(reason || '').trim()
  if (!raw) return 'No producer has supplied provenance-valid candidates yet.'
  const map: Record<string, string> = {
    NO_VERIFIED_EVIDENCE: 'No producer has supplied provenance-valid candidates.',
    PRODUCER_SOURCE_UNVERIFIED: 'Producer source is not on the approved list.',
    INVALID_OR_FUTURE_AS_OF: 'Evidence timestamp is missing or invalid.',
    CANDIDATE_EVIDENCE_UNAVAILABLE: 'Candidate evidence is not available.',
    NO_CANDIDATE_PASSED_PROVENANCE_VALIDATION: 'Candidates were rejected for missing price or model provenance.',
    ADDITIONAL_RESEARCH_SECTIONS_UNAVAILABLE: 'Ranking is partial; other research sections are still pending.',
  }
  if (map[raw]) return map[raw]
  return raw.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}
