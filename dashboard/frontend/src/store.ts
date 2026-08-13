import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
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
  positions: [],
  orders: [],
  alerts: [],
  paper: {},
  autoGates: {},
  brokerConnected: false,
  health: {},
  isLoading: false,
  error: null,
  lastUpdate: 0,
  lastDataUpdate: {},
  connectionHealth: { status: 'connecting' as const, latency: 0 },
};

export const useStore = create<AppState>()(
  devtools(
    immer((set, get) => ({
      ...initialState,

      // ── UI Actions ────────────────────────────────────────────────
      setActiveTab: (tab: string) => set(state => {
        state.activeTab = tab;
      }),

      setSidebarOpen: (open: boolean) => set(state => {
        state.sidebarOpen = open;
      }),

      setDarkMode: (dark: boolean) => set(state => {
        state.darkMode = dark;
      }),

      // ── Data Actions ──────────────────────────────────────────────
      setPositions: (positions: Position[]) => set(state => {
        state.positions = positions;
        state.lastUpdate = Date.now();
        state.lastDataUpdate['positions'] = Date.now();
      }),

      addPosition: (position: Position) => set(state => {
        const existing = state.positions.find(p => p.id === position.id);
        if (!existing) {
          state.positions.push(position);
          state.lastUpdate = Date.now();
        }
      }),

      updatePosition: (id: string, updates: Partial<Position>) => set(state => {
        const position = state.positions.find(p => p.id === id);
        if (position) {
          Object.assign(position, updates);
          state.lastUpdate = Date.now();
        }
      }),

      removePosition: (id: string) => set(state => {
        state.positions = state.positions.filter(p => p.id !== id);
        state.lastUpdate = Date.now();
      }),

      setOrders: (orders: Order[]) => set(state => {
        state.orders = orders;
        state.lastUpdate = Date.now();
        state.lastDataUpdate['orders'] = Date.now();
      }),

      addOrder: (order: Order) => set(state => {
        const existing = state.orders.find(o => o.id === order.id);
        if (!existing) {
          state.orders.push(order);
          state.lastUpdate = Date.now();
        }
      }),

      updateOrder: (id: string, updates: Partial<Order>) => set(state => {
        const order = state.orders.find(o => o.id === id);
        if (order) {
          Object.assign(order, updates);
          state.lastUpdate = Date.now();
        }
      }),

      setAlerts: (alerts: Alert[]) => set(state => {
        state.alerts = alerts;
        state.lastDataUpdate['alerts'] = Date.now();
      }),

      addAlert: (alert: Alert) => set(state => {
        const existing = state.alerts.find(a => a.id === alert.id);
        if (!existing) {
          state.alerts.unshift(alert);
          if (state.alerts.length > 500) state.alerts.pop();
        }
      }),

      markAlertRead: (id: string) => set(state => {
        const alert = state.alerts.find(a => a.id === id);
        if (alert) alert.read = true;
      }),

      clearAlerts: (type?: Alert['type']) => set(state => {
        if (type) {
          state.alerts = state.alerts.filter(a => a.type !== type);
        } else {
          state.alerts = [];
        }
      }),

      setPaper: (paper: Partial<PaperTradingState>) => set(state => {
        state.paper = { ...state.paper, ...paper };
        state.lastUpdate = Date.now();
        state.lastDataUpdate['paper'] = Date.now();
      }),

      setAutoGates: (gates: AutoGatesData) => set(state => {
        state.autoGates = gates;
        state.lastUpdate = Date.now();
      }),

      setBrokerConnected: (connected: boolean) => set(state => {
        state.brokerConnected = connected;
        state.lastUpdate = Date.now();
      }),

      setHealth: (health: Record<string, any>) => set(state => {
        state.health = health;
      }),

      // ── Network Actions ───────────────────────────────────────────
      setLoading: (loading: boolean) => set(state => {
        state.isLoading = loading;
      }),

      setError: (error: string | null) => set(state => {
        state.error = error;
      }),

      updateDataTimestamp: (key: string) => set(state => {
        state.lastDataUpdate[key] = Date.now();
        state.lastUpdate = Date.now();
      }),

      setConnectionHealth: (health: Partial<ConnectionHealth>) => set(state => {
        state.connectionHealth = { ...state.connectionHealth, ...health };
      }),

      // ── Computed Selectors ────────────────────────────────────────
      getPositionsByStrategy: (strategy: string) => {
        return get().positions.filter(p => p.strategy === strategy);
      },

      getTotalPnL: () => {
        return get().positions.reduce((sum, p) => sum + (p.pnl || 0), 0);
      },

      getActiveOrderCount: () => {
        return get().orders.filter(o => o.status === 'pending').length;
      },

      getUnreadAlertCount: () => {
        return get().alerts.filter(a => !a.read).length;
      },

      getAlertsByType: (type: Alert['type']) => {
        return get().alerts.filter(a => a.type === type);
      },

      getDataStaleness: (key: string) => {
        const timestamp = get().lastDataUpdate[key];
        if (!timestamp) return Infinity;
        return Date.now() - timestamp;
      },

      isDataStale: (key: string, ttlMs: number) => {
        return get().getDataStaleness(key) > ttlMs;
      },

      // ── Utilities ─────────────────────────────────────────────────
      reset: () => set(initialState),
    })),
    { name: 'GenesisStore', trace: true }
  )
);
