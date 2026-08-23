import { useEffect, useMemo, useState } from 'react'
import { Activity, BarChart3, BriefcaseBusiness, Database, Layers3, Radio } from 'lucide-react'
import { useStore } from '../store'
import { OptionChain } from './OptionChain'
import Signals from './Signals'
import { PredictionAudit } from './workspaces/PredictionAudit'
import Backtest from './Backtest'
import { Positions } from './Positions'

type MobilePanel = 'options' | 'equities' | 'predictions' | 'backtest' | 'portfolio'

const PANELS: Array<{ id: MobilePanel; label: string; icon: typeof Layers3 }> = [
  { id: 'options', label: 'Options Chain', icon: Layers3 },
  { id: 'equities', label: 'Equity Feed', icon: Activity },
  { id: 'predictions', label: 'Prediction Charts', icon: BarChart3 },
  { id: 'backtest', label: 'Backtest', icon: Database },
  { id: 'portfolio', label: 'Portfolio', icon: BriefcaseBusiness },
]

function usePhoneLayout() {
  const query = '(max-width: 820px)'
  const [phone, setPhone] = useState(() => typeof window !== 'undefined' && window.matchMedia(query).matches)

  useEffect(() => {
    const media = window.matchMedia(query)
    const update = () => setPhone(media.matches)
    update()
    media.addEventListener?.('change', update)
    return () => media.removeEventListener?.('change', update)
  }, [])

  return phone
}

function positionCount(value: any) {
  const rows = value?.positions ?? value?.data ?? value?.rows
  return Array.isArray(rows) ? rows.length : Number(value?.count ?? 0)
}

export function MobileTradingHub() {
  const phone = usePhoneLayout()
  const [active, setActive] = useState<MobilePanel>('options')
  const { wsStatus, brokerConnected, marketOpen, lastSync, brokerPositions, deployInfo } = useStore()
  const positions = positionCount(brokerPositions)
  const shortSha = String(deployInfo?.git_sha || '').slice(0, 7) || 'pending'

  useEffect(() => {
    console.info('[SYSTEM3_MOBILE_HUB]', {
      event: 'mounted',
      transport: wsStatus,
      brokerConnected,
      mode: 'PAPER',
      liveTrading: false,
    })

    const unsubscribe = useStore.subscribe((next, previous) => {
      if (next.wsStatus !== previous.wsStatus || next.lastSync !== previous.lastSync || next.brokerPositions !== previous.brokerPositions) {
        console.info('[SYSTEM3_STREAM_PROOF]', {
          transport: next.wsStatus,
          marketOpen: next.marketOpen,
          brokerConnected: next.brokerConnected,
          lastSync: next.lastSync,
          portfolioRows: positionCount(next.brokerPositions),
          liveTrading: false,
        })
      }
    })
    return unsubscribe
  }, [])

  const panel = useMemo(() => {
    switch (active) {
      case 'options': return <OptionChain />
      case 'equities': return <Signals />
      case 'predictions': return <PredictionAudit />
      case 'backtest': return <Backtest />
      case 'portfolio': return <Positions />
    }
  }, [active])

  if (!phone) {
    return (
      <main className="mobile-hub-desktop-gate">
        <Radio size={28} />
        <h1>Mobile Trading Hub</h1>
        <p>This orchestration workspace renders only at mobile widths (820px or below).</p>
        <p>Existing desktop workspaces remain unchanged.</p>
      </main>
    )
  }

  return (
    <main className="mobile-hub-shell" aria-label="System3 mobile trading hub">
      <header className="mobile-hub-header">
        <div>
          <div className="mobile-hub-eyebrow">SYSTEM3 · MOBILE COMMAND</div>
          <h1>Trading Intelligence</h1>
        </div>
        <span className="mobile-hub-sha">SHA {shortSha}</span>
      </header>

      <section className="mobile-hub-status" aria-label="Live transport and safety status">
        <span className={wsStatus === 'live' ? 'is-ok' : 'is-warn'}>WS transport {wsStatus.toUpperCase()}</span>
        <span className={brokerConnected ? 'is-ok' : 'is-warn'}>Broker {brokerConnected ? 'CONNECTED' : 'WAITING'}</span>
        <span className={marketOpen ? 'is-ok' : 'is-muted'}>Market {marketOpen ? 'OPEN' : 'CLOSED'}</span>
        <span className="is-safe">PAPER · LIVE OFF</span>
        <span className="is-muted">Portfolio rows {positions}</span>
        <span className="is-muted">Sync {lastSync === '--' ? 'pending' : new Date(lastSync).toLocaleTimeString('en-IN')}</span>
      </section>

      <nav className="mobile-hub-tabs" role="tablist" aria-label="Mobile dashboard panels">
        {PANELS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={active === id}
            className={active === id ? 'is-active' : ''}
            onClick={() => {
              setActive(id)
              console.info('[SYSTEM3_MOBILE_TAB]', { tab: id, at: new Date().toISOString() })
            }}
          >
            <Icon size={16} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <section className="mobile-hub-panel" role="tabpanel" aria-label={PANELS.find(item => item.id === active)?.label}>
        {panel}
      </section>
    </main>
  )
}

