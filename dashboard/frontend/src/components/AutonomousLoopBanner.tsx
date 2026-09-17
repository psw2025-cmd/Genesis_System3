import { useEffect, useMemo, useState } from 'react'
import { useStore } from '../store'
import { shortSha } from '../lib/formatLive'
import { pickFutureNextOpen } from '../lib/nextMarketOpen'
import { brokerConnectedFromPayloads, gatesDisplay } from '../lib/sourceQuality'

const IST_FMT = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Asia/Kolkata',
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hour12: false,
})

export const AUTONOMOUS_LOOP_BANNER_ENABLED = true

export function AutonomousLoopBanner() {
  const {
    deployInfo, brokerStatus, brokerConnected, gainRank, chain, state, autoGates, marketOpen, health, setActiveTab,
  } = useStore()
  const [ist, setIst] = useState(() => `${IST_FMT.format(new Date()).replace(', ', ' ')} IST`)

  useEffect(() => {
    const t = window.setInterval(() => {
      setIst(`${IST_FMT.format(new Date()).replace(', ', ' ')} IST`)
    }, 1000)
    return () => window.clearInterval(t)
  }, [])

  const gates = gatesDisplay(autoGates)
  const passCount = gates.passCount
  const brokerOk = brokerConnectedFromPayloads(health, brokerStatus, brokerConnected).value
  const serving = deployInfo?.git_sha ? shortSha(deployInfo.git_sha) : deployInfo?.version ? String(deployInfo.version).slice(0, 7) : '—'
  const marketReason = String(state?.market?.reason || health?.market?.reason || '')
  const isWeekendClosed = /weekend/i.test(marketReason)
  const isHolidayClosed = /holiday/i.test(marketReason)
  const nextOpen = useMemo(
    () => pickFutureNextOpen([state?.market?.next_open, health?.market?.next_open]),
    [state?.market?.next_open, health?.market?.next_open, ist],
  )

  if (!AUTONOMOUS_LOOP_BANNER_ENABLED) return null

  return (
    <div
      data-testid="autonomous-loop-banner"
      role="status"
      className="bg-slate-900/95 border-b border-slate-800 px-4 py-2 text-xs text-slate-300 flex flex-wrap items-center justify-between gap-3 shrink-0"
    >
      <div className="flex flex-wrap items-center gap-3">
        {/* Session Badge */}
        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md font-bold ${
          marketOpen
            ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
            : 'bg-slate-800 text-slate-300 border border-slate-700'
        }`}>
          <span className={`w-2 h-2 rounded-full ${marketOpen ? 'bg-emerald-400 animate-pulse' : 'bg-slate-400'}`} />
          <span>{marketOpen ? 'MARKET SESSION OPEN' : `MARKET CLOSED${isHolidayClosed ? ' (HOLIDAY)' : isWeekendClosed ? ' (WEEKEND STANDBY)' : ' (AFTER HOURS)'}`}</span>
        </div>

        {!marketOpen && nextOpen !== '—' && (
          <div className="flex items-center gap-1.5 text-slate-300">
            <span>Next Live Market Open:</span>
            <span className="font-mono text-sky-400 font-bold">{nextOpen}</span>
          </div>
        )}
      </div>

      {/* System State Chips */}
      <div className="flex flex-wrap items-center gap-2 font-mono text-[11px]">
        <div className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300">
          BROKER: <strong className={brokerOk ? 'text-emerald-400' : 'text-rose-400'}>{brokerOk ? 'CONNECTED' : 'DISCONNECTED'}</strong>
        </div>
        <div className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300">
          SERVING: <strong className="text-sky-400">{serving}</strong>
        </div>
        <div className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300">
          GATES: <strong className={gates.stale ? 'text-amber-400' : 'text-emerald-400'}>{passCount}/{gates.total}{gates.stale ? ' STALE' : ''}</strong>
        </div>
        <div className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300">
          SAFETY: <strong className="text-emerald-400">PAPER LOCKED</strong>
        </div>
        <span className="text-slate-500 font-sans">{ist}</span>
      </div>
    </div>
  )
}
export default AutonomousLoopBanner
