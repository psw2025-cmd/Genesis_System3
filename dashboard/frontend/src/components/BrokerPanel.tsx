import { useStore } from '../store'
import { fmt, fmtCr, signClass, cn } from '../lib/utils'
import { PriceCell } from './ui/PriceCell'
import { AuthUnlock } from './AuthUnlock'
import { isNonAuthBrokerRejection } from '../lib/healthTruth'

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
  const detail = JSON.stringify([msg, code, typ, obj?.error]).toLowerCase()
  // Rate-limit / transient transport failures must NOT be painted as token expiry.
  if (detail.includes('rate_limit') || code === 429 || status === 'rate_limit') {
    return { bad: false, message: 'rate_limited_transient' }
  }
  const bad = obj?.success === false || obj?.pendingProof === true || status === 'failure' || detail.includes('invalid') || detail.includes('token') || detail.includes('unauthorized') || detail.includes('dh-901')
  return { bad, message: [code, typ, msg].filter(Boolean).join(' - ') }
}

function brokerClientId(status: any, funds?: any) {
  const fromStatus = status?.client_id ?? status?.clientId ?? status?.dhan_client_id ?? status?.dhanClientId ?? status?.account_id
  const raw = funds?.normalized?.raw ?? funds?.raw ?? funds?.data ?? funds
  const fromFunds = raw?.dhanClientId ?? raw?.dhan_client_id ?? raw?.clientId
  const val = fromStatus ?? fromFunds
  return String(val || 'NOT PROVIDED BY BROKER API')
}

function liveTradingState(state: any, brokerStatus: any) {
  const raw = state?.live_trading_enabled ?? state?.liveTradingEnabled ?? brokerStatus?.live_trading_enabled ?? brokerStatus?.liveTradingEnabled ?? brokerStatus?.live_allowed ?? '0'
  return String(raw) === '1' || raw === true ? 'ENABLED BY BACKEND FLAG' : 'DISABLED BY BACKEND FLAG'
}

