import { useStore } from '../store'
import { BrokerPanel } from './BrokerPanel'

function ProofItem({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return (
    <div className="card p-3" style={{ minWidth: 0 }}>
      <div style={{ color: 'var(--text-mut)', fontSize: '.65rem', letterSpacing: '.06em', fontWeight: 700 }}>{label}</div>
      <div
        className="num"
        style={{
          marginTop: '6px',
          fontSize: '.78rem',
          fontWeight: 700,
          color: ok ? 'var(--up)' : 'var(--down)',
          overflowWrap: 'anywhere',
        }}
      >
        {value}
      </div>
    </div>
  )
}

function fmtTime(value: any) {
  if (!value) return 'PENDING PROOF'
  const d = new Date(value)
  return Number.isNaN(d.getTime())
    ? String(value)
    : d.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })
}

function responded(obj: any) {
  return Boolean(obj && obj.pendingProof !== true && obj.error == null && obj.success !== false)
}

export function BrokerProofPanel() {
  const {
    brokerStatus,
    brokerConnected,
    brokerFunds,
    brokerHoldings,
    brokerPositions,
    chain,
    state,
  } = useStore()

  const proof = brokerStatus?.token_proof || {}
  const reload = brokerStatus?.token_reload || {}
  const required = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']
  const readyChains = required.filter((sym) => {
    const row = chain?.[sym]
    return Number(row?.total_contracts || row?.contracts?.length || 0) > 0 && Number(row?.spot || 0) > 0
  }).length

  const hours = proof?.hours_remaining
  const tokenHealthy = proof?.expired === false && (hours == null || Number(hours) > 0)
  const sourceOk = proof?.source === 'GCP_SECRET_MANAGER_DYNAMIC'
  const liveOff = !Boolean(
    state?.live_trading_enabled
    || state?.liveTradingEnabled
    || brokerStatus?.live_trading_enabled
    || brokerStatus?.order_placement_allowed,
  )

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <div style={{ padding: '16px 24px 0', flexShrink: 0 }}>
        <div className="card p-4">
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap' }}>
            <div>
              <div style={{ color: 'var(--text-pri)', fontSize: '.85rem', fontWeight: 800, letterSpacing: '.05em' }}>
                DHAN TOKEN ROTATION PROOF
              </div>
              <div style={{ color: 'var(--text-mut)', fontSize: '.7rem', marginTop: '4px' }}>
                Google Cloud only · no raw token values · analyzer/read-only safety
              </div>
            </div>
            <div style={{ color: brokerConnected ? 'var(--up)' : 'var(--down)', fontWeight: 800, fontSize: '.8rem' }}>
              {brokerConnected ? 'BROKER CONNECTED' : `BROKER PENDING: ${brokerStatus?.error || 'PENDING PROOF'}`}
            </div>
          </div>

          <div
            style={{
              marginTop: '14px',
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
              gap: '8px',
            }}
          >
            <ProofItem label="BROKER PROFILE" value={brokerConnected ? `PASS · ${brokerStatus?.latency_ms ?? '-'} ms` : String(brokerStatus?.error || 'PENDING')} ok={brokerConnected} />
            <ProofItem label="TOKEN SOURCE" value={proof?.source || 'PENDING PROOF'} ok={sourceOk} />
            <ProofItem label="SECRET VERSION" value={proof?.secret_version ? `VERSION ${proof.secret_version}` : 'PENDING PROOF'} ok={Boolean(proof?.secret_version)} />
            <ProofItem label="TOKEN LOADED (IST)" value={fmtTime(proof?.loaded_at_utc)} ok={Boolean(proof?.loaded_at_utc)} />
            <ProofItem label="TOKEN EXPIRY (IST)" value={fmtTime(proof?.expires_at_utc)} ok={tokenHealthy} />
            <ProofItem label="TOKEN TIME LEFT" value={hours == null ? 'PENDING PROOF' : `${Number(hours).toFixed(2)} HOURS`} ok={tokenHealthy} />
            <ProofItem label="LAST RELOAD REASON" value={String(proof?.last_reload_reason || 'NOT YET RELOADED')} ok={!proof?.last_error_type} />
            <ProofItem label="AUTH-PENDING RETRY" value={reload?.attempted ? (reload?.success ? 'RELOADED + RETRIED' : 'RELOAD PENDINGED') : 'NOT REQUIRED'} ok={!reload?.attempted || Boolean(reload?.success)} />
            <ProofItem label="ROTATION JOB" value={`${proof?.rotation_job || 'genesis-system3-dhan-token-rotate'} · ${proof?.rotation_schedule || '07:30 IST daily'}`} ok={Boolean(proof?.rotation_job || sourceOk)} />
            <ProofItem label="FUNDS / HOLDINGS / POSITIONS" value={`${responded(brokerFunds) ? 'F' : '-'} / ${responded(brokerHoldings) ? 'H' : '-'} / ${responded(brokerPositions) ? 'P' : '-'}`} ok={responded(brokerFunds) && responded(brokerHoldings) && responded(brokerPositions)} />
            <ProofItem label="REQUIRED DHAN CHAINS" value={`${readyChains}/4 READY`} ok={readyChains === 4} />
            <ProofItem label="LIVE-MONEY SAFETY" value={liveOff ? 'ANALYZER · LIVE OFF · ORDERS DISABLED' : 'LIVE FLAG DETECTED'} ok={liveOff} />
          </div>

          <div style={{ marginTop: '10px', color: 'var(--text-mut)', fontSize: '.68rem' }}>
            Raw token exposed: NO · Secret ID: {proof?.secret_id || 'not shown until dynamic provider loads'} · Cache age: {proof?.cache_age_s ?? '-'}s · Reload count: {proof?.reload_count ?? 0}
          </div>
        </div>
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>
        <BrokerPanel />
      </div>
    </div>
  )
}
