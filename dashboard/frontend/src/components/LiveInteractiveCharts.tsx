import React from 'react'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  Cell
} from 'recharts'

export interface TimeSeriesPoint {
  time: string
  price: number
  volume?: number
}

export function NiftyIntradayChart({
  spot,
  changePct,
  title = "NIFTY 50 Intraday Dynamics"
}: {
  spot?: number
  changePct?: number | null
  title?: string
}) {
  const base = Number(spot) > 0 ? Number(spot) : null
  const data = base == null ? [] : [{ time: 'SNAPSHOT', price: base, vol: 0 }]
  const isUp = (changePct ?? 0) >= 0

  return (
    <div className="card p-3" style={{ background: 'var(--surface-2, #0d1b2a)', border: '1px solid var(--border, #1e293b)', borderRadius: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <div>
          <div style={{ fontSize: '11px', color: 'var(--text-sec, #94a3b8)', fontWeight: 600 }}>{title}</div>
          <div className="num" style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-pri, #f8fafc)', marginTop: 2 }}>
            {base == null ? 'PENDING' : `₹${base.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          </div>
        </div>
        <span className="pill" style={{
          fontSize: '11px',
          fontWeight: 700,
          color: isUp ? 'var(--up, #10b981)' : 'var(--down, #ef4444)',
          background: isUp ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
          padding: '2px 8px',
          borderRadius: 4
        }}>
          {isUp ? '+' : ''}{(changePct ?? 0).toFixed(2)}%
        </span>
      </div>
      <div style={{ height: 110, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
            <defs>
              <linearGradient id="niftyGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={isUp ? "#10b981" : "#ef4444"} stopOpacity={0.4} />
                <stop offset="95%" stopColor={isUp ? "#10b981" : "#ef4444"} stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="2 2" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="time" stroke="#64748b" fontSize={9} tickLine={false} />
            <YAxis domain={['auto', 'auto']} stroke="#64748b" fontSize={9} tickLine={false} tickFormatter={(v) => `₹${Math.round(v)}`} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: 6, fontSize: 11 }}
              formatter={(val: any) => [`₹${Number(val).toFixed(2)}`, 'Spot Price']}
            />
            <Area type="monotone" dataKey="price" stroke={isUp ? "#10b981" : "#ef4444"} strokeWidth={2} fillOpacity={1} fill="url(#niftyGradient)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export function VolatilitySmileChart({
  strikes,
  ivs,
  spot,
}: {
  strikes?: number[]
  ivs?: number[]
  spot?: number
}) {
  const smileStrikes = Array.isArray(strikes) ? strikes : []
  const smileIvs = Array.isArray(ivs) ? ivs : []
  const data = smileStrikes.length && smileIvs.length
    ? smileStrikes.map((s, i) => ({
      strike: s,
      iv: smileIvs[i],
      isAtm: spot != null && Math.abs(s - spot) < 100,
    })).filter((row) => row.iv != null)
    : []

  return (
    <div className="card p-3" style={{ background: 'var(--surface-2, #0d1b2a)', border: '1px solid var(--border, #1e293b)', borderRadius: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <div>
          <div style={{ fontSize: '11px', color: 'var(--text-sec, #94a3b8)', fontWeight: 600 }}>Implied Volatility Smile (IV)</div>
          <div className="num" style={{ fontSize: '16px', fontWeight: 800, color: '#38bdf8', marginTop: 2 }}>
            {data.length ? `ATM IV: ${Number(data[Math.floor(data.length / 2)]?.iv).toFixed(1)}%` : 'ATM IV: PENDING'}
          </div>
        </div>
        <span style={{ fontSize: '10px', color: '#94a3b8', background: '#1e293b', padding: '2px 6px', borderRadius: 4 }}>
          Skew: Normal
        </span>
      </div>
      <div style={{ height: 110, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
            <CartesianGrid strokeDasharray="2 2" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="strike" stroke="#64748b" fontSize={9} tickLine={false} />
            <YAxis domain={['auto', 'auto']} stroke="#64748b" fontSize={9} tickLine={false} tickFormatter={(v) => `${v}%`} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: 6, fontSize: 11 }}
              formatter={(val: any) => [`${Number(val).toFixed(2)}%`, 'Implied Vol']}
            />
            {spot != null ? <ReferenceLine x={spot} stroke="#f59e0b" strokeDasharray="3 3" /> : null}
            <Line type="monotone" dataKey="iv" stroke="#38bdf8" strokeWidth={2} dot={{ r: 2, fill: '#38bdf8' }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export function PnlEquityCurveChart({
  pnlHistory = [],
  totalPnl = 0
}: {
  pnlHistory?: Array<{ date: string; pnl: number }>
  totalPnl?: number
}) {
  const data = pnlHistory.length > 0 ? pnlHistory : []
  const lastVal = data.length ? (data[data.length - 1]?.cumulative ?? totalPnl) : null
  const isUp = typeof lastVal === 'number' && lastVal > 0

  return (
    <div className="card p-3" style={{ background: 'var(--surface-2, #0d1b2a)', border: '1px solid var(--border, #1e293b)', borderRadius: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <div>
          <div style={{ fontSize: '11px', color: 'var(--text-sec, #94a3b8)', fontWeight: 600 }}>Cumulative Paper Equity Curve</div>
          <div className="num" style={{ fontSize: '16px', fontWeight: 800, color: isUp ? '#10b981' : '#ef4444', marginTop: 2 }}>
            {lastVal == null ? 'PENDING' : `₹${Number(lastVal).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          </div>
        </div>
        <span style={{ fontSize: '10px', color: '#10b981', background: 'rgba(16,185,129,0.1)', padding: '2px 6px', borderRadius: 4, fontWeight: 700 }}>
          High-Water
        </span>
      </div>
      <div style={{ height: 110, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="pnlGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="2 2" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="trade" stroke="#64748b" fontSize={9} tickLine={false} />
            <YAxis domain={['auto', 'auto']} stroke="#64748b" fontSize={9} tickLine={false} tickFormatter={(v) => `₹${v}`} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: 6, fontSize: 11 }}
              formatter={(val: any) => [`₹${Number(val).toFixed(2)}`, 'Cumulative P&L']}
            />
            <Area type="monotone" dataKey="cumulative" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#pnlGradient)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export function SpearmanAccuracyTrendChart({
  trend = []
}: {
  trend?: Array<{ date?: string; rho?: number; hit_rate?: number }>
}) {
  const data = trend.length > 0 ? trend : []
  const avgRho = data.length
    ? data.reduce((sum, row) => sum + Number(row.rho || 0), 0) / data.length
    : null

  return (
    <div className="card p-4" style={{ background: 'var(--surface-2, #0d1b2a)', border: '1px solid var(--border, #1e293b)', borderRadius: 8, marginTop: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div>
          <h3 style={{ fontSize: '13px', fontWeight: 700, margin: 0, color: 'var(--text-pri, #f8fafc)' }}>
            Rolling Spearman Rank Correlation (ρ) Trend
          </h3>
          <span style={{ fontSize: '11px', color: 'var(--text-mut, #94a3b8)' }}>
            5 Consecutive Validated Trading Days · Target Threshold: ρ ≥ 0.70
          </span>
        </div>
        <span style={{ fontSize: '12px', fontWeight: 800, color: '#10b981', background: 'rgba(16,185,129,0.1)', padding: '3px 10px', borderRadius: 6 }}>
          {avgRho == null ? 'Avg ρ PENDING' : `Avg ρ = ${avgRho.toFixed(4)}`}
        </span>
      </div>
      <div style={{ height: 180, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 15, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickFormatter={(d) => d.slice(5)} />
            <YAxis domain={[0.60, 0.85]} stroke="#64748b" fontSize={10} tickFormatter={(v) => v.toFixed(2)} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: 6, fontSize: 11 }}
              formatter={(val: any, name: string) => [
                name === 'rho' ? Number(val).toFixed(4) : `${(Number(val) * 100).toFixed(1)}%`,
                name === 'rho' ? 'Spearman ρ' : 'Hit Rate'
              ]}
            />
            <Legend wrapperStyle={{ fontSize: '11px' }} />
            <ReferenceLine y={0.70} stroke="#f59e0b" strokeDasharray="4 4" label={{ value: 'Target ρ ≥ 0.70', fill: '#f59e0b', fontSize: 10 }} />
            <Line type="monotone" dataKey="rho" name="Spearman ρ" stroke="#10b981" strokeWidth={3} dot={{ r: 4, fill: '#10b981' }} />
            <Line type="monotone" dataKey="hit_rate" name="Hit Rate (%)" stroke="#38bdf8" strokeWidth={2} strokeDasharray="2 2" dot={{ r: 3, fill: '#38bdf8' }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
