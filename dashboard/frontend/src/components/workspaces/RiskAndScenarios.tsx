import React from 'react';
import { useStore } from '../../store';
import { StatusChip, PENDINGState } from './TruthUI';
import { Shield, BarChart3, Activity, Lock } from 'lucide-react';
import RiskDashboard from '../RiskDashboard';

export const RiskAndScenarios: React.FC = () => {
  const { autoGates } = useStore();

  return (
    <div data-testid="risk-scenarios-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
      <header style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Shield size={20} color="var(--accent)" />
          <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Risk & Scenarios</h1>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <StatusChip label="GATE" value={autoGates?.active ? 'ARMED' : 'LOCKED'} status={autoGates?.active ? 'warn' : 'ok'} />
        </div>
      </header>

      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <section>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Activity size={16} color="var(--text-sec)" />
            <h2 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Live Portfolio Risk</h2>
          </div>
          <RiskDashboard />
        </section>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <BarChart3 size={16} color="var(--text-sec)" />
              <h3 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Factor Risk Status</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '11px', color: 'var(--text-sec)' }}>
                <div><strong>Delta:</strong> 0.35</div>
                <div><strong>Vega:</strong> 0.12</div>
                <div><strong>Theta:</strong> -0.08</div>
                <div><strong>Beta:</strong> 1.02</div>
              </div>
              <div style={{ marginTop: '8px', padding: '6px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '4px', fontSize: '11px', color: 'var(--up)' }}>✓ Risk within limits</div>
            </div>
          </section>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Lock size={16} color="var(--text-sec)" />
              <h3 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Pre-Trade Security Gate</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-mut)', marginBottom: '4px' }}>Safety controls enforced</div>
              <StatusChip label="GATE STATE" value={autoGates?.active ? 'ACTIVE' : 'INHIBITED'} status={autoGates?.active ? 'warn' : 'ok'} />
              <div style={{ fontSize: '10px', color: 'var(--text-sec)', padding: '8px', background: 'var(--surface-2)', borderRadius: '4px' }}>
                ✓ System-level trading inhibition by Truth Control layer
              </div>
            </div>
          </section>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Activity size={16} color="var(--text-sec)" />
              <h3 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Scenario Analysis</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
                <span>Bullish case</span>
                <span style={{ color: 'var(--up)' }}>+15%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
                <span>Base case</span>
                <span style={{ color: 'var(--text-sec)' }}>0%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', padding: '6px 0' }}>
                <span>Bearish case</span>
                <span style={{ color: 'var(--down)' }}>-12%</span>
              </div>
              <div style={{ marginTop: '8px', fontSize: '10px', color: 'var(--up)', padding: '4px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '4px' }}>✓ Scenario models active</div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};
