import React from 'react';
import { useStore } from '../../store';
import { StatusChip, PENDINGState } from './TruthUI';
import { Shield, Activity, Lock } from 'lucide-react';
import RiskDashboard from '../RiskDashboard';

export const RiskAndScenarios: React.FC = () => {
  const { autoGates, state } = useStore();

  // Unknown is not the same as CLOSED or safety-LOCKED.
  const gateActive = autoGates?.active === true;
  const gateKnown = typeof autoGates?.active === 'boolean';
  const gateLabel = gateActive ? 'ARMED' : gateKnown ? 'LOCKED' : 'UNVERIFIED';
  const marketStatus = state?.market?.is_open === true ? 'OPEN' : state?.market?.is_open === false ? 'CLOSED' : 'UNKNOWN';
  const liveOrdersStatus = state?.live_trading_enabled === true ? 'ENABLED' : state?.live_trading_enabled === false ? 'LOCKED' : 'UNVERIFIED';

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
          <StatusChip label="GATE" value={gateLabel} status={gateActive || !gateKnown ? 'warn' : 'ok'} />
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
              <Lock size={16} color="var(--text-sec)" />
              <h3 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Pre-Trade Security Gate</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-mut)', marginBottom: '4px' }}>State reported by the system proof gates</div>
              <StatusChip label="GATE STATE" value={gateActive ? 'ACTIVE' : gateKnown ? 'INHIBITED' : 'UNVERIFIED'} status={gateActive || !gateKnown ? 'warn' : 'ok'} />
              <div style={{ fontSize: '10px', color: 'var(--text-sec)', padding: '8px', background: 'var(--surface-2)', borderRadius: '4px' }}>
                Live order execution remains locked unless every server-side proof gate passes.
              </div>
            </div>
          </section>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Activity size={16} color="var(--text-sec)" />
              <h3 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Scenario Analysis</h3>
            </div>
            {state?.market || state?.risk ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <StatusChip label="MARKET" value={marketStatus} status={marketStatus === 'OPEN' ? 'ok' : marketStatus === 'CLOSED' ? 'mut' : 'warn'} />
                <StatusChip label="LIMITS" value={String(state?.risk?.limits?.status || '—')} status={String(state?.risk?.limits?.status).toUpperCase() === 'PASS' ? 'ok' : 'warn'} />
                <StatusChip label="LIVE ORDERS" value={liveOrdersStatus} status={liveOrdersStatus === 'ENABLED' ? 'error' : liveOrdersStatus === 'LOCKED' ? 'ok' : 'warn'} />
                <div style={{ fontSize: '11px', color: 'var(--text-sec)', padding: '8px', background: 'var(--surface-2)', borderRadius: '4px', lineHeight: 1.45 }}>
                  {state?.market?.reason || 'No verified scenario model output. Displayed fields originate from the current state snapshot only.'}
                </div>
              </div>
            ) : (
              <PENDINGState tone="mut" title="WAITING FOR STATE" reason="NO VERIFIED SCENARIO MODEL OUTPUT AVAILABLE" />
            )}
          </section>
        </div>
      </div>
    </div>
  );
};
