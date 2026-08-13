import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

export interface Position {
  id: string;
  symbol: string;
  qty: number;
  avg_price: number;
  current_price: number;
  pnl: number;
  pnl_percent: number;
  strategy: string;
  entry_time: string;
  status: 'active' | 'closed';
}

export interface Order {
  id: string;
  symbol: string;
  qty: number;
  price: number;
  side: 'BUY' | 'SELL';
  status: 'pending' | 'filled' | 'rejected' | 'cancelled';
  created_at: string;
  filled_at?: string;
}

export interface Alert {
  id: string;
  type: 'price' | 'signal' | 'risk' | 'system';
  symbol?: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  active: boolean;
  created_at: string;
  read: boolean;
}

export interface PaperTradingState {
  initial_capital: number;
  current_capital: number;
  pnl_today: number;
  pnl_week: number;
  pnl_month: number;
  win_rate: number;
  sharpe_ratio: number;
  max_drawdown: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  avg_pnl_per_trade: number;
  daily_returns?: Array<{ date: string; return: number; cumulative: number }>;
  summary?: any;
}

export interface AutoGatesData {
  gates?: Record<string, any>;
  proof_gates?: Array<any>;
}

export interface ConnectionHealth {
  status: 'connected' | 'connecting' | 'disconnected' | 'error';
  latency: number;
  lastHeartbeat?: number;
  reconnectAttempts?: number;
}

export interface AppState {
  // ── UI State ──────────────────────────────────────────────────
  activeTab: string;
  sidebarOpen: boolean;
  darkMode: boolean;

  // ── Core Data State ───────────────────────────────────────────
  positions: Position[];
  orders: Order[];
  alerts: Alert[];
  paper: Partial<PaperTradingState>;
  autoGates: AutoGatesData;
  brokerConnected: boolean;
  health: Record<string, any>;

  // ── Network State ─────────────────────────────────────────────
  isLoading: boolean;
  error: string | null;
  lastUpdate: number;
  lastDataUpdate: Record<string, number>;
  connectionHealth: ConnectionHealth;

  // ── UI Actions ────────────────────────────────────────────────
  setActiveTab: (tab: string) => void;
  setSidebarOpen: (open: boolean) => void;
  setDarkMode: (dark: boolean) => void;

  // ── Data Actions ──────────────────────────────────────────────
  setPositions: (positions: Position[]) => void;
  addPosition: (position: Position) => void;
  updatePosition: (id: string, updates: Partial<Position>) => void;
  removePosition: (id: string) => void;

  setOrders: (orders: Order[]) => void;
  addOrder: (order: Order) => void;
  updateOrder: (id: string, updates: Partial<Order>) => void;

  setAlerts: (alerts: Alert[]) => void;
  addAlert: (alert: Alert) => void;
  markAlertRead: (id: string) => void;
  clearAlerts: (type?: Alert['type']) => void;

  setPaper: (paper: Partial<PaperTradingState>) => void;
  setAutoGates: (gates: AutoGatesData) => void;
  setBrokerConnected: (connected: boolean) => void;
  setHealth: (health: Record<string, any>) => void;

  // ── Network Actions ───────────────────────────────────────────
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  updateDataTimestamp: (key: string) => void;
  setConnectionHealth: (health: Partial<ConnectionHealth>) => void;

  // ── Computed Selectors ────────────────────────────────────────
  getPositionsByStrategy: (strategy: string) => Position[];
  getTotalPnL: () => number;
  getActiveOrderCount: () => number;
  getUnreadAlertCount: () => number;
  getAlertsByType: (type: Alert['type']) => Alert[];
  getDataStaleness: (key: string) => number;
  isDataStale: (key: string, ttlMs: number) => boolean;

  // ── Utilities ─────────────────────────────────────────────────
  reset: () => void;
}

// ───────────────────────────────────────────────────────────────────
// Store Implementation
// ───────────────────────────────────────────────────────────────────

const initialState = {
  activeTab: 'decision-intel',
  sidebarOpen: true,
  darkMode: true,
  positions: [] as Position[],
  orders: [] as Order[],
  alerts: [] as Alert[],
  paper: {} as Partial<PaperTradingState>,
  autoGates: {} as AutoGatesData,
  brokerConnected: false,
  health: {} as Record<string, any>,
  isLoading: false,
  error: null as string | null,
  lastUpdate: 0,
  lastDataUpdate: {} as Record<string, number>,
  connectionHealth: { status: 'connecting' as const, latency: 0 },
};

