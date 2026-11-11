import React from 'react';
import { useStore } from '../../store';
import { StatusChip, PENDINGState } from './TruthUI';
import { Layers, Activity, TrendingUp, ShieldAlert, BarChart2 } from 'lucide-react';
import AdvancedCharts from '../AdvancedCharts';

function pickArray(obj: any, ...keys: string[]): any[] {
  if (!obj) return [];
  for (const k of keys) {
    const v = obj[k];
    if (Array.isArray(v)) return v;
  }
  return [];
}

export const OptionsIntelligence: React.FC = () => {
  const { chain, chainSymbol, setChainSymbol, setActiveTab, marketTop, gainRank, brokerPositions, marketOpen } = useStore();
  const [allUnderlyings, setAllUnderlyings] = React.useState<string[]>([
    'NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX',
    'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN',
    'TATAMOTORS', 'BHARTIARTL', 'ITC', 'LT', 'MARUTI', 'SUNPHARMA',
    'TATASTEEL', 'BAJFINANCE', 'ADANIENT'
  ]);

  React.useEffect(() => {
    let cancelled = false;
    fetch('/api/underlyings')
      .then(res => res.json())
      .then(data => {
        if (!cancelled && Array.isArray(data?.underlyings) && data.underlyings.length > 0) {
          setAllUnderlyings(Array.from(new Set(data.underlyings)));
        }
      })
      .catch(() => {});
    return () => { cancelled = true; };
  }, []);

  const currentChain = chain[chainSymbol] || null;
  const rankings: any[] = Array.isArray(gainRank?.rankings) ? gainRank.rankings : [];
  const marketTopRows: any[] = Array.isArray(marketTop?.market_top_table) ? marketTop.market_top_table : [];
  const positions: any[] = pickArray(brokerPositions, 'rows', 'positions', 'data');

  // Compute fallback IV percentile and OI change from contracts if not provided at root
  const contracts = Array.isArray(currentChain?.contracts) ? currentChain.contracts : [];
  const computedOiChange = React.useMemo(() => {
    if (currentChain?.oi_change != null) return String(currentChain.oi_change);
    if (!contracts.length) return null;
    const total = contracts.reduce((sum: number, c: any) => sum + (Number(c.oi_change) || 0), 0);
    return total >= 0 ? `+${total.toLocaleString('en-IN')}` : total.toLocaleString('en-IN');
  }, [currentChain?.oi_change, contracts]);

  const computedIvPct = React.useMemo(() => {
    if (currentChain?.iv_percentile != null) return Number(currentChain.iv_percentile);
    const validIvs = contracts.map((c: any) => Number(c.iv)).filter((iv: number) => Number.isFinite(iv) && iv > 0);
    if (!validIvs.length) return null;
    const avg = validIvs.reduce((a: number, b: number) => a + b, 0) / validIvs.length;
    return Math.round((validIvs.filter((v: number) => v <= avg).length / validIvs.length) * 100);
  }, [currentChain?.iv_percentile, contracts]);

  return (
    <div data-testid="options-intel-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
      <header style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Layers size={20} color="var(--accent)" />
          <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Options Intelligence</h1>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <StatusChip label="SYMBOL" value={chainSymbol} status="ok" />
          <StatusChip label="MARKET" value={marketOpen ? 'OPEN' : 'CLOSED'} status={marketOpen ? 'ok' : 'warn'} />
        </div>
      </header>

      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
          {['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'INFY', 'SBIN'].map((symbol) => (
            <button key={symbol} type="button" className={`soft-btn ${chainSymbol === symbol ? 'active' : ''}`} onClick={() => setChainSymbol(symbol)}>{symbol}</button>
          ))}
          <select
            value={chainSymbol}
            onChange={(e) => setChainSymbol(e.target.value)}
            className="soft-btn"
            style={{ minHeight: '32px', background: 'var(--surface-2)', color: 'var(--text-pri)', border: '1px solid var(--border)', padding: '0 8px', borderRadius: '6px' }}
            aria-label="Filter underlying symbol"
          >
            {allUnderlyings.map((sym) => (
              <option key={sym} value={sym}>{sym}</option>
            ))}
          </select>
          <button type="button" className="soft-btn" onClick={() => setActiveTab('chain')}>OPEN FULL OPTION CHAIN</button>
        </div>
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
                    <span className="num" style={{ fontSize: '16px' }}>{currentChain?.pcr_oi ?? currentChain?.pcr ?? '—'}</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontSize: '10px', color: 'var(--text-mut)' }}>PCR (VOL)</span>
                    <span className="num" style={{ fontSize: '16px' }}>{currentChain?.pcr_vol ?? currentChain?.pcr ?? '—'}</span>
                  </div>
                </div>
                <StatusChip label="IV PERCENTILE" value={computedIvPct != null ? `${computedIvPct}%` : '50% (MEDIAN)'} status={computedIvPct && computedIvPct > 80 ? 'warn' : 'ok'} />
                <StatusChip label="OI CHANGE" value={computedOiChange ?? '+0 (AFTER HOURS)'} status="ok" />
                <StatusChip label="SOURCE" value={currentChain?.source ?? currentChain?.data_source ?? 'DHAN'} status="ok" />
              </div>
            ) : (
              <PENDINGState
                tone="mut"
                title={marketOpen ? 'CHAIN WARMING' : 'AFTER HOURS'}
                reason={currentChain?.message || `No Dhan chain snapshot for ${chainSymbol} yet. Analyzer keeps last-good when available.`}
              />
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
              <PENDINGState
                tone="mut"
                title={marketOpen ? 'RANKING WARMING' : 'AFTER HOURS'}
                reason="Gain-rank rows appear when the scanner or market-top stream supplies them."
              />
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
              <PENDINGState
                tone="mut"
                title={marketOpen ? 'MARKET TOP WARMING' : 'AFTER HOURS'}
                reason="Market-wide top contract table is empty until Dhan market-top data arrives."
              />
            )}
          </section>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <ShieldAlert size={16} color="var(--text-sec)" />
              <h2 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Abnormal Activity</h2>
            </div>
            <PENDINGState
              tone="mut"
              title={marketOpen ? 'NO CATALYST FEED' : 'AFTER HOURS'}
              reason="No catalyst/sentiment feed is wired. Unusual activity is not invented from empty after-hours chains."
            />
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

        {/* Real-time Interactive Option Analytics & Visual Charts */}
        <section className="card" style={{ padding: '20px', background: 'var(--surface-2)' }}>
          <AdvancedCharts />
        </section>
      </div>
    </div>
  );
};
