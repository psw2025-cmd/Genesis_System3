import { useStore } from '../store'
import { fmt, fmtCr, signClass, cn } from '../lib/utils'
import { PriceCell } from './ui/PriceCell'
import { AuthUnlock } from './AuthUnlock'

function Row({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="flex items-center justify-between py-2 border-b" style={{ borderColor: 'var(--border)' }}>
      <span style={{ color: 'var(--text-mut)', fontSize: '.75rem' }}>{label}</span>
      <span className={cn('num', color)} style={{ fontSize: '.8rem', fontWeight: 600 }}>{value}</span>
    </div>
  )
}

function pickArray(obj: any, ...keys: string[]): any[] {
  if (!obj) return []
  for (const k of keys) {
    const v = obj[k]
    if (Array.isArray(v)) return v
  }
  return []
}

function brokerFailure(obj: any): { bad: boolean; message: string } {
  if (!obj) return { bad: false, message: '' }
  const raw = obj.raw ?? obj.data ?? obj.normalized?.raw ?? obj.funds?.raw ?? obj
  const remarks = raw?.remarks ?? obj?.remarks ?? {}
  const msg = remarks?.error_message ?? raw?.error_message ?? raw?.message ?? obj?.error ?? obj?.message ?? ''
  const code = remarks?.error_code ?? raw?.error_code ?? obj?.error_code ?? ''
  const typ = remarks?.error_type ?? raw?.error_type ?? obj?.error_type ?? ''
  const status = String(raw?.status ?? obj?.status ?? '').toLowerCase()
  const detail = JSON.stringify([msg, code, typ]).toLowerCase()
  const bad = obj?.success === false || obj?.blocked === true || status === 'failure' || detail.includes('invalid') || detail.includes('token') || detail.includes('unauthorized')
  return { bad, message: [code, typ, msg].filter(Boolean).join(' - ') }
}

function brokerClientId(status: any) {
  return String(status?.client_id ?? status?.clientId ?? status?.dhan_client_id ?? status?.account_id ?? 'NOT PROVIDED BY BROKER API')
}

function liveTradingState(state: any, brokerStatus: any) {
  const raw = state?.live_trading_enabled ?? state?.liveTradingEnabled ?? brokerStatus?.live_trading_enabled ?? brokerStatus?.liveTradingEnabled ?? brokerStatus?.live_allowed ?? '0'
  return String(raw) === '1' || raw === true ? 'ENABLED BY BACKEND FLAG' : 'BLOCKED BY BACKEND FLAG'
}

