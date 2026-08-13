import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import { useStore } from '../store'
import { PENDINGState, StatusChip } from './workspaces/TruthUI'

type NumericMap = Record<string, number>

interface RiskMetrics {
  var_95?: number
  expected_shortfall_95?: number
  total_exposure?: number
  concentration_risk?: number
  total_pnl?: number
  position_count?: number
  max_underlying_exposure?: number
  greeks_exposure?: Partial<Record<'delta' | 'gamma' | 'theta' | 'vega', number>>
  underlying_exposures?: NumericMap
}

type LoadState = 'loading' | 'ready' | 'partial' | 'unavailable'

const numberOrUndefined = (value: unknown): number | undefined => {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : undefined
}

const money = (value: unknown): string => {
  const parsed = numberOrUndefined(value)
  return parsed === undefined ? '—' : `₹${parsed.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
}

const decimal = (value: unknown, digits = 2): string => {
  const parsed = numberOrUndefined(value)
  return parsed === undefined ? '—' : parsed.toFixed(digits)
}

function stateRiskFallback(state: any): RiskMetrics | null {
  const risk = state?.risk
  if (!risk || typeof risk !== 'object') return null
  return {
    var_95: numberOrUndefined(risk.var_95 ?? risk.var95),
    expected_shortfall_95: numberOrUndefined(risk.expected_shortfall_95 ?? risk.es95),
    total_exposure: numberOrUndefined(risk.total_exposure ?? risk.exposure),
    concentration_risk: numberOrUndefined(risk.concentration_risk ?? risk.concentration),
    total_pnl: numberOrUndefined(risk.total_pnl ?? state?.pnl?.total),
    position_count: numberOrUndefined(risk.position_count ?? state?.positions?.length),
    greeks_exposure: risk.greeks_exposure,
    underlying_exposures: risk.underlying_exposures,
  }
}

export default function RiskDashboard() {
  const state = useStore((store) => store.state)
  const fallback = useMemo(() => stateRiskFallback(state), [state])
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(fallback)
  const [loadState, setLoadState] = useState<LoadState>(fallback ? 'partial' : 'loading')
  const [message, setMessage] = useState('Loading read-only portfolio risk…')

  useEffect(() => {
    const controller = new AbortController()

    const fetchRiskData = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/risk/portfolio`, {
          signal: controller.signal,
          timeout: 15000,
        })
        const payload = response.data
        if (payload?.status !== 'ok' || !payload?.risk_metrics) {
          throw new Error(payload?.message || 'Portfolio risk is not available')
        }
        setRiskMetrics(payload.risk_metrics)
        setLoadState('ready')
        setMessage('Read-only portfolio risk loaded')
      } catch (error: any) {
        if (error?.code === 'ERR_CANCELED') return
        if (fallback) {
          setRiskMetrics(fallback)
          setLoadState('partial')
          setMessage('Showing partial risk fields from the system state snapshot')
        } else {
          setRiskMetrics(null)
          setLoadState('unavailable')
          const status = error?.response?.status
          setMessage(status ? `Risk service unavailable (HTTP ${status})` : 'Risk service unavailable')
        }
      }
    }

    void fetchRiskData()
    return () => controller.abort()
  }, [])

  useEffect(() => {
    if (loadState !== 'ready' && fallback) {
      setRiskMetrics(fallback)
      setLoadState('partial')
      setMessage('Showing partial risk fields from the system state snapshot')
    }
  }, [fallback, loadState])

  if (!riskMetrics) {
    return <PENDINGState reason={loadState === 'loading' ? 'LOADING READ-ONLY PORTFOLIO RISK' : message} dataTestId="risk-data-pending" />
  }

  const greeks = riskMetrics.greeks_exposure || {}
  const exposures = riskMetrics.underlying_exposures || {}
  const concentration = numberOrUndefined(riskMetrics.concentration_risk)
  const pnl = numberOrUndefined(riskMetrics.total_pnl)

  return (
    <div data-testid="risk-dashboard" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        <StatusChip label="SOURCE" value={loadState === 'ready' ? 'PORTFOLIO RISK API' : 'STATE SNAPSHOT'} status={loadState === 'ready' ? 'ok' : 'warn'} />
        <StatusChip label="STATUS" value={loadState.toUpperCase()} status={loadState === 'ready' ? 'ok' : 'warn'} />
        <span style={{ color: 'var(--text-mut)', fontSize: '11px', alignSelf: 'center' }}>{message}</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '12px' }}>
        {[
          ['Value at Risk (95%)', money(riskMetrics.var_95), numberOrUndefined(riskMetrics.var_95)],
          ['Expected Shortfall (95%)', money(riskMetrics.expected_shortfall_95), numberOrUndefined(riskMetrics.expected_shortfall_95)],
          ['Total Exposure', money(riskMetrics.total_exposure), undefined],
          ['Concentration Risk', concentration === undefined ? '—' : `${concentration.toFixed(1)}%`, concentration === undefined ? undefined : 50 - concentration],
          ['Total P&L', money(pnl), pnl],
          ['Open Positions', decimal(riskMetrics.position_count, 0), undefined],
        ].map(([label, value, tone]) => (
          <div key={String(label)} className="card" style={{ padding: '14px' }}>
            <div style={{ color: 'var(--text-mut)', fontSize: '10px', textTransform: 'uppercase' }}>{label}</div>
            <div className="num" style={{ marginTop: '6px', fontSize: '20px', fontWeight: 800, color: typeof tone === 'number' ? (tone < 0 ? 'var(--down)' : 'var(--up)') : 'var(--text-pri)' }}>{value}</div>
          </div>
        ))}
      </div>

      <div className="card" style={{ padding: '16px' }}>
        <h3 style={{ margin: '0 0 12px', fontSize: '14px' }}>Greeks Exposure</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(90px, 1fr))', gap: '12px' }}>
          {(['delta', 'gamma', 'theta', 'vega'] as const).map((name) => (
            <div key={name}>
              <div style={{ color: 'var(--text-mut)', fontSize: '10px', textTransform: 'uppercase' }}>{name}</div>
              <div className="num" style={{ marginTop: '4px', fontWeight: 800 }}>{decimal(greeks[name], 4)}</div>
            </div>
          ))}
        </div>
      </div>

      {Object.keys(exposures).length > 0 && (
        <div className="card" style={{ padding: '16px' }}>
          <h3 style={{ margin: '0 0 12px', fontSize: '14px' }}>Exposure by Underlying</h3>
          <div style={{ display: 'grid', gap: '8px' }}>
            {Object.entries(exposures).map(([underlying, exposure]) => (
              <div key={underlying} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                <span>{underlying}</span><span className="num">{money(exposure)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
