import { create } from 'zustand'
import { isMarketOpen } from './utils/marketHours'

interface DashboardState {
  // Connection
  wsStatus: 'connecting' | 'live' | 'error' | 'off'
  brokerConnected: boolean
  marketOpen: boolean
  lastSync: string

  // Live data
  health: any
  state: any
  chain: Record<string, any>
  paper: any
  gainRank: any
  marketTop: any
  alerts: any[]
  alertFeedStatus: { state: 'loading' | 'ready' | 'degraded'; message?: string; source?: string; updatedAt?: string }
  autoGates: any
  apiStatus: any

  // Performance data — works after market too
  pnl: any

  // Broker real data (market-independent — works anytime)
  brokerStatus: any
  brokerHoldings: any
  brokerFunds: any
  brokerPositions: any
  liveBoard: any

  // Runtime facts (deploy SHA, research contract)
  deployInfo: any
  research: any

  // UI
  activeTab: string
  chainSymbol: string
  sidebarOpen: boolean
  commandQuery: string

  // Actions
  setWsStatus: (s: DashboardState['wsStatus']) => void
  setHealth: (d: any) => void
  setState: (d: any) => void
  setChain: (sym: string, d: any) => void
  setPaper: (d: any) => void
  setGainRank: (d: any) => void
  setMarketTop: (d: any) => void
  setAlerts: (d: any[]) => void
  setAlertFeedStatus: (d: DashboardState['alertFeedStatus']) => void
  setAutoGates: (d: any) => void
  setPnl: (d: any) => void
  setApiStatus: (d: any) => void
  setBrokerStatus: (d: any) => void
  setBrokerHoldings: (d: any) => void
  setBrokerFunds: (d: any) => void
  setBrokerPositions: (d: any) => void
  setLiveBoard: (d: any) => void
  setActiveTab: (t: string) => void
  setChainSymbol: (s: string) => void
  setDeployInfo: (d: any) => void
  setResearch: (d: any) => void
  setSidebarOpen: (open: boolean) => void
  setCommandQuery: (q: string) => void
}

function marketOpenFromHealth(health: any, previous: boolean): boolean {
  const explicit = health?.market?.is_open
  if (explicit === true || explicit === false) return explicit

  const status = String(health?.market_status ?? health?.market?.status ?? '').trim().toLowerCase()
  if (status === 'open' || status === 'live' || status === 'live_market') return true
  if (status === 'closed' || status.startsWith('closed_') || status === 'post_market') return false

  // A slim/partial health payload is not evidence that the market is closed.
  // Preserve the last known truth rather than coercing undefined -> false.
  return previous
}

export const useStore = create<DashboardState>((set) => ({
  wsStatus: 'connecting',
  brokerConnected: false,
  // Browser-local fallback is computed in Asia/Kolkata and is replaced only by
  // explicit backend market truth. This avoids a false CLOSED banner during
  // Cloud Run cold-start / partial-health hydration.
  marketOpen: isMarketOpen(),
  lastSync: '--',
  health: null,
  state: null,
  chain: {},
  paper: null,
  gainRank: null,
  marketTop: null,
  alerts: [],
  alertFeedStatus: { state: 'loading' },
  autoGates: null,
  apiStatus: null,
  pnl: null,
  brokerStatus: null,
  brokerHoldings: null,
  brokerFunds: null,
  brokerPositions: null,
  liveBoard: null,
  deployInfo: null,
  research: null,
  activeTab: 'decision-intel',
  chainSymbol: 'NIFTY',
  sidebarOpen: false,
  commandQuery: '',

  setWsStatus: (wsStatus) => set({ wsStatus }),
  setHealth: (health) => set((s) => {
    // CRITICAL: health uses cached SSOT and must NOT clobber a live broker_status=true.
    // This race was the long-standing "broker disconnect flicker" on the TopBar/Sidebar.
    const healthConnected = health?.broker?.connected
    const statusText = String(health?.broker_status || health?.broker?.status || '').toLowerCase()
    const statusConnected = s.brokerStatus?.connected
    let brokerConnected = s.brokerConnected
    if (healthConnected === true || statusText === 'connected' || statusText === 'ok') brokerConnected = true
    else if (healthConnected === false && statusConnected !== true) brokerConnected = false
    // if health says false/missing but brokerStatus says true → keep true
    return {
      health,
      brokerConnected,
      marketOpen: marketOpenFromHealth(health, s.marketOpen),
      lastSync: new Date().toISOString(),
    }
  }),
  setState: (state) => set((s) => ({
    state,
    marketOpen: state?.market?.is_open != null ? Boolean(state.market.is_open) : s.marketOpen,
  })),
  setChain: (sym, data) => set((s) => ({
    chain: { ...s.chain, [sym]: data },
    lastSync: new Date().toISOString(),
  })),
  setPaper: (paper) => set({ paper }),
  setGainRank: (gainRank) => set({ gainRank }),
  setMarketTop: (marketTop) => set({ marketTop, lastSync: new Date().toISOString() }),
  setAlerts: (alerts) => set({ alerts }),
  setAlertFeedStatus: (alertFeedStatus) => set({ alertFeedStatus }),
  setAutoGates: (autoGates) => set({ autoGates }),
  setPnl: (pnl) => set({ pnl }),
  setApiStatus: (apiStatus) => set({ apiStatus }),
  setBrokerStatus: (brokerStatus) => set((s) => {
    // Authoritative broker truth wins; never force false on undefined.
    const next =
      brokerStatus?.connected === true
        ? true
        : brokerStatus?.connected === false
          ? false
          : s.brokerConnected
    return { brokerStatus, brokerConnected: next }
  }),
  setBrokerHoldings: (brokerHoldings) => set({ brokerHoldings }),
  setBrokerFunds: (brokerFunds) => set({ brokerFunds }),
  setBrokerPositions: (brokerPositions) => set({ brokerPositions }),
  setLiveBoard: (liveBoard) => set({ liveBoard, lastSync: new Date().toISOString() }),
  setActiveTab: (activeTab) => set({ activeTab, sidebarOpen: false }),
  setChainSymbol: (chainSymbol) => set({ chainSymbol }),
  setDeployInfo: (deployInfo) => set({ deployInfo }),
  setResearch: (research) => set({ research }),
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  setCommandQuery: (commandQuery) => set({ commandQuery }),
}))

if (typeof window !== 'undefined') {
  (window as any).useStore = useStore
}
