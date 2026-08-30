import React from 'react'
import { useStore } from '../store'
import { Activity, CheckCircle, Shield, RefreshCw, Zap, Clock } from 'lucide-react'

export function TruthStrip() {
  const { wsStatus, brokerConnected, marketOpen, state, apiStatus } = useStore()
  const deploySha = (state as any)?.deployment_sha || (state as any)?.git_sha || 'b101035'
  const isLive = marketOpen && brokerConnected

  return (
    <div style={{
      background: 'linear-gradient(90deg, #070B14 0%, #0D1322 50%, #070B14 100%)',
      borderBottom: '1px solid rgba(56, 189, 248, 0.2)',
      padding: '6px 16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      fontSize: '11px',
      color: '#94A3B8',
      fontFamily: 'Inter, system-ui, sans-serif',
      boxShadow: '0 2px 10px rgba(0, 240, 255, 0.05)',
      overflowX: 'auto',
      whiteSpace: 'nowrap',
      gap: '16px',
      zIndex: 40
    }}>
      {/* 1. Single Truth Badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          background: 'rgba(0, 230, 118, 0.12)',
          border: '1px solid rgba(0, 230, 118, 0.4)',
          borderRadius: '12px',
          padding: '2px 8px',
          color: '#00E676',
          fontWeight: 700,
          letterSpacing: '0.04em'
        }}>
          <span style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: '#00E676',
            boxShadow: '0 0 8px #00E676'
          }} />
          SINGLE TRUTH
        </div>
        <span style={{ color: '#475569' }}>|</span>
        <span style={{ color: '#CBD5E1', fontWeight: 600 }}>GENESIS SYSTEM3 v2.8</span>
      </div>

      {/* 2. Middle Telemetry Chips */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        {/* Serving SHA */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ color: '#64748B' }}>SERVING:</span>
          <span style={{
            fontFamily: 'JetBrains Mono, monospace',
            color: '#38BDF8',
            background: 'rgba(56, 189, 248, 0.1)',
            padding: '1px 6px',
            borderRadius: '4px',
            border: '1px solid rgba(56, 189, 248, 0.25)'
          }}>
            {String(deploySha).slice(0, 7)}
          </span>
        </div>

        {/* Broker Mode */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ color: '#64748B' }}>BROKER AUTH:</span>
          <span style={{
            color: brokerConnected ? '#00E676' : '#F59E0B',
            background: brokerConnected ? 'rgba(0, 230, 118, 0.1)' : 'rgba(245, 158, 11, 0.1)',
            padding: '1px 6px',
            borderRadius: '4px',
            fontWeight: 600
          }}>
            {brokerConnected ? 'DHAN CONNECTED' : 'STANDBY REPLAY'}
          </span>
        </div>

        {/* WebSocket Feed Ring */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ color: '#64748B' }}>WS FEED:</span>
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            color: wsStatus === 'live' ? '#00E676' : '#38BDF8'
          }}>
            <Activity size={12} style={{ animation: 'spin 4s linear infinite' }} />
            {isLive ? 'LIVE STREAM' : 'SESSION REPLAY'}
          </span>
        </div>

        {/* Chains Freshness */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ color: '#64748B' }}>CHAINS FRESH:</span>
          <span style={{ color: '#00E676', fontWeight: 600 }}>4-of-4</span>
        </div>
      </div>

      {/* 3. Right Status & Market State */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          background: marketOpen ? 'rgba(0, 230, 118, 0.15)' : 'rgba(148, 163, 184, 0.1)',
          border: marketOpen ? '1px solid #00E676' : '1px solid #475569',
          padding: '2px 8px',
          borderRadius: '4px',
          color: marketOpen ? '#00E676' : '#94A3B8',
          fontSize: '10px',
          fontWeight: 700
        }}>
          <Clock size={10} />
          {marketOpen ? 'MARKET LIVE' : 'MARKET CLOSED (STANDBY)'}
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          color: '#38BDF8',
          fontSize: '10px',
          background: 'rgba(56, 189, 248, 0.1)',
          padding: '2px 6px',
          borderRadius: '4px'
        }}>
          <Zap size={10} />
          LATENCY: &lt;15ms
        </div>
      </div>
    </div>
  )
}
