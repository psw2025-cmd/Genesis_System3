import React from 'react'
import { useStore } from '../store'
import { Activity, ShieldCheck, Clock } from 'lucide-react'
import { brokerPermissionLabel, requiredChainCounts } from '../lib/lifecycleTruth'
import { resolveFeedQuality } from '../lib/feedQuality'

export function TruthStrip() {
  const { wsStatus, brokerConnected, brokerStatus, marketOpen, state, health, deployInfo, chain } = useStore()
  const permission = brokerPermissionLabel({ brokerConnected, brokerStatus, health, state })
  const chains = requiredChainCounts(chain)
  const latency = brokerStatus?.latency_ms
  const feed = resolveFeedQuality({
    marketOpen,
    wsStatus,
    tickAgeSec: state?.last_tick_age_sec ?? state?.tick_health?.last_tick_age_sec,
    dataSource: state?.data_source || health?.data_source,
    brokerConnected,
  })
  const transport = wsStatus === 'live' ? 'CONNECTED'
    : wsStatus === 'connecting' ? 'CONNECTING'
      : wsStatus === 'error' ? 'ERROR' : 'DISCONNECTED'
  const feedTone = {
    ok: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
    warn: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
    error: 'text-rose-400 border-rose-500/30 bg-rose-500/10',
    mut: 'text-slate-300 border-slate-700 bg-slate-950',
  }[feed.tone]
  
  // Authoritative live deployed SHA resolution (never hardcoded fallback)
  const deploySha = deployInfo?.git_sha
    || (state as any)?.deployment_sha
    || (state as any)?.git_sha
    || (health as any)?.git_sha
    || ''
    
  return (
    <div className="truth-strip bg-slate-900/90 border-b border-slate-800/80 px-3 md:px-4 py-2 text-xs text-slate-300 font-sans shadow-sm z-30 shrink-0 flex flex-wrap items-center justify-between gap-2 overflow-x-hidden">
      {/* 1. Single Truth Badge */}
      <div className="truth-strip-brand flex items-center gap-2 shrink-0">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-950 border border-slate-700 text-slate-300 font-bold tracking-wide">
          <span className="w-2 h-2 rounded-full bg-slate-500" />
          <span>SYSTEM STATUS</span>
        </div>
        <span className="text-slate-600">|</span>
        <span className="text-slate-200 font-semibold">GENESIS SYSTEM3 v2.8</span>
      </div>

      {/* 2. Telemetry Badges */}
      <div className="truth-strip-telemetry flex flex-wrap items-center gap-1.5 md:gap-2">
        {/* Dynamic Serving SHA */}
        <div className="flex items-center gap-1.5 bg-slate-950 px-2.5 py-1 rounded-md border border-slate-800">
          <span className="text-slate-400 font-medium">SERVING:</span>
          <span className="font-mono text-sky-400 font-bold">
            {deploySha ? String(deploySha).slice(0, 7) : '—'}
          </span>
        </div>

        {/* Broker Status */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md border font-semibold bg-amber-500/10 border-amber-500/30 text-amber-400">
          <ShieldCheck size={14} />
          <span>DHAN {permission}</span>
        </div>

        {/* Data freshness and socket transport are separate facts. */}
        <div data-testid="market-data-status" title={feed.detail} className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border font-semibold ${feedTone}`}>
          <Activity size={13} aria-hidden />
          <span>MARKET DATA: {feed.label.toUpperCase()}</span>
        </div>
        <div data-testid="websocket-transport-status" title="WebSocket status describes the dashboard connection, not market-data freshness." className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-950/70 border border-slate-800/80 text-[11px] text-slate-400">
          <span className={`w-1.5 h-1.5 rounded-full ${wsStatus === 'live' ? 'bg-emerald-400' : wsStatus === 'error' || wsStatus === 'off' ? 'bg-rose-400' : 'bg-amber-400'}`} />
          <span className="text-slate-400 text-[10px]">WS:</span>
          <span className={`font-medium ${wsStatus === 'live' ? 'text-emerald-400' : wsStatus === 'error' || wsStatus === 'off' ? 'text-rose-400' : 'text-amber-400'}`}>{transport}</span>
        </div>

        {/* Option Chains */}
        <div className="truth-strip-chains flex items-center gap-1.5 bg-slate-950 px-2.5 py-1 rounded-md border border-slate-800">
          <span className="text-slate-400 font-medium">CHAINS:</span>
          <span className="text-amber-300 font-bold">required_ready {chains.requiredReady}/{chains.total} · safe_no_trade {chains.safeNoTrade}/{chains.total} · {chains.tradableLabel}</span>
        </div>
      </div>

      {/* 3. Market State & Latency */}
      <div className="truth-strip-market flex items-center gap-1.5 shrink-0">
        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md border font-bold text-[11px] ${
          marketOpen
            ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-400'
            : 'bg-slate-800/80 border-slate-700 text-slate-300'
        }`}>
          <Clock size={13} />
          <span>{marketOpen ? 'MARKET OPEN' : 'MARKET CLOSED'}</span>
        </div>

        <div className="hidden sm:flex items-center gap-1 px-2 py-1 rounded-md bg-slate-950 border border-slate-700 text-slate-300 font-mono text-[11px] font-semibold">
          <Clock size={12} />
          <span>LATENCY: {latency != null ? `${latency}ms read-only` : 'PENDING'}</span>
        </div>
      </div>
    </div>
  )
}
export default TruthStrip
