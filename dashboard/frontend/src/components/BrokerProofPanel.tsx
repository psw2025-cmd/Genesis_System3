import { Activity, Database, Shield, Wallet } from 'lucide-react'
import { useStore } from '../store'
import { BrokerPanel } from './BrokerPanel'

function fmtTime(value: any) {
  if (!value) return 'PENDING PROOF'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })
}

function responded(obj: any) {
  return Boolean(obj && obj.pendingProof !== true && obj.error == null && obj.success !== false)
}

function ProofMetric({ label, value, ok, icon }: { label: string; value: string; ok: boolean; icon?: React.ReactNode }) {
  return (
    <div className="metric-card" style={{ minWidth: 0 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
        <div className="metric-label">{label}</div>
        <div style={{ color: ok ? 'var(--up)' : 'var(--amber)' }}>{icon}</div>
      </div>
      <div className="num" style={{ marginTop: 7, color: ok ? 'var(--up)' : 'var(--amber)', fontSize: '.66rem', fontWeight: 800, overflowWrap: 'anywhere' }}>{value}</div>
    </div>
  )
}

export function BrokerProofPanel() {
  const { brokerStatus, brokerConnected, brokerFunds, brokerHoldings, brokerPositions, chain, state } = useStore()
  const proof = brokerStatus?.token_proof || {}
  const reload = brokerStatus?.token_reload || {}
  const required = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']
  const readyChains = required.filter((symbol) => {
    const row = chain?.[symbol]
    return Number(row?.total_contracts || row?.contracts?.length || 0) > 0 && Number(row?.spot || 0) > 0
  }).length
  const hours = proof?.hours_remaining
  const tokenHealthy = proof?.expired === false && (hours == null || Number(hours) > 0)
  const sourceOk = proof?.source === 'GCP_SECRET_MANAGER_DYNAMIC'
  const liveOff = !Boolean(state?.live_trading_enabled || state?.liveTradingEnabled || brokerStatus?.live_trading_enabled || brokerStatus?.order_placement_allowed)

  return (
    <div className="workspace-shell" style={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <div className="card" style={{ padding: 12, flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 14, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 34, height: 34, display: 'grid', placeItems: 'center', borderRadius: 9, color: 'var(--accent)', background: 'rgba(59,140,255,.10)', border: '1px solid rgba(59,140,255,.28)' }}><Database size={17} /></div>
            <div>
              <div className="workspace-title" style={{ fontSize: '.92rem' }}>Broker Connection · DHAN</div>
              <div style={{ marginTop: 3, color: 'var(--text-mut)', fontSize: '.59rem' }}>Read-only account proof · Google Cloud token authority · Raw token exposed: NO</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
            <span className="pill" style={{ color: brokerConnected ? 'var(--up)' : 'var(--amber)', border: `1px solid ${brokerConnected ? 'rgba(24,215,130,.26)' : 'rgba(245,165,36,.26)'}`, background: brokerConnected ? 'rgba(24,215,130,.06)' : 'rgba(245,165,36,.06)' }}>
              <span className="status-dot" style={{ color: brokerConnected ? 'var(--up)' : 'var(--amber)' }} />
              {brokerConnected ? 'CONNECTED' : 'PENDING PROOF'}
            </span>
            <span className="pill" style={{ color: liveOff ? 'var(--up)' : 'var(--down)', border: `1px solid ${liveOff ? 'rgba(24,215,130,.22)' : 'rgba(255,73,100,.24)'}`, background: liveOff ? 'rgba(24,215,130,.05)' : 'rgba(255,73,100,.06)' }}>
              <Shield size={11} /> {liveOff ? 'READ-ONLY / LIVE OFF' : 'LIVE FLAG REVIEW'}
            </span>
          </div>
        </div>

        <div className="workspace-grid" style={{ gridTemplateColumns: 'repeat(6, minmax(0, 1fr))', marginTop: 10 }}>
          <ProofMetric label="API / Broker" value={brokerConnected ? `CONNECTED · ${brokerStatus?.latency_ms ?? '-'}ms` : String(brokerStatus?.error || 'WAITING')} ok={brokerConnected} icon={<Activity size={13} />} />
          <ProofMetric label="Token Source" value={proof?.source || 'PENDING'} ok={sourceOk} icon={<Shield size={13} />} />
          <ProofMetric label="Secret Version" value={proof?.secret_version ? `VERSION ${proof.secret_version}` : 'PENDING'} ok={Boolean(proof?.secret_version)} icon={<Database size={13} />} />
          <ProofMetric label="Token Loaded" value={fmtTime(proof?.loaded_at_utc)} ok={Boolean(proof?.loaded_at_utc)} icon={<Activity size={13} />} />
          <ProofMetric label="Token Time Left" value={hours == null ? 'PENDING' : `${Number(hours).toFixed(2)} HOURS`} ok={tokenHealthy} icon={<Activity size={13} />} />
          <ProofMetric label="Account APIs" value={`${responded(brokerFunds) ? 'F' : '-'} / ${responded(brokerHoldings) ? 'H' : '-'} / ${responded(brokerPositions) ? 'P' : '-'}`} ok={responded(brokerFunds) && responded(brokerHoldings) && responded(brokerPositions)} icon={<Wallet size={13} />} />
        </div>

        <div className="workspace-grid" style={{ gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', marginTop: 8 }}>
          <ProofMetric label="Required Chains" value={`${readyChains}/4 READY`} ok={readyChains === 4} icon={<Database size={13} />} />
          <ProofMetric label="Reload State" value={reload?.attempted ? (reload?.success ? 'RELOADED + RETRIED' : 'RELOAD PENDING') : 'NOT REQUIRED'} ok={!reload?.attempted || Boolean(reload?.success)} icon={<Activity size={13} />} />
          <ProofMetric label="Expiry" value={fmtTime(proof?.expires_at_utc)} ok={tokenHealthy} icon={<Shield size={13} />} />
          <ProofMetric label="Authority" value={liveOff ? 'ANALYZER · ORDERS DISABLED' : 'REVIEW REQUIRED'} ok={liveOff} icon={<Shield size={13} />} />
        </div>
      </div>

      <div style={{ flex: 1, minHeight: 0, marginTop: 9 }}>
        <BrokerPanel />
      </div>
    </div>
  )
}