export const useStore = create<AppState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // ── UI Actions ────────────────────────────────────────────────
      setActiveTab: (tab: string) => set({ activeTab: tab }),
      setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),
      setDarkMode: (dark: boolean) => set({ darkMode: dark }),

      // ── Data Actions ──────────────────────────────────────────────
      setPositions: (positions: Position[]) => {
        const now = Date.now();
        set(state => ({
          positions,
          lastUpdate: now,
          lastDataUpdate: { ...state.lastDataUpdate, positions: now },
        }));
      },

      addPosition: (position: Position) => set(state => {
        if (state.positions.some(p => p.id === position.id)) return {};
        return {
          positions: [...state.positions, position],
          lastUpdate: Date.now(),
        };
      }),

      updatePosition: (id: string, updates: Partial<Position>) => set(state => {
        if (!state.positions.some(p => p.id === id)) return {};
        return {
          positions: state.positions.map(p => p.id === id ? { ...p, ...updates } : p),
          lastUpdate: Date.now(),
        };
      }),

      removePosition: (id: string) => set(state => ({
        positions: state.positions.filter(p => p.id !== id),
        lastUpdate: Date.now(),
      })),

      setOrders: (orders: Order[]) => {
        const now = Date.now();
        set(state => ({
          orders,
          lastUpdate: now,
          lastDataUpdate: { ...state.lastDataUpdate, orders: now },
        }));
      },

      addOrder: (order: Order) => set(state => {
        if (state.orders.some(o => o.id === order.id)) return {};
        return {
          orders: [...state.orders, order],
          lastUpdate: Date.now(),
        };
      }),

      updateOrder: (id: string, updates: Partial<Order>) => set(state => {
        if (!state.orders.some(o => o.id === id)) return {};
        return {
          orders: state.orders.map(o => o.id === id ? { ...o, ...updates } : o),
          lastUpdate: Date.now(),
        };
      }),

      setAlerts: (alerts: Alert[]) => {
        const now = Date.now();
        set(state => ({
          alerts,
          lastDataUpdate: { ...state.lastDataUpdate, alerts: now },
        }));
      },

      addAlert: (alert: Alert) => set(state => {
        if (state.alerts.some(a => a.id === alert.id)) return {};
        return { alerts: [alert, ...state.alerts].slice(0, 500) };
      }),

      markAlertRead: (id: string) => set(state => ({
        alerts: state.alerts.map(a => a.id === id ? { ...a, read: true } : a),
      })),

      clearAlerts: (type?: Alert['type']) => set(state => ({
        alerts: type ? state.alerts.filter(a => a.type !== type) : [],
      })),

      setPaper: (paper: Partial<PaperTradingState>) => {
        const now = Date.now();
        set(state => ({
          paper: { ...state.paper, ...paper },
          lastUpdate: now,
          lastDataUpdate: { ...state.lastDataUpdate, paper: now },
        }));
      },

      setAutoGates: (gates: AutoGatesData) => set({
        autoGates: gates,
        lastUpdate: Date.now(),
      }),

      setBrokerConnected: (connected: boolean) => set({
        brokerConnected: connected,
        lastUpdate: Date.now(),
      }),

      setHealth: (health: Record<string, any>) => set({ health }),

      // ── Network Actions ───────────────────────────────────────────
      setLoading: (loading: boolean) => set({ isLoading: loading }),
      setError: (error: string | null) => set({ error }),

      updateDataTimestamp: (key: string) => {
        const now = Date.now();
        set(state => ({
          lastDataUpdate: { ...state.lastDataUpdate, [key]: now },
          lastUpdate: now,
        }));
      },

      setConnectionHealth: (health: Partial<ConnectionHealth>) => set(state => ({
        connectionHealth: { ...state.connectionHealth, ...health },
      })),

      // ── Computed Selectors ────────────────────────────────────────
      getPositionsByStrategy: (strategy: string) =>
        get().positions.filter(p => p.strategy === strategy),

      getTotalPnL: () =>
        get().positions.reduce((sum, p) => sum + (p.pnl || 0), 0),

      getActiveOrderCount: () =>
        get().orders.filter(o => o.status === 'pending').length,

      getUnreadAlertCount: () =>
        get().alerts.filter(a => !a.read).length,

      getAlertsByType: (type: Alert['type']) =>
        get().alerts.filter(a => a.type === type),

      getDataStaleness: (key: string) => {
        const timestamp = get().lastDataUpdate[key];
        return timestamp ? Date.now() - timestamp : Infinity;
      },

      isDataStale: (key: string, ttlMs: number) =>
        get().getDataStaleness(key) > ttlMs,

      // ── Utilities ─────────────────────────────────────────────────
      reset: () => set(initialState),
    }),
    { name: 'GenesisStore', trace: true }
  )
);
