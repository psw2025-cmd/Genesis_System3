import React from 'react';
import { Search } from 'lucide-react';
import { PENDINGState, StatusChip } from './TruthUI';

export const PredictionAudit: React.FC = () => (
  <div data-testid="prediction-audit-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
    <header style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <Search size={20} color="var(--accent)" />
        <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Prediction Audit Ledger</h1>
      </div>
      <StatusChip label="AUDIT" value="PENDING DATA" status="warn" />
    </header>
    <div style={{ padding: '20px' }}>
      <section className="card" style={{ padding: '20px' }}>
        <h2 style={{ fontSize: '14px', margin: '0 0 10px' }}>Forensic Audit History</h2>
        <p style={{ color: 'var(--text-sec)', fontSize: '12px', margin: '0 0 16px' }}>
          Monitoring status, ledger count, model accuracy, and last-update time remain unavailable until the audit service supplies timestamped records.
        </p>
        <PENDINGState reason="NO VERIFIED PREDICTION AUDIT LEDGER RESPONSE AVAILABLE" dataTestId="prediction-audit-pending" />
      </section>
    </div>
  </div>
);
