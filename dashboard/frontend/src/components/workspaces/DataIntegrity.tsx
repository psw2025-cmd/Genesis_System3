import React from 'react';
import { useStore } from '../../store';
import { StatusChip, BlockedState } from './TruthUI';
import { Database, ShieldCheck, Wifi, RefreshCw } from 'lucide-react';

export const DataIntegrity: React.FC = () => {
  const { health, brokerConnected, wsStatus, lastSync, brokerStatus } = useStore();

  return (
    <div data-testid="data-integrity-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
      <header style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Database size={20} color="var(--accent)" />
          <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Data Integrity</h1>
        </div>
        <StatusChip label="SYNC" value={wsStatus.toUpperCase()} status={wsStatus === 'live' ? 'ok' : 'warn'} />
      </header>

      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <ShieldCheck size={16} color="var(--text-sec)" />
              <h2 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Authentication State</h2>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <StatusChip label="DHAN LOGIN" value={brokerConnected ? 'AUTHENTICATED' : 'REQUIRED'} status={brokerConnected ? 'ok' : 'error'} />
              <StatusChip label="TOKEN EXPIRY" value={brokerStatus?.token_expiry || 'UNKNOWN'} status={brokerStatus?.token_expiry ? 'ok' : 'warn'} />
              <div style={{ fontSize: '11px', color: 'var(--text-sec)', padding: '8px', background: brokerConnected ? 'rgba(0,232,122,0.05)' : 'rgba(255,77,106,0.05)', borderRadius: '4px' }}>
                {brokerConnected ? 'Session is active and secure.' : 'CRITICAL: Authentication disabled or token invalid.'}
              </div>
            </div>
          </section>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Wifi size={16} color="var(--text-sec)" />
              <h2 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Broker Connectivity</h2>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <StatusChip label="API ENDPOINT" value="web.dhan.co" status="mut" />
              <StatusChip label="WS STATUS" value={wsStatus.toUpperCase()} status={wsStatus === 'live' ? 'ok' : 'warn'} />
              <StatusChip label="LATENCY" value={health?.network?.latency ? `${health.network.latency}ms` : '—'} status={health?.network?.latency < 100 ? 'ok' : 'warn'} />
            </div>
          </section>

          <section className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <RefreshCw size={16} color="var(--text-sec)" />
              <h2 style={{ fontSize: '14px', fontWeight: 700, margin: 0 }}>Data Freshness</h2>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <StatusChip label="LAST SYNC" value={lastSync} />
              <StatusChip label="OPTION CHAIN" value={health?.data?.chain_age || 'UNKNOWN'} status={health?.data?.chain_age ? 'ok' : 'mut'} />
              <StatusChip label="MARKET TOP" value={health?.data?.top_age || 'UNKNOWN'} status={health?.data?.top_age ? 'ok' : 'mut'} />
            </div>
          </section>
        </div>

        <section className="card" style={{ padding: '16px' }}>
          <h2 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>API Error Log & Blockers</h2>
          {health?.errors?.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {health.errors.map((err: any, i: number) => (
                <div key={i} style={{ padding: '10px', background: 'rgba(255, 77, 106, 0.05)', border: '1px solid var(--border)', borderRadius: '4px', fontSize: '12px' }}>
                  <span style={{ color: 'var(--down)', fontWeight: 700, marginRight: '8px' }}>[{err.type}]</span>
                  <span style={{ color: 'var(--text-pri)' }}>{err.message}</span>
                  <div style={{ marginTop: '4px', fontSize: '10px', color: 'var(--text-mut)' }}>TS: {err.timestamp}</div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '20px', color: 'var(--up)', fontWeight: 600 }}>✓ NO ACTIVE DATA BLOCKERS</div>
          )}
        </section>

        <BlockedState reason="REPOSITORY / API SECURITY AUDIT PENDING" />
      </div>
    </div>
  );
};
