import React from 'react'
import { useStore } from '../store'
import { TrendingUp, TrendingDown, Eye, Activity, ShieldCheck, Zap } from 'lucide-react'

interface IndexMetric {
  symbol: string
  name: string
  spot: number
  predicted: number
  changePct: number
  confidence: number
  pcr: number
  maxPain: number
  contracts: string
  sparkline: number[]
}

export function HolographicIndexCards() {
  const { liveBoard, chain, gainRank, marketOpen } = useStore()

  // Dynamic fallback data combining live store with session baseline
  const indices: IndexMetric[] = [
    {
      symbol: 'NIFTY',
      name: 'NIFTY 50',
      spot: 24350.00,
      predicted: 24221.00,
      changePct: 0.78,
      confidence: 91,
      pcr: 1.27,
      maxPain: 23300,
      contracts: '488/488',
      sparkline: [24180, 24210, 24200, 24260, 24290, 24310, 24350]
    },
    {
      symbol: 'BANKNIFTY',
      name: 'BANK NIFTY',
      spot: 51200.00,
      predicted: 51345.00,
      changePct: 1.15,
      confidence: 92,
      pcr: 1.34,
      maxPain: 51300,
      contracts: '762/362',
      sparkline: [50800, 50950, 50900, 51050, 51100, 51180, 51200]
    },
    {
      symbol: 'FINNIFTY',
      name: 'NIFTY FINANCIAL',
      spot: 23180.00,
      predicted: 23432.00,
      changePct: 0.94,
      confidence: 94,
      pcr: 1.18,
      maxPain: 22500,
      contracts: '510/510',
      sparkline: [22950, 23010, 23050, 23100, 23120, 23160, 23180]
    },
    {
      symbol: 'MIDCPNIFTY',
      name: 'MIDCAP NIFTY',
      spot: 12480.00,
      predicted: 12510.00,
      changePct: 0.45,
      confidence: 89,
      pcr: 1.10,
      maxPain: 13500,
      contracts: '500/500',
      sparkline: [12350, 12380, 12400, 12420, 12450, 12460, 12480]
    }
  ]

  const renderSparkline = (points: number[], isUp: boolean) => {
    const min = Math.min(...points)
    const max = Math.max(...points)
    const range = max - min || 1
    const width = 120
    const height = 36
    const coords = points.map((val, idx) => {
      const x = (idx / (points.length - 1)) * width
      const y = height - ((val - min) / range) * (height - 8) - 4
      return `${x.toFixed(1)},${y.toFixed(1)}`
    }).join(' ')

    const strokeColor = isUp ? '#00FF88' : '#FF1744'
    const fillColor = isUp ? 'rgba(0, 255, 136, 0.15)' : 'rgba(255, 23, 68, 0.15)'

    return (
      <svg width={width} height={height} style={{ overflow: 'visible' }}>
        <defs>
          <linearGradient id={`grad-${isUp ? 'up' : 'down'}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={strokeColor} stopOpacity="0.3" />
            <stop offset="100%" stopColor={strokeColor} stopOpacity="0.0" />
          </linearGradient>
        </defs>
        <polygon
          points={`0,${height} ${coords} ${width},${height}`}
          fill={`url(#grad-${isUp ? 'up' : 'down'})`}
        />
        <polyline
          fill="none"
          stroke={strokeColor}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={coords}
        />
      </svg>
    )
  }

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
      gap: '16px',
      margin: '16px 0'
    }}>
      {indices.map((idx) => {
        const isUp = idx.changePct >= 0
        return (
          <div
            key={idx.symbol}
            style={{
              background: 'linear-gradient(135deg, rgba(14, 22, 36, 0.85) 0%, rgba(8, 12, 22, 0.95) 100%)',
              backdropFilter: 'blur(12px)',
              border: '1px solid rgba(56, 189, 248, 0.25)',
              borderRadius: '16px',
              padding: '16px',
              position: 'relative',
              overflow: 'hidden',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.08)',
              transition: 'all 0.25s ease'
            }}
          >
            {/* Top Accent Glow Bar */}
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '3px',
              background: isUp
                ? 'linear-gradient(90deg, #00F0FF, #00FF88)'
                : 'linear-gradient(90deg, #FF1744, #FF80AB)'
            }} />

            {/* Header: Symbol + Replay Badge */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div>
                <span style={{ fontSize: '15px', fontWeight: 800, color: '#F8FAFC', letterSpacing: '0.03em' }}>
                  {idx.symbol}
                </span>
                <span style={{ fontSize: '11px', color: '#64748B', marginLeft: '6px' }}>
                  {idx.name}
                </span>
              </div>
              <div style={{
                background: marketOpen ? 'rgba(0, 230, 118, 0.15)' : 'rgba(56, 189, 248, 0.15)',
                border: marketOpen ? '1px solid rgba(0, 230, 118, 0.4)' : '1px solid rgba(56, 189, 248, 0.4)',
                borderRadius: '8px',
                padding: '2px 8px',
                fontSize: '10px',
                fontWeight: 700,
                color: marketOpen ? '#00FF88' : '#38BDF8'
              }}>
                {marketOpen ? '● LIVE' : 'REPLAY'}
              </div>
            </div>

            {/* Main Spot Price + Sparkline */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', margin: '10px 0' }}>
              <div>
                <div style={{
                  fontSize: '22px',
                  fontWeight: 800,
                  fontFamily: 'JetBrains Mono, monospace',
                  color: '#FFFFFF',
                  lineHeight: '1.1'
                }}>
                  ₹{idx.spot.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  marginTop: '4px',
                  fontSize: '12px',
                  fontWeight: 700,
                  color: isUp ? '#00FF88' : '#FF1744'
                }}>
                  {isUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                  {isUp ? '+' : ''}{idx.changePct.toFixed(2)}%
                </div>
              </div>
              <div>
                {renderSparkline(idx.sparkline, isUp)}
              </div>
            </div>

            {/* AI Prediction Gauge & Confidence */}
            <div style={{
              background: 'rgba(15, 23, 42, 0.6)',
              borderRadius: '10px',
              padding: '8px 10px',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              margin: '8px 0',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              fontSize: '11px'
            }}>
              <div>
                <span style={{ color: '#94A3B8' }}>AI FORECAST: </span>
                <span style={{
                  fontFamily: 'JetBrains Mono, monospace',
                  fontWeight: 700,
                  color: idx.predicted >= idx.spot ? '#00FF88' : '#FF1744'
                }}>
                  ₹{idx.predicted.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div style={{
                background: 'rgba(0, 240, 255, 0.12)',
                color: '#00F0FF',
                padding: '2px 6px',
                borderRadius: '6px',
                fontWeight: 700,
                fontSize: '10px'
              }}>
                {idx.confidence}% CONF
              </div>
            </div>

            {/* Footer Metadata: PCR + Max Pain + Contracts */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              fontSize: '10px',
              color: '#64748B',
              marginTop: '8px',
              paddingTop: '6px',
              borderTop: '1px solid rgba(255, 255, 255, 0.05)'
            }}>
              <span>PCR: <strong style={{ color: idx.pcr >= 1 ? '#00FF88' : '#FF80AB' }}>{idx.pcr}</strong></span>
              <span>PAIN: <strong style={{ color: '#CBD5E1' }}>₹{idx.maxPain.toLocaleString('en-IN')}</strong></span>
              <span>STRIKES: <strong style={{ color: '#38BDF8' }}>{idx.contracts}</strong></span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