export function BrokerPanel() {
  const { brokerStatus, brokerFunds, brokerHoldings, brokerPositions, brokerConnected, apiStatus, marketOpen, state, liveBoard } = useStore()

  const funds = brokerFunds?.normalized ?? brokerFunds?.funds ?? brokerFunds ?? null
  const authNeeded = apiStatus?.status === 'API_AUTH_REQUIRED'
  const brokerApiIssue = authNeeded || apiStatus?.status === 'API_ERROR'
  const fundsFailure = brokerFailure(brokerFunds)
  const statusFailure = brokerFailure(brokerStatus)
  const holdingsFailure = brokerFailure(brokerHoldings)
  const positionsFailure = brokerFailure(brokerPositions)
  const brokerApiResponded = Boolean(brokerStatus || brokerFunds || brokerHoldings || brokerPositions)
  const brokerTruthConnected = Boolean(brokerConnected === true || brokerStatus?.connected === true)
  const requestRejected = isNonAuthBrokerRejection(brokerStatus)
  // Do not paint TOKEN ERROR when broker truth is already connected (rate-limit false fails).
  // DH-906/805/810 are non-auth upstream rejections and must not look like token expiry.
  const brokerTokenBad = (!brokerTruthConnected) && !requestRejected && (fundsFailure.bad || statusFailure.bad)
  const dataState = authNeeded
    ? 'AUTH_NEEDED'
    : requestRejected
      ? 'REQUEST REJECTED (NON-AUTH)'
      : brokerTokenBad
        ? 'AUTH OR TOKEN ISSUE'
        : brokerTruthConnected
          ? 'SESSION OK / RELIABILITY NOT IMPLIED'
          : brokerApiResponded
            ? 'API RESPONDED'
            : brokerApiIssue
              ? 'API OFFLINE'
              : 'WAITING'
  const fundsError = Boolean(
    brokerFunds
    && (
      brokerFunds.pendingProof === true
      || fundsFailure.bad
      || (
        brokerFunds.success === false
        && Boolean(brokerFunds.error || brokerFunds.message)
      )
    )
  )
  const fundsLoading = brokerFunds == null

  const holdings = pickArray(brokerHoldings, 'rows', 'holdings', 'data')
  const positions = pickArray(brokerPositions, 'rows', 'positions', 'data')
  const portfolio = liveBoard?.portfolio
  const investment = Number(portfolio?.investment)
    || holdings.reduce((s: number, h: any) => s + (Number(h.avg_price || h.avgCostPrice || 0) * Number(h.quantity || h.totalQty || 0)), 0)
  const currentValue = Number(portfolio?.current_value)
    || holdings.reduce((s: number, h: any) => s + (Number(h.ltp || h.lastTradedPrice || 0) * Number(h.quantity || h.totalQty || 0)), 0)
  const overallPnl = portfolio?.overall_pnl != null ? Number(portfolio.overall_pnl) : (currentValue - investment)
  const overallPnlPct = portfolio?.overall_pnl_pct != null
    ? Number(portfolio.overall_pnl_pct)
    : (investment > 0 ? (overallPnl / investment) * 100 : null)

  const holdingsError = Boolean(
    brokerHoldings
    && (
      brokerHoldings.pendingProof === true
      || holdingsFailure.bad
      || (
        brokerHoldings.success === false
        && Boolean(brokerHoldings.error || brokerHoldings.message)
      )
    )
  )
  const positionsError = Boolean(
    brokerPositions
    && (
      brokerPositions.pendingProof === true
      || positionsFailure.bad
      || (
        brokerPositions.success === false
        && Boolean(brokerPositions.error || brokerPositions.message)
      )
    )
  )

  const availBal = funds?.available_balance ?? funds?.availableBalance ?? null
  const usedMargin = funds?.utilized_amount ?? funds?.utilizedAmount ?? null
  const totalBal = funds?.total_limit ?? funds?.total_balance ?? funds?.totalBalance ?? null

  const getAvg = (h: any) => h.avg_price ?? h.average_price ?? h.avgCostPrice ?? 0
  const getEntry = (p: any) => p.avg_price ?? p.buy_avg ?? p.buyAvg ?? p.entry_price ?? 0

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      {authNeeded && <AuthUnlock />}

      <div className="card p-4">
        <h3 style={{ fontSize: '.8rem', fontWeight: 700, color: 'var(--text-pri)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '.05em' }}>
          Broker Connection - Dhan
        </h3>
        <Row label="Status" value={requestRejected ? dataState : brokerTruthConnected ? 'SESSION OK' : dataState} color={brokerTruthConnected ? 'tx-up' : requestRejected || (brokerApiResponded && !brokerTokenBad) ? 'tx-amber' : 'tx-down'} />
        <Row label="Truth" value={brokerTokenBad ? 'BROKER AUTH_NEEDED - NOT READY' : requestRejected ? 'DH-906/RATE/CONFIG REJECTION - NOT TOKEN EXPIRY' : brokerTruthConnected ? 'SESSION CONNECTED - RELIABILITY NOT PROVEN' : 'BROKER PROOF NOT READY'} color={brokerTokenBad ? 'tx-down' : brokerTruthConnected ? 'tx-up' : 'tx-amber'} />
        <Row label="Mode" value="READ-ONLY BROKER PROOF" />
        <Row label="Client ID" value={brokerClientId(brokerStatus, brokerFunds)} color={brokerClientId(brokerStatus, brokerFunds).startsWith('NOT PROVIDED') ? 'tx-down' : undefined} />
        <Row label="Token Status" value={requestRejected ? 'JWT PRESENT - UPSTREAM NON-AUTH REJECTION' : brokerTokenBad ? 'ERROR / INVALID OR EXPIRED' : brokerStatus?.token_status ?? brokerStatus?.tokenStatus ?? (brokerTruthConnected ? 'VALID' : 'UNKNOWN')} color={brokerTokenBad ? 'tx-down' : requestRejected ? 'tx-amber' : brokerTruthConnected ? 'tx-up' : 'tx-down'} />
        <Row label="Holdings API" value={holdingsError ? 'ERROR/AUTH_NEEDED' : holdings.length >= 0 && brokerHoldings ? 'RESPONDED' : authNeeded ? 'AUTH_NEEDED' : 'CHECKING'} color={holdingsError || authNeeded ? 'tx-down' : brokerHoldings ? 'tx-up' : undefined} />
        <Row label="Funds API" value={fundsError ? 'ERROR/AUTH_NEEDED' : funds ? 'RESPONDED' : authNeeded ? 'AUTH_NEEDED' : 'CHECKING'} color={fundsError || authNeeded ? 'tx-down' : funds ? 'tx-up' : undefined} />
        <Row label="Broker Blocker" value={requestRejected ? String(brokerStatus?.error || 'DHAN_REQUEST_REJECTED_906') : brokerTokenBad ? (fundsFailure.message || statusFailure.message || 'BROKER API AUTH ERROR') : marketOpen ? 'NONE' : 'NONE - MARKET CLOSED IS OK'} color={requestRejected || brokerTokenBad ? 'tx-amber' : 'tx-up'} />
        <Row label="Market State" value={marketOpen ? 'MARKET OPEN' : 'MARKET CLOSED / READ-ONLY OK'} />
        <Row label="Data Visibility" value={authNeeded ? 'VISIBLE AFTER API KEY IS CONFIGURED' : brokerTokenBad ? 'VISIBLE AFTER DHAN TOKEN / CLIENT AUTH IS VALID' : requestRejected ? 'PROFILE REJECTED - DO NOT ROTATE TOKEN FOR 906' : 'VISIBLE ONLY WHEN LIVE READ-ONLY BROKER API RESPONDS'} color={authNeeded || brokerTokenBad || requestRejected ? 'tx-down' : undefined} />
        <Row label="Live Trading" value={liveTradingState(state, brokerStatus)} color="tx-down" />
      </div>

      <div className="card p-4">
        <h3 style={{ fontSize: '.8rem', fontWeight: 700, color: 'var(--text-pri)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '.05em' }}>
          Portfolio Value (Dhan live)
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 10, marginBottom: 8 }}>
          <div>
            <div style={{ fontSize: 10, color: 'var(--text-mut)' }}>Investment</div>
            <div className="num" style={{ fontWeight: 700 }}>{fmtCr(investment)}</div>
          </div>
          <div>
            <div style={{ fontSize: 10, color: 'var(--text-mut)' }}>Current Value</div>
            <div className="num" style={{ fontWeight: 700 }}>{fmtCr(currentValue)}</div>
          </div>
          <div>
            <div style={{ fontSize: 10, color: 'var(--text-mut)' }}>Overall P&L</div>
            <div className={cn('num', signClass(overallPnl))} style={{ fontWeight: 700 }}>
              {fmtCr(overallPnl)}{overallPnlPct == null ? '' : ` (${overallPnlPct >= 0 ? '+' : ''}${Number(overallPnlPct).toFixed(2)}%)`}
            </div>
          </div>
          <div>
            <div style={{ fontSize: 10, color: 'var(--text-mut)' }}>Open Positions</div>
            <div className="num" style={{ fontWeight: 700 }}>{positions.length}</div>
          </div>
        </div>
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
            <div>{authNeeded ? 'Funds hidden: backend requires X-API-Key.' : brokerApiIssue ? 'Funds data pending: backend API did not respond.' : 'Funds API responded but no balance field found in response'}</div>
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
            {authNeeded ? 'Holdings hidden: backend requires X-API-Key.' : brokerApiIssue ? 'Holdings data pending: backend API did not respond.' : brokerTruthConnected ? 'No equity holdings found in Dhan broker response' : 'No broker holdings proof visible yet.'}
          </p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>{['Symbol', 'Qty', 'Avg Cost', 'LTP', 'P&L', 'P&L%'].map(h => <th key={h} className="thead" style={{ textAlign: h === 'Symbol' ? 'left' : 'right' }}>{h}</th>)}</tr>
            </thead>
            <tbody>
              {holdings.map((h: any, i: number) => {
                const avg = Number(getAvg(h) || 0)
                const ltp = Number(h.ltp ?? h.lastTradedPrice ?? 0)
                const qty = Number(h.quantity ?? h.totalQty ?? 0)
                const pnl = Number(h.pnl ?? ((ltp - avg) * qty))
                const pnlPct = Number(h.pnl_pct ?? (avg > 0 ? ((ltp - avg) / avg) * 100 : 0))
                return (
                  <tr key={i} className="trow">
                    <td className="tcell" style={{ fontWeight: 600 }}>{h.trading_symbol ?? h.tradingSymbol ?? h.symbol ?? '--'}</td>
                    <td className="tcell" style={{ textAlign: 'right' }}>{qty || '--'}</td>
                    <td className="tcell" style={{ textAlign: 'right' }}>{fmt(avg)}</td>
                    <td className="tcell" style={{ textAlign: 'right' }}><PriceCell value={ltp} /></td>
                    <td className={cn('tcell', signClass(pnl))} style={{ textAlign: 'right', fontWeight: 600 }}>{fmtCr(pnl)}</td>
                    <td className={cn('tcell', signClass(pnlPct))} style={{ textAlign: 'right' }}>{pnlPct >= 0 ? '+' : ''}{pnlPct.toFixed(2)}%</td>
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
            {authNeeded ? 'Positions hidden: backend requires X-API-Key.' : brokerApiIssue ? 'Positions data pending: backend API did not respond.' : brokerTruthConnected ? 'No open positions in Dhan account read-only response' : 'No broker positions proof visible yet.'}
          </p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>{['Symbol', 'Side', 'Qty', 'Entry', 'LTP', 'P&L'].map(h => <th key={h} className="thead">{h}</th>)}</tr>
            </thead>
            <tbody>
              {positions.map((p: any, i: number) => {
                const entry = Number(getEntry(p) || 0)
                const qty = Number(p.net_qty ?? p.netQty ?? p.quantity ?? 0)
                const upnl = Number(p.unrealized_pnl ?? p.unrealizedProfit ?? p.pnl ?? 0)
                let ltp = Number(p.ltp ?? 0)
                if (!(ltp > 0) && qty) ltp = entry + (upnl / qty)
                const side = p.position_type ?? p.positionType ?? p.side ?? '--'
                return (
                  <tr key={i} className="trow">
                    <td className="tcell" style={{ fontWeight: 600 }}>{p.trading_symbol ?? p.tradingSymbol ?? p.symbol ?? '--'}</td>
                    <td className="tcell"><span className={cn('pill text-xs', side === 'LONG' ? 'tx-up' : 'tx-down')} style={{ fontSize: '.6rem' }}>{side}</span></td>
                    <td className="tcell">{qty || '--'}</td>
                    <td className="tcell">{fmt(entry)}</td>
                    <td className="tcell"><PriceCell value={ltp} /></td>
                    <td className={cn('tcell', signClass(upnl))} style={{ fontWeight: 600 }}>{fmtCr(upnl)}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
