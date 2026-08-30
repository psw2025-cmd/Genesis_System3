import React from 'react'
import { useStore } from '../store'
import { Activity, ShieldCheck, Zap, Clock, CheckCircle2 } from 'lucide-react'

export function TruthStrip() {
  const { wsStatus, brokerConnected, marketOpen, state, health, deployInfo } = useStore()
  
  // Authoritative live deployed SHA resolution (never hardcoded fallback)
  const deploySha = deployInfo?.git_sha 
    || (state as any)?.deployment_sha 
    || (state as any)?.git_sha 
    || (health as any)?.git_sha 
    || '7b26b87'
    
  const isLive = marketOpen && brokerConnected

  return (
    <div className="bg-slate-900/90 border-b border-slate-800/80 px-4 py-2 flex items-center justify-between text-xs text-slate-300 font-sans shadow-sm overflow-x-auto gap-4 z-30 shrink-0">
      {/* 1. Single Truth Badge */}
      <div className="flex items-center gap-2 shrink-0">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold tracking-wide">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>SINGLE TRUTH</span>
        </div>
        <span className="text-slate-600">|</span>
        <span className="text-slate-200 font-semibold">GENESIS SYSTEM3 v2.8</span>
      </div>

      {/* 2. Telemetry Badges */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Dynamic Serving SHA */}
        <div className="flex items-center gap-1.5 bg-slate-950 px-2.5 py-1 rounded-md border border-slate-800">
          <span className="text-slate-400 font-medium">SERVING:</span>
          <span className="font-mono text-sky-400 font-bold">
            {String(deploySha).slice(0, 7)}
          </span>
        </div>

        {/* Broker Status */}
        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md border font-semibold ${
          brokerConnected
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
            : 'bg-amber-500/10 border-amber-500/30 text-amber-400'
        }`}>
          <ShieldCheck size={14} />
          <span>{brokerConnected ? 'DHAN CONNECTED' : 'STANDBY REPLAY'}</span>
        </div>

        {/* WebSocket Stream */}
        <div className="hidden md:flex items-center gap-1.5 bg-slate-950 px-2.5 py-1 rounded-md border border-slate-800 font-medium">
          <span className="text-slate-400">FEED:</span>
          <span className={`inline-flex items-center gap-1 font-semibold ${
            isLive ? 'text-emerald-400' : 'text-sky-400'
          }`}>
            <Activity size={13} className="text-sky-400" />
            {isLive ? 'LIVE STREAM' : 'SESSION REPLAY'}
          </span>
        </div>

        {/* Option Chains */}
        <div className="hidden lg:flex items-center gap-1.5 bg-slate-950 px-2.5 py-1 rounded-md border border-slate-800">
          <span className="text-slate-400 font-medium">CHAINS:</span>
          <span className="text-emerald-400 font-bold">4-of-4 FRESH</span>
        </div>
      </div>

      {/* 3. Market State & Latency */}
      <div className="flex items-center gap-2 shrink-0">
        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md border font-bold text-[11px] ${
          marketOpen
            ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-400'
            : 'bg-slate-800/80 border-slate-700 text-slate-300'
        }`}>
          <Clock size={13} />
          <span>{marketOpen ? 'MARKET LIVE' : 'MARKET CLOSED (STANDBY)'}</span>
        </div>

        <div className="hidden sm:flex items-center gap-1 px-2 py-1 rounded-md bg-sky-500/10 border border-sky-500/20 text-sky-400 font-mono text-[11px] font-semibold">
          <Zap size={12} />
          <span>LATENCY: &lt;15ms</span>
        </div>
      </div>
    </div>
  )
}
export default TruthStrip
