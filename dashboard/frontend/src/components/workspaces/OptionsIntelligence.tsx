import React from 'react';
import { useStore } from '../../store';
import { StatusChip, PENDINGState } from './TruthUI';
import { Layers, Activity, TrendingUp, ShieldAlert, BarChart2 } from 'lucide-react';

function pickArray(obj: any, ...keys: string[]): any[] {
  if (!obj) return [];
  for (const k of keys) {
    const v = obj[k];
    if (Array.isArray(v)) return v;
  }
  return [];
}

export const OptionsIntelligence: React.FC = React.memo(() => {
  const { chain, chainSymbol, marketTop, gainRank, brokerPositions } = useStore();

  const currentChain = chain[chainSymbol] || null;
  const rankings: any[] = Array.isArray(gainRank?.rankings) ? gainRank.rankings : [];
  const marketTopRows: any[] = Array.isArray(marketTop?.market_top_table) ? marketTop.market_top_table : [];
  const positions: any[] = pickArray(brokerPositions, 'rows', 'positions', 'data');

  return (
    <div data-testid="options-intel-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
      <header style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Layers size={20} color="var(--accent)" />
          <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Options Intelligence</h1>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <StatusChip label="SYMBOL" value={chainSymbol} status="ok" />
          <StatusChip label="MODE" value="ANALYTICS" />
        </div>
      </header>

      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Activity size={16} color="var(--text-sec)" />
              <h2 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Market Sentiment & Flows</h2>
            </div>
            {currentChain ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontSize: '10px', color: 'var(--text-mut)' }}>PCR (OI)</span>
                    <span className="num" style={{ fontSize: '16px' }}>{currentChain?.pcr_oi || '—'}</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontSize: '10px', color: 'var(--text-mut)' }}>PCR (VOL)</span>
                    <span className="num" style={{ fontSize: '16px' }}>{currentChain?.pcr_vol || '—'}</span>
                  </div>
                </div>
                <StatusChip label="IV PERCENTILE" value={currentChain?.iv_percentile ? `${currentChain.iv_percentile}%` : 'PENDING'} status={currentChain?.iv_percentile > 80 ? 'warn' : 'ok'} />
                <StatusChip label="OI CHANGE" value={currentChain?.oi_change || 'STABLE'} />
              </div>
            ) : (
              <PENDINGState reason={`NO CHAIN DATA YET FOR ${chainSymbol}`} />
            )}
          </section>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <TrendingUp size={16} color="var(--text-sec)" />
              <h2 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Gain Rank Comparison</h2>
            </div>
            {rankings.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-sec)', marginBottom: '4px' }}>System3 Top Forecasts vs Market Leaders</div>
                {rankings.slice(0, 3).map((r: any, i: number) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px', background: 'var(--surface-2)', borderRadius: '4px' }}>
                    <span style={{ fontSize: '12px', fontWeight: 600 }}>{r.underlying || r.symbol || '—'}</span>
                    <span className="num" style={{ color: 'var(--up)' }}>{Number.isFinite(Number(r.gain_pct)) ? Number(r.gain_pct).toFixed(1) : '—'}</span>
                  </div>
                ))}
              </div>
            ) : (
              <PENDINGState reason="GAIN RANK SERVICE PENDING" />
            )}
          </section>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <BarChart2 size={16} color="var(--text-sec)" />
              <h2 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Market Leaders vs System3</h2>
            </div>
            {marketTopRows.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-sec)', marginBottom: '4px' }}>Market-wide top contract gainers</div>
                {marketTopRows.slice(0, 3).map((r: any, i: number) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px', background: 'var(--surface-2)', borderRadius: '4px' }}>
                    <span style={{ fontSize: '12px', fontWeight: 600 }}>{r.underlying || r.symbol || '—'} {r.option_type || ''}</span>
                    <span className="num" style={{ color: 'var(--up)' }}>{Number.isFinite(Number(r.gain_pct)) ? `${Number(r.gain_pct).toFixed(1)}%` : '—'}</span>
                  </div>
                ))}
              </div>
            ) : (
              <PENDINGState reason="MARKET TOP DATA PENDING" />
            )}
          </section>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <ShieldAlert size={16} color="var(--text-sec)" />
              <h2 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Abnormal Activity</h2>
            </div>
            <PENDINGState reason="CATALYST & SENTIMENT DATA PENDING" />
          </section>
        </div>

        <section className="card" style={{ padding: '16px' }}>
          <h2 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>Dhan Position Context</h2>
          {positions.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%' }}>
                <thead>
                  <tr>
                    <th className="thead" style={{ textAlign: 'left' }}>Instrument</th>
                    <th className="thead" style={{ textAlign: 'right' }}>Qty</th>
                    <th className="thead" style={{ textAlign: 'right' }}>Avg</th>
                    <th className="thead" style={{ textAlign: 'right' }}>LTP</th>
                    <th className="thead" style={{ textAlign: 'right' }}>P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {positions.map((p: any, i: number) => {
                    const avg = Number(p.avg_price ?? p.buy_avg ?? p.entry_price ?? NaN);
                    const ltp = Number(p.ltp ?? NaN);
                    const pnl = Number(p.unrealized_pnl ?? p.pnl ?? NaN);
                    return (
                      <tr key={i} className="trow">
                        <td className="tcell">{p.trading_symbol ?? p.symbol ?? '—'}</td>
                        <td className="tcell" style={{ textAlign: 'right' }}>{p.net_qty ?? p.quantity ?? '—'}</td>
                        <td className="tcell" style={{ textAlign: 'right' }}>{Number.isFinite(avg) ? avg.toFixed(2) : '—'}</td>
                        <td className="tcell" style={{ textAlign: 'right' }}>{Number.isFinite(ltp) ? ltp.toFixed(2) : '—'}</td>
                        <td className="tcell" style={{ textAlign: 'right', color: Number.isFinite(pnl) ? (pnl >= 0 ? 'var(--up)' : 'var(--down)') : 'var(--text-mut)' }}>
                          {Number.isFinite(pnl) ? pnl.toFixed(2) : '—'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-mut)' }}>NO ACTIVE DHAN POSITIONS</div>
          )}
        </section>
      </div>
    </div>
  );
};
