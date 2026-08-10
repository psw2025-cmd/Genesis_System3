import React from 'react';
import { StatusChip, BlockedState } from './TruthUI';
import { Sparkles, BarChart, Zap, Search } from 'lucide-react';

export const MultibaggerResearch: React.FC = () => {
  return (
    <div data-testid="multibagger-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
      <header style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Sparkles size={20} color="var(--accent)" />
          <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Multibagger Research V4</h1>
        </div>
        <StatusChip label="RESEARCH" value="TRUTH-ONLY" status="warn" />
      </header>

      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div className="card" style={{ padding: '20px', textAlign: 'center', border: '1px solid var(--accent)', background: 'rgba(59, 130, 246, 0.05)' }}>
          <Zap size={24} color="var(--accent)" style={{ marginBottom: '12px' }} />
          <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '8px' }}>Institutional Research Pipeline</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-sec)', maxWidth: '600px', margin: '0 auto' }}>
            The Multibagger V4 engine performs high-horizon forecast matrix analysis for 2x–100x potential symbols.
            All results below are constrained by available production truth.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '16px' }}>
          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <BarChart size={16} color="var(--text-sec)" />
              <h3 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Horizon Forecast Matrix</h3>
            </div>
            <BlockedState reason="FORECAST SERVICE NOT IMPLEMENTED" />
          </section>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Search size={16} color="var(--text-sec)" />
              <h3 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Probability Ladder (2x - 100x)</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {[2, 5, 10, 50, 100].map(mult => (
                <div key={mult} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ width: '40px', fontSize: '12px', fontWeight: 700, color: 'var(--text-pri)' }}>{mult}x</div>
                  <div className="progress-bar" style={{ flex: 1 }}>
                    <div className="progress-fill" style={{ width: '0%', background: 'var(--accent)' }} />
                  </div>
                  <div style={{ width: '50px', fontSize: '10px', color: 'var(--text-mut)', textAlign: 'right' }}>BLOCKED</div>
                </div>
              ))}
            </div>
          </section>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <section className="card" style={{ padding: '12px' }}>
            <h4 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-mut)', marginBottom: '8px', textTransform: 'uppercase' }}>Fundamentals</h4>
            <BlockedState reason="DATA SERVICE NOT IMPLEMENTED" />
          </section>
          <section className="card" style={{ padding: '12px' }}>
            <h4 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-mut)', marginBottom: '8px', textTransform: 'uppercase' }}>Governance</h4>
            <BlockedState reason="DATA SERVICE NOT IMPLEMENTED" />
          </section>
          <section className="card" style={{ padding: '12px' }}>
            <h4 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-mut)', marginBottom: '8px', textTransform: 'uppercase' }}>Ownership / Flows</h4>
            <BlockedState reason="DATA SERVICE NOT IMPLEMENTED" />
          </section>
        </div>

        <section className="card" style={{ padding: '16px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>Actual-versus-Predicted Ledger</h3>
          <table style={{ width: '100%' }}>
            <thead>
              <tr>
                <th className="thead" style={{ textAlign: 'left' }}>Symbol</th>
                <th className="thead" style={{ textAlign: 'left' }}>Date</th>
                <th className="thead" style={{ textAlign: 'right' }}>Predicted</th>
                <th className="thead" style={{ textAlign: 'right' }}>Actual</th>
                <th className="thead" style={{ textAlign: 'right' }}>Error</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td colSpan={5} style={{ padding: '40px', textAlign: 'center', color: 'var(--text-mut)', fontSize: '12px' }}>
                  NO LEDGER ENTRIES AVAILABLE
                </td>
              </tr>
            </tbody>
          </table>
        </section>
      </div>
    </div>
  );
};