export function BrokerPanel() {
  const { brokerStatus, brokerFunds, brokerHoldings, brokerPositions, brokerConnected, apiStatus, marketOpen, state } = useStore()

  const funds = brokerFunds?.normalized ?? brokerFunds?.funds ?? brokerFunds ?? null
  const authBlocked = apiStatus?.status === 'API_AUTH_REQUIRED'
  const brokerBlocked = authBlocked || apiStatus?.status === 'API_ERROR'
  const fundsFailure = brokerFailure(brokerFunds)
  const statusFailure = brokerFailure(brokerStatus)
  const holdingsFailure = brokerFailure(brokerHoldings)
  const positionsFailure = brokerFailure(brokerPositions)
  const brokerApiResponded = Boolean(brokerStatus || brokerFunds || brokerHoldings || brokerPositions)
  const brokerTokenBad = fundsFailure.bad || statusFailure.bad
  const brokerTruthConnected = Boolean(brokerConnected && !brokerTokenBad && !authBlocked)
  const dataState = authBlocked ? 'AUTH REQUIRED' : brokerTokenBad ? 'BLOCKED / TOKEN ERROR' : brokerTruthConnected ? 'LIVE READ-ONLY' : brokerApiResponded ? 'API RESPONDED' : brokerBlocked ? 'API OFFLINE' : 'WAITING'
  const fundsError = Boolean(brokerFunds && (brokerFunds.success === false || brokerFunds.blocked === true || fundsFailure.bad))
  const fundsLoading = brokerFunds == null

  const holdings = pickArray(brokerHoldings, 'rows', 'holdings', 'data')
  const positions = pickArray(brokerPositions, 'rows', 'positions', 'data')

  const holdingsError = Boolean(brokerHoldings && (brokerHoldings.success === false || brokerHoldings.blocked === true || holdingsFailure.bad))
  const positionsError = Boolean(brokerPositions && (brokerPositions.success === false || brokerPositions.blocked === true || positionsFailure.bad))

  const availBal = funds?.available_balance ?? funds?.availableBalance ?? null
  const usedMargin = funds?.utilized_amount ?? funds?.utilizedAmount ?? null
  const totalBal = funds?.total_limit ?? funds?.total_balance ?? funds?.totalBalance ?? null

  const getAvg = (h: any) => h.avg_price ?? h.average_price ?? 0
  const getEntry = (p: any) => p.avg_price ?? p.buy_avg ?? p.entry_price ?? 0

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      {authBlocked && <AuthUnlock />}

      <div className="card p-4">
        <h3 style={{ fontSize: '.8rem', fontWeight: 700, color: 'var(--text-pri)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '.05em' }}>
          Broker Connection - Dhan
        </h3>
        <Row label="Status" value={brokerTruthConnected ? 'CONNECTED' : dataState} color={brokerTruthConnected ? 'tx-up' : brokerApiResponded && !brokerTokenBad ? 'tx-amber' : 'tx-down'} />
        <Row label="Truth" value={brokerTokenBad ? 'BROKER AUTH BLOCKED - NOT READY' : brokerTruthConnected ? 'READ-ONLY BROKER PROOF OK' : 'BROKER PROOF NOT READY'} color={brokerTokenBad ? 'tx-down' : brokerTruthConnected ? 'tx-up' : 'tx-amber'} />
        <Row label="Mode" value="READ-ONLY BROKER PROOF" />
        <Row label="Client ID" value={brokerClientId(brokerStatus)} color={brokerClientId(brokerStatus).startsWith('NOT PROVIDED') ? 'tx-down' : undefined} />
        <Row label="Token Status" value={brokerTokenBad ? 'ERROR / INVALID OR EXPIRED' : brokerStatus?.token_status ?? brokerStatus?.tokenStatus ?? (brokerTruthConnected ? 'VALID' : 'UNKNOWN')} color={brokerTokenBad ? 'tx-down' : brokerTruthConnected ? 'tx-up' : 'tx-down'} />
        <Row label="Holdings API" value={holdingsError ? 'ERROR/BLOCKED' : holdings.length >= 0 && brokerHoldings ? 'RESPONDED' : authBlocked ? 'AUTH REQUIRED' : 'CHECKING'} color={holdingsError || authBlocked ? 'tx-down' : brokerHoldings ? 'tx-up' : undefined} />
        <Row label="Funds API" value={fundsError ? 'ERROR/BLOCKED' : funds ? 'RESPONDED' : authBlocked ? 'AUTH REQUIRED' : 'CHECKING'} color={fundsError || authBlocked ? 'tx-down' : funds ? 'tx-up' : undefined} />
        <Row label="Broker Blocker" value={brokerTokenBad ? (fundsFailure.message || statusFailure.message || 'BROKER API AUTH ERROR') : marketOpen ? 'NONE' : 'NONE - MARKET CLOSED IS OK'} color={brokerTokenBad ? 'tx-down' : 'tx-up'} />
        <Row label="Market State" value={marketOpen ? 'MARKET OPEN' : 'MARKET CLOSED / READ-ONLY OK'} />
        <Row label="Data Visibility" value={authBlocked ? 'LOCKED UNTIL API KEY IS CONFIGURED' : brokerTokenBad ? 'BLOCKED UNTIL DHAN TOKEN / CLIENT AUTH IS VALID' : 'VISIBLE ONLY WHEN LIVE READ-ONLY BROKER API RESPONDS'} color={authBlocked || brokerTokenBad ? 'tx-down' : undefined} />
        <Row label="Live Trading" value={liveTradingState(state, brokerStatus)} color="tx-down" />
      </div>

      <div className="card p-4">
        <h3 style={{ fontSize: '.8rem', fontWeight: 700, color: 'var(--text-pri)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '.05em' }}>
          Account Funds
        </h3>
        {fundsError ? (
          <div style={{ color: 'var(--down)', fontSize: '.8rem', lineHeight: 1.6 }}>
            <div>Failed to load funds: {fundsFailure.message || brokerFunds?.error || 'unknown error'}</div>
            <div>Market close is not the blocker. Check Dhan token/API response.</div>
          </div>
        ) : fundsLoading ? (
          <p style={{ color: 'var(--text-mut)', fontSize: '.8rem' }}>Checking live broker funds API...</p>
        ) : availBal == null ? (
          <div style={{ color: 'var(--text-mut)', fontSize: '.8rem', lineHeight: 1.6 }}>
            <div>{authBlocked ? 'Funds hidden: backend requires X-API-Key.' : brokerBlocked ? 'Funds unavailable: backend API did not respond.' : 'Funds API responded but no balance field found in response'}</div>
            <div>Read-only funds must come from current Dhan broker API response. No cached/hardcoded balance is displayed.</div>
          </div>
        ) : (
          <>
            <Row label="Available Balance" value={fmtCr(availBal)} color="tx-up" />
            <Row label="Used Margin" value={fmtCr(usedMargin)} color={(usedMargin ?? 0) > 0 ? 'tx-down' : undefined} />
            <Row label="Total Balance" value={fmtCr(totalBal)} />
          </>
        )}
      </div>

      <div className="card" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '8px 16px', borderBottom: '1px solid var(--border)', background: 'var(--surface-2)' }}>
          <h3 style={{ fontSize: '.75rem', fontWeight: 700, color: 'var(--text-pri)', textTransform: 'uppercase', letterSpacing: '.05em' }}>
            Equity Holdings ({holdings.length})
          </h3>
        </div>
        {holdingsError ? (
          <p style={{ padding: '20px', color: 'var(--down)', fontSize: '.8rem' }}>Failed to load holdings: {holdingsFailure.message || brokerHoldings?.error || 'unknown error'}</p>
        ) : !brokerHoldings ? (
          <p style={{ padding: '20px', color: 'var(--text-mut)', fontSize: '.8rem' }}>Checking live broker holdings API...</p>
        ) : holdings.length === 0 ? (
          <p style={{ padding: '20px', color: 'var(--text-mut)', fontSize: '.8rem' }}>
            {authBlocked ? 'Holdings hidden: backend requires X-API-Key.' : brokerBlocked ? 'Holdings unavailable: backend API did not respond.' : brokerTruthConnected ? 'No equity holdings found in Dhan broker response' : 'No valid broker holdings truth available.'}
          </p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>{['Symbol', 'Qty', 'Avg Cost', 'LTP', 'P&L', 'P&L%'].map(h => <th key={h} className="thead" style={{ textAlign: h === 'Symbol' ? 'left' : 'right' }}>{h}</th>)}</tr>
            </thead>
            <tbody>
              {holdings.slice(0, 15).map((h: any, i: number) => {
                const avg = getAvg(h)
                const ltp = h.ltp ?? 0
                const qty = h.quantity ?? 0
                const pnl = h.pnl ?? ((ltp - avg) * qty)
                const pnlPct = h.pnl_pct ?? (avg > 0 ? ((ltp - avg) / avg) * 100 : 0)
                return (
                  <tr key={i} className="trow">
                    <td className="tcell" style={{ fontWeight: 600 }}>{h.trading_symbol ?? h.symbol ?? '--'}</td>
                    <td className="tcell" style={{ textAlign: 'right' }}>{qty || '--'}</td>
                    <td className="tcell" style={{ textAlign: 'right' }}>{fmt(avg)}</td>
                    <td className="tcell" style={{ textAlign: 'right' }}><PriceCell value={ltp} /></td>
                    <td className={cn('tcell', signClass(pnl))} style={{ textAlign: 'right', fontWeight: 600 }}>{fmtCr(pnl)}</td>
                    <td className={cn('tcell', signClass(pnlPct))} style={{ textAlign: 'right' }}>{pnlPct >= 0 ? '+' : ''}{(pnlPct ?? 0).toFixed(2)}%</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      <div className="card" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '8px 16px', borderBottom: '1px solid var(--border)', background: 'var(--surface-2)' }}>
          <h3 style={{ fontSize: '.75rem', fontWeight: 700, color: 'var(--text-pri)', textTransform: 'uppercase', letterSpacing: '.05em' }}>
            Dhan Live Positions ({positions.length})
          </h3>
        </div>
        {positionsError ? (
          <p style={{ padding: '20px', color: 'var(--down)', fontSize: '.8rem' }}>Failed to load positions: {positionsFailure.message || brokerPositions?.error || 'unknown error'}</p>
        ) : !brokerPositions ? (
          <p style={{ padding: '20px', color: 'var(--text-mut)', fontSize: '.8rem' }}>Checking live broker positions API...</p>
        ) : positions.length === 0 ? (
          <p style={{ padding: '20px', color: 'var(--text-mut)', fontSize: '.8rem' }}>
            {authBlocked ? 'Positions hidden: backend requires X-API-Key.' : brokerBlocked ? 'Positions unavailable: backend API did not respond.' : brokerTruthConnected ? 'No open positions in Dhan account read-only response' : 'No valid broker positions truth available.'}
          </p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>{['Symbol', 'Side', 'Qty', 'Entry', 'LTP', 'P&L'].map(h => <th key={h} className="thead">{h}</th>)}</tr>
            </thead>
            <tbody>
              {positions.map((p: any, i: number) => (
                <tr key={i} className="trow">
                  <td className="tcell" style={{ fontWeight: 600 }}>{p.trading_symbol ?? p.symbol ?? '--'}</td>
                  <td className="tcell"><span className={cn('pill text-xs', p.position_type === 'LONG' ? 'tx-up' : 'tx-down')} style={{ fontSize: '.6rem' }}>{p.position_type ?? p.side ?? '--'}</span></td>
                  <td className="tcell">{p.net_qty ?? p.quantity ?? '--'}</td>
                  <td className="tcell">{fmt(getEntry(p))}</td>
                  <td className="tcell"><PriceCell value={p.ltp ?? 0} /></td>
                  <td className={cn('tcell', signClass(p.unrealized_pnl ?? p.pnl ?? 0))} style={{ fontWeight: 600 }}>{fmtCr(p.unrealized_pnl ?? p.pnl ?? 0)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
