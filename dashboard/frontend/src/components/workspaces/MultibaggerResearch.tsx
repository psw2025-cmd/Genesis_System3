import React from 'react';
import { Sparkles } from 'lucide-react';
import { useStore } from '../../store';
import { MetricTile, PENDINGState, StatusChip } from './TruthUI';
import { formatInr, formatIstStamp } from '../../lib/formatLive';

export const MultibaggerResearch: React.FC = () => {
  const { research, state, health, paper, pnl } = useStore()
  const contract = research || {}
  const status = String(contract.status || 'loading').toUpperCase()
  const candidates: any[] = Array.isArray(contract.candidates) ? contract.candidates : []
  const sections = contract.sections && typeof contract.sections === 'object' ? contract.sections : {}
  const ready = candidates.length > 0
  const totalPnl = paper?.pnl?.summary?.total_pnl ?? pnl?.summary?.total_pnl ?? state?.pnl?.total

  return (
    <div data-testid="multibagger-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
      <header style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Sparkles size={20} color="var(--accent)" aria-hidden />
          <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Multibagger Research V4</h1>
        </div>
        <StatusChip
          label="CONTRACT"
          value={status}
          status={status === 'PARTIAL' || status === 'OK' ? 'ok' : status === 'STALE' ? 'warn' : 'mut'}
        />
      </header>
      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 12 }}>
          <MetricTile label="Analyzer mode" value={String(health?.mode || state?.mode || 'PAPER')} sub="LIVE trading locked off" />
          <MetricTile label="Paper P&L" value={formatInr(totalPnl)} />
          <MetricTile label="Exposure" value={formatInr(state?.risk?.exposure)} />
          <MetricTile label="Last fetch" value={formatIstStamp(state?.last_fetch_ts_iso)} />
          <MetricTile label="Candidates" value={String(candidates.length)} sub={contract.reason || 'Live /api/research/multibagger'} />
        </div>

        {ready ? (
          <section className="card" style={{ padding: '20px', overflowX: 'auto' }}>
            <h2 style={{ fontSize: '16px', margin: '0 0 12px' }}>Verified candidates</h2>
            <table style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th className="thead" style={{ textAlign: 'left' }}>Rank</th>
                  <th className="thead" style={{ textAlign: 'left' }}>Symbol</th>
                  <th className="thead" style={{ textAlign: 'right' }}>Price</th>
                  <th className="thead" style={{ textAlign: 'left' }}>Model</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map((row) => (
                  <tr key={row.candidate_id || row.symbol} className="trow">
                    <td className="tcell">{row.rank ?? '—'}</td>
                    <td className="tcell">{row.symbol ?? '—'}</td>
                    <td className="tcell" style={{ textAlign: 'right' }}>{formatInr(row.price?.value)}</td>
                    <td className="tcell">{row.model?.name ? `${row.model.name} ${row.model.version || ''}`.trim() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        ) : (
          <section className="card" style={{ padding: '20px' }}>
            <h2 style={{ fontSize: '16px', margin: '0 0 10px' }}>Institutional Research Pipeline</h2>
            <p style={{ color: 'var(--text-sec)', fontSize: '12px', margin: '0 0 16px' }}>
              Forecast probabilities are not invented from analyzer PnL. This board shows the live evidence
              contract. Sections stay pending until a producer supplies provenance-valid candidates.
            </p>
            <PENDINGState
              tone="mut"
              title="NO VERIFIED CANDIDATES"
              reason={contract.reason || 'Waiting for /api/research/multibagger producer evidence'}
              dataTestId="multibagger-pending"
            />
            {Object.keys(sections).length > 0 && (
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 16 }}>
                {Object.entries(sections).map(([key, value]) => (
                  <StatusChip key={key} label={key.replace(/_/g, ' ')} value={String(value).toUpperCase()} status={String(value) === 'partial' ? 'ok' : 'mut'} />
                ))}
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  )
}
