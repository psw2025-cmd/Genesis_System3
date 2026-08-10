import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { API_BASE, API_HEADERS } from '../../config';
import { StatusChip } from './TruthUI';
import { Sparkles, RefreshCw, TrendingUp, AlertTriangle } from 'lucide-react';

interface Row {
  rank: number; symbol: string; score: number; close: number;
  return_1y_pct: number | null; return_6m_pct: number | null; return_3m_pct: number | null;
  pct_from_52w_high: number | null; volume_expansion_x: number | null;
  above_200dma: boolean; max_drawdown_1y_pct: number; fo_eligible: boolean;
}

interface ScreenResult {
  status: string; reason?: string; rows: Row[]; generated_at_utc?: string;
  universe_size?: number; scanned?: number; succeeded?: number; errors?: number;
  data_source?: string; cache_hit?: boolean;
}

const num = (v: number | null | undefined, suffix = '') =>
  v === null || v === undefined ? '—' : `${v > 0 && suffix === '%' ? '+' : ''}${v}${suffix}`;

const retColor = (v: number | null | undefined) =>
  v === null || v === undefined ? 'var(--text-mut)' : v >= 0 ? 'var(--up)' : 'var(--down)';

export const MultibaggerResearch: React.FC = () => {
  const [data, setData] = useState<ScreenResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (refresh = false) => {
    setLoading(true); setError(null);
    try {
      const res = await axios.get(`${API_BASE}/api/equity/multibagger`, {
        headers: API_HEADERS, timeout: 120000, params: refresh ? { refresh: true } : {},
      });
      const d = res.data?.data ?? res.data;
      setData(d);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Request failed');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(false); }, [load]);

  const ok = data?.status === 'OK';

  return (
    <div data-testid="multibagger-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
      <header style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Sparkles size={20} color="var(--accent)" />
          <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Multibagger Equity Screen</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <StatusChip label="DATA" value={ok ? 'DHAN LIVE' : (data?.status || '...')} status={ok ? 'ok' : 'warn'} />
          <button
            data-testid="multibagger-refresh-btn"
            onClick={() => load(true)}
            disabled={loading}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--surface-2)', color: 'var(--text-pri)', cursor: loading ? 'wait' : 'pointer', fontSize: '12px' }}>
            <RefreshCw size={13} className={loading ? 'spin' : undefined} /> {loading ? 'Scanning…' : 'Rescan'}
          </button>
        </div>
      </header>

      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div className="card" style={{ padding: '14px 18px', display: 'flex', gap: '24px', flexWrap: 'wrap', fontSize: '12px', color: 'var(--text-sec)' }}>
          <span><TrendingUp size={13} style={{ verticalAlign: '-2px' }} /> Momentum multibagger ranking over real Dhan daily candles (~400 sessions)</span>
          {ok && (<>
            <span data-testid="multibagger-meta-universe">Universe: <b>{data?.universe_size}</b> F&O equities</span>
            <span>Scanned: <b>{data?.scanned}</b> · OK: <b>{data?.succeeded}</b> · Failed: <b>{data?.errors}</b></span>
            <span>Generated: <b>{data?.generated_at_utc?.slice(0, 16).replace('T', ' ')}Z</b>{data?.cache_hit ? ' (cached)' : ''}</span>
          </>)}
        </div>

        {loading && !data && (
          <div className="card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-mut)', fontSize: '13px' }} data-testid="multibagger-loading">
            Scanning F&O equity universe with live Dhan historical data…
          </div>
        )}

        {(error || (data && !ok)) && !loading && (
          <div className="card" data-testid="multibagger-not-ready" style={{ padding: '24px', textAlign: 'center', border: '1px solid rgba(245,158,11,.3)', background: 'rgba(245,158,11,.05)' }}>
            <AlertTriangle size={20} color="var(--amber)" style={{ marginBottom: '8px' }} />
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--amber)', marginBottom: '6px' }}>{data?.status || 'ERROR'}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-sec)', maxWidth: '560px', margin: '0 auto' }}>
              {error || data?.reason || 'Screener unavailable'}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-mut)', marginTop: '8px' }}>
              No placeholder data is ever shown — this screen renders only real broker data.
            </div>
          </div>
        )}

        {ok && (
          <section className="card" style={{ padding: '16px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }} data-testid="multibagger-table">
              <thead>
                <tr>
                  <th className="thead" style={{ textAlign: 'left', padding: '6px' }}>#</th>
                  <th className="thead" style={{ textAlign: 'left', padding: '6px' }}>Symbol</th>
                  <th className="thead" style={{ textAlign: 'right', padding: '6px' }}>Score</th>
                  <th className="thead" style={{ textAlign: 'right', padding: '6px' }}>Close</th>
                  <th className="thead" style={{ textAlign: 'right', padding: '6px' }}>1Y</th>
                  <th className="thead" style={{ textAlign: 'right', padding: '6px' }}>6M</th>
                  <th className="thead" style={{ textAlign: 'right', padding: '6px' }}>3M</th>
                  <th className="thead" style={{ textAlign: 'right', padding: '6px' }}>vs 52wH</th>
                  <th className="thead" style={{ textAlign: 'right', padding: '6px' }}>Vol ×</th>
                  <th className="thead" style={{ textAlign: 'center', padding: '6px' }}>200DMA</th>
                  <th className="thead" style={{ textAlign: 'right', padding: '6px' }}>MaxDD</th>
                  <th className="thead" style={{ textAlign: 'center', padding: '6px' }}>F&O</th>
                </tr>
              </thead>
              <tbody>
                {data!.rows.map((r) => (
                  <tr key={r.symbol} data-testid={`multibagger-row-${r.symbol}`} style={{ borderTop: '1px solid var(--border)' }}>
                    <td style={{ padding: '7px 6px', fontSize: '12px', color: 'var(--text-mut)' }}>{r.rank}</td>
                    <td style={{ padding: '7px 6px', fontSize: '13px', fontWeight: 700 }}>{r.symbol}</td>
                    <td style={{ padding: '7px 6px', textAlign: 'right' }}>
                      <span style={{ display: 'inline-block', minWidth: '46px', padding: '2px 8px', borderRadius: '5px', fontSize: '12px', fontWeight: 700, background: r.score >= 65 ? 'rgba(0,232,122,.12)' : r.score >= 45 ? 'rgba(245,158,11,.12)' : 'var(--surface-3)', color: r.score >= 65 ? 'var(--up)' : r.score >= 45 ? 'var(--amber)' : 'var(--text-mut)' }}>{r.score}</span>
                    </td>
                    <td style={{ padding: '7px 6px', textAlign: 'right', fontSize: '12px', fontFamily: 'var(--font-mono)' }}>₹{r.close}</td>
                    <td style={{ padding: '7px 6px', textAlign: 'right', fontSize: '12px', color: retColor(r.return_1y_pct) }}>{num(r.return_1y_pct, '%')}</td>
                    <td style={{ padding: '7px 6px', textAlign: 'right', fontSize: '12px', color: retColor(r.return_6m_pct) }}>{num(r.return_6m_pct, '%')}</td>
                    <td style={{ padding: '7px 6px', textAlign: 'right', fontSize: '12px', color: retColor(r.return_3m_pct) }}>{num(r.return_3m_pct, '%')}</td>
                    <td style={{ padding: '7px 6px', textAlign: 'right', fontSize: '12px', color: 'var(--text-sec)' }}>{num(r.pct_from_52w_high, '%')}</td>
                    <td style={{ padding: '7px 6px', textAlign: 'right', fontSize: '12px', color: (r.volume_expansion_x ?? 0) >= 1.3 ? 'var(--up)' : 'var(--text-sec)' }}>{num(r.volume_expansion_x)}</td>
                    <td style={{ padding: '7px 6px', textAlign: 'center', fontSize: '12px', color: r.above_200dma ? 'var(--up)' : 'var(--down)' }}>{r.above_200dma ? '▲' : '▼'}</td>
                    <td style={{ padding: '7px 6px', textAlign: 'right', fontSize: '12px', color: 'var(--down)' }}>{num(r.max_drawdown_1y_pct, '%')}</td>
                    <td style={{ padding: '7px 6px', textAlign: 'center', fontSize: '11px', color: r.fo_eligible ? 'var(--up)' : 'var(--text-mut)' }}>{r.fo_eligible ? 'YES' : 'NO'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ marginTop: '10px', fontSize: '11px', color: 'var(--text-mut)' }}>
              Source: Dhan /v2/charts/historical (real daily candles). Momentum research ranking — not investment advice. Live trading remains gated OFF.
            </div>
          </section>
        )}
      </div>
    </div>
  );
};
