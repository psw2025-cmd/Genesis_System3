import { useStore } from '../store'
import { fmt, fmtCr, signClass, cn } from '../lib/utils'
import { PriceCell } from './ui/PriceCell'

function Row({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="flex items-center justify-between py-2 border-b" style={{ borderColor: 'var(--border)' }}>
      <span style={{ color: 'var(--text-mut)', fontSize: '.75rem' }}>{label}</span>
      <span className={cn('num', color)} style={{ fontSize: '.8rem', fontWeight: 600 }}>{value}</span>
    </div>
  )
}

export function BrokerPanel() {
  const { brokerStatus, brokerFunds, brokerHoldings, brokerPositions, brokerConnected } = useStore()

  const funds     = brokerFunds?.funds ?? brokerFunds
  const holdings  = brokerHoldings?.holdings ?? brokerHoldings?.data ?? []
  const positions = brokerPositions?.positions ?? brokerPositions?.data ?? []

  const availBal   = funds?.available_balance ?? funds?.availableBalance ?? null
  const usedMargin = funds?.utilized_amount   ?? funds?.utilizedAmount    ?? null
  const totalBal   = funds?.total_balance     ?? funds?.totalBalance       ?? null

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">

      {/* Connection Status */}
      <div className="card p-4">
        <h3 style={{ fontSize: '.8rem', fontWeight: 700, color: 'var(--text-pri)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '.05em' }}>
          🔗 Broker Connection — Dhan
        </h3>
        <Row label="Status"       value={brokerConnected ? 'CONNECTED' : 'OFFLINE'}
             color={brokerConnected ? 'tx-up' : 'tx-down'} />
        <Row label="Mode"         value="READ-ONLY (Analyzer)" />
        <Row label="Client ID"    value={brokerStatus?.client_id ?? '...3741'} />
        <Row label="Token Status" value={brokerStatus?.token_status ?? 'VALID'} color="tx-up" />
        <Row label="Holdings API" value={brokerStatus?.holdings_valid ? 'VALID ✓' : 'CHECKING...'}
             color={brokerStatus?.holdings_valid ? 'tx-up' : undefined} />
        <Row label="Funds API"    value={brokerStatus?.funds_valid ? 'VALID ✓' : 'CHECKING...'}
             color={brokerStatus?.funds_valid ? 'tx-up' : undefined} />
        <Row label="Live Trading" value="DISABLED (hardcoded 0)" color="tx-down" />
      </div>

      {/* Funds — works market closed */}
      <div className="card p-4">
        <h3 style={{ fontSize: '.8rem', fontWeight: 700, color: 'var(--text-pri)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '.05em' }}>
          💰 Account Funds
        </h3>
        {availBal == null ? (
          <p style={{ color: 'var(--text-mut)', fontSize: '.8rem' }}>Loading funds data…</p>
        ) : (
          <>
            <Row label="Available Balance" value={fmtCr(availBal)}  color="tx-up" />
            <Row label="Used Margin"       value={fmtCr(usedMargin)} color={usedMargin > 0 ? 'tx-down' : undefined} />
            <Row label="Total Balance"     value={fmtCr(totalBal)} />
          </>
        )}
      </div>

      {/* Holdings — works market closed */}
      <div className="card" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '8px 16px', borderBottom: '1px solid var(--border)', background: 'var(--surface-2)' }}>
          <h3 style={{ fontSize: '.75rem', fontWeight: 700, color: 'var(--text-pri)', textTransform: 'uppercase', letterSpacing: '.05em' }}>
            📊 Equity Holdings ({Array.isArray(holdings) ? holdings.length : 0})
          </h3>
        </div>
        {!Array.isArray(holdings) || holdings.length === 0 ? (
          <p style={{ padding: '20px', color: 'var(--text-mut)', fontSize: '.8rem' }}>
            {brokerConnected ? 'No equity holdings found' : 'Waiting for broker connection…'}
          </p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                {['Symbol', 'Qty', 'Avg Cost', 'LTP', 'P&L', 'P&L%'].map(h => (
                  <th key={h} className="thead" style={{ textAlign: h === 'Symbol' ? 'left' : 'right' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {holdings.slice(0, 15).map((h: any, i: number) => {
                const pnl = (h.ltp - h.average_price) * h.quantity
                const pnlPct = h.average_price > 0 ? ((h.ltp - h.average_price) / h.average_price) * 100 : 0
                return (
                  <tr key={i} className="trow">
                    <td className="tcell" style={{ fontWeight: 600 }}>{h.trading_symbol ?? h.symbol ?? '--'}</td>
                    <td className="tcell" style={{ textAlign: 'right' }}>{h.quantity ?? '--'}</td>
                    <td className="tcell" style={{ textAlign: 'right' }}>{fmt(h.average_price)}</td>
                    <td className="tcell" style={{ textAlign: 'right' }}>
                      <PriceCell value={h.ltp} />
                    </td>
                    <td className={cn('tcell', signClass(pnl))} style={{ textAlign: 'right', fontWeight: 600 }}>
                      {fmtCr(pnl)}
                    </td>
                    <td className={cn('tcell', signClass(pnlPct))} style={{ textAlign: 'right' }}>
                      {pnlPct >= 0 ? '+' : ''}{pnlPct.toFixed(2)}%
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Live Positions — Dhan actual (not paper) */}
      <div className="card" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '8px 16px', borderBottom: '1px solid var(--border)', background: 'var(--surface-2)' }}>
          <h3 style={{ fontSize: '.75rem', fontWeight: 700, color: 'var(--text-pri)', textTransform: 'uppercase', letterSpacing: '.05em' }}>
            📋 Dhan Live Positions ({Array.isArray(positions) ? positions.length : 0})
          </h3>
        </div>
        {!Array.isArray(positions) || positions.length === 0 ? (
          <p style={{ padding: '20px', color: 'var(--text-mut)', fontSize: '.8rem' }}>
            No open positions in Dhan account (read-only view)
          </p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                {['Symbol', 'Side', 'Qty', 'Entry', 'LTP', 'P&L'].map(h => (
                  <th key={h} className="thead">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {positions.map((p: any, i: number) => (
                <tr key={i} className="trow">
                  <td className="tcell" style={{ fontWeight: 600 }}>{p.trading_symbol ?? p.symbol ?? '--'}</td>
                  <td className="tcell">
                    <span className={cn('pill text-xs', p.position_type === 'LONG' ? 'tx-up' : 'tx-down')}
                          style={{ fontSize: '.6rem' }}>
                      {p.position_type ?? p.side ?? '--'}
                    </span>
                  </td>
                  <td className="tcell">{p.net_qty ?? p.quantity ?? '--'}</td>
                  <td className="tcell">{fmt(p.buy_avg ?? p.entry_price)}</td>
                  <td className="tcell"><PriceCell value={p.ltp} /></td>
                  <td className={cn('tcell', signClass(p.unrealized_pnl ?? p.pnl))} style={{ fontWeight: 600 }}>
                    {fmtCr(p.unrealized_pnl ?? p.pnl)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
