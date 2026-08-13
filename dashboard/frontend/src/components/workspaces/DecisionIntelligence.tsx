import React from 'react';
import { useStore } from '../../store';
import { StatusChip } from './TruthUI';
import { Zap, Shield, Activity, Database, AlertTriangle } from 'lucide-react';

export const DecisionIntelligence: React.FC = React.memo(() => {
  const {
    health, brokerConnected, marketOpen, wsStatus, apiStatus
  } = useStore();

  const sectionStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    padding: '16px',
  };

  const gridStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '12px',
  };

  return (
    <div data-testid="decision-intel-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
      <header style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Zap size={20} color="var(--accent)" />
          <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Decision Intelligence</h1>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <StatusChip label="MODE" value="PAPER" status="warn" />
          <StatusChip label="LIVE" value="OFF" status="error" />
        </div>
      </header>

      <div style={sectionStyle}>
        <h2 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-mut)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          System Health & Truth
        </h2>

        <div style={gridStyle}>
          <div className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Shield size={16} color="var(--text-sec)" />
              <span style={{ fontWeight: 600 }}>Truth Control</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <StatusChip label="BROKER" value={brokerConnected ? 'CONNECTED' : 'DISCONNECTED'} status={brokerConnected ? 'ok' : 'error'} />
              <StatusChip label="WS" value={wsStatus.toUpperCase()} status={wsStatus === 'live' ? 'ok' : 'warn'} />
              <StatusChip label="MARKET" value={marketOpen ? 'OPEN' : 'CLOSED'} status={marketOpen ? 'ok' : 'mut'} />
            </div>
          </div>

          <div className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Activity size={16} color="var(--text-sec)" />
              <span style={{ fontWeight: 600 }}>Service Availability</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <StatusChip label="API" value={apiStatus?.status || 'UNKNOWN'} status={apiStatus?.status === 'ok' ? 'ok' : 'warn'} />
              <StatusChip label="SCANNER" value={health?.scanner?.status || 'OFFLINE'} status={health?.scanner?.status === 'active' ? 'ok' : 'mut'} />
              <StatusChip label="PREDICTOR" value={health?.predictor?.status || 'PENDING'} status={health?.predictor?.status === 'ready' ? 'ok' : 'error'} />
            </div>
          </div>

          <div className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Database size={16} color="var(--text-sec)" />
              <span style={{ fontWeight: 600 }}>Data Sources</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <StatusChip label="DHAN" value={brokerConnected ? 'AUTH OK' : 'NO AUTH'} status={brokerConnected ? 'ok' : 'error'} />
              <StatusChip label="NSE" value={health?.nse?.status || 'FALLBACK'} status={health?.nse?.status === 'ok' ? 'ok' : 'warn'} />
              <StatusChip label="DATA SOURCE" value={health?.data_source || 'UNKNOWN'} status={health?.data_source ? 'ok' : 'mut'} />
            </div>
          </div>

          <div className="card" style={{ padding: '16px', background: 'rgba(255, 77, 106, 0.03)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <AlertTriangle size={16} color="var(--down)" />
              <span style={{ fontWeight: 600, color: 'var(--down)' }}>Critical Blockers</span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-sec)' }}>
              {health?.blockers?.length > 0 ? (
                <ul style={{ margin: 0, paddingLeft: '16px' }}>
                  {health.blockers.map((b: any, i: number) => <li key={i}>{b}</li>)}
                </ul>
              ) : (
                <div style={{ color: 'var(--up)', fontWeight: 600 }}>✓ NO SYSTEM BLOCKERS</div>
              )}
            </div>
          </div>
        </div>

        <div className="card" style={{ padding: '16px', marginTop: '12px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-mut)', marginBottom: '8px' }}>AI DECISION BRIEF CONTRACT</div>
          <div style={{ fontSize: '13px', lineHeight: 1.5, color: 'var(--text-pri)', marginBottom: '12px' }}>
            System is operating in <strong>PAPER</strong> mode with <strong>LIVE OFF</strong>.
            Automated trading is inhibited by safety gates. All decisions are for simulation and research
            purposes only. Evidence-based auditing is active.
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button className="nav-item" style={{ width: 'auto', fontSize: '11px', padding: '4px 10px', border: '1px solid var(--border)' }} onClick={() => useStore.getState().setActiveTab('truth')}>TRUTH CONTROL</button>
            <button className="nav-item" style={{ width: 'auto', fontSize: '11px', padding: '4px 10px', border: '1px solid var(--border)' }} onClick={() => useStore.getState().setActiveTab('options-intel')}>OPTIONS INTEL</button>
            <button className="nav-item" style={{ width: 'auto', fontSize: '11px', padding: '4px 10px', border: '1px solid var(--border)' }} onClick={() => useStore.getState().setActiveTab('risk-scenarios')}>RISK & SCENARIOS</button>
            <button className="nav-item" style={{ width: 'auto', fontSize: '11px', padding: '4px 10px', border: '1px solid var(--border)' }} onClick={() => useStore.getState().setActiveTab('data-integrity')}>DATA INTEGRITY</button>
          </div>
        </div>
      </div>
    </div>
  );
};
