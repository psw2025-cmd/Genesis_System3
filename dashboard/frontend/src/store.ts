import { create } from 'zustand'

interface DashboardState {
  // Connection
  wsStatus: 'connecting' | 'live' | 'error' | 'off'
  brokerConnected: boolean
  marketOpen: boolean
  marketCountdown: string
  lastSync: string

  // Live data
  health: any
  state: any
  chain: Record<string, any>
  paper: any
  gainRank: any
  alerts: any[]
  autoGates: any

  // UI
  activeTab: string
  chainSymbol: string

  // Actions
  setWsStatus: (s: DashboardState['wsStatus']) => void
  setHealth: (d: any) => void
  setState: (d: any) => void
  setChain: (sym: string, d: any) => void
  setPaper: (d: any) => void
  setGainRank: (d: any) => void
  setAlerts: (d: any[]) => void
  setAutoGates: (d: any) => void
  setActiveTab: (t: string) => void
  setChainSymbol: (s: string) => void
}

export const useStore = create<DashboardState>((set) => ({
  wsStatus: 'connecting',
  brokerConnected: false,
  marketOpen: false,
  marketCountdown: '--',
  lastSync: '--',
  health: null,
  state: null,
  chain: {},
  paper: null,
  gainRank: null,
  alerts: [],
  autoGates: null,
  activeTab: 'trade',
  chainSymbol: 'NIFTY',

  setWsStatus: (wsStatus) => set({ wsStatus }),
  setHealth: (health) => set({
    health,
    brokerConnected: health?.broker?.connected ?? false,
    marketOpen: health?.market?.is_open ?? false,
  }),
  setState: (state) => set({ state }),
  setChain: (sym, data) => set((s) => ({ chain: { ...s.chain, [sym]: data } })),
  setPaper: (paper) => set({ paper }),
  setGainRank: (gainRank) => set({ gainRank }),
  setAlerts: (alerts) => set({ alerts }),
  setAutoGates: (autoGates) => set({ autoGates }),
  setActiveTab: (activeTab) => set({ activeTab }),
  setChainSymbol: (chainSymbol) => set({ chainSymbol }),
}))
