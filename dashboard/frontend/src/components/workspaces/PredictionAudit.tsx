import React from 'react';
import { StatusChip, PENDINGState } from './TruthUI';
import { Search, Shield } from 'lucide-react';

export const PredictionAudit: React.FC = () => {
  return (
    <div data-testid="prediction-audit-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
      <header style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Search size={20} color="var(--accent)" />
          <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Prediction Audit Ledger</h1>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <StatusChip label="AUDIT" value="PENDING" status="warn" />
        </div>
      </header>

      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="card" style={{ padding: '16px', background: 'rgba(59, 130, 246, 0.03)', border: '1px solid var(--accent)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Shield size={16} color="var(--accent)" />
            <span style={{ fontSize: '14px', fontWeight: 700 }}>Immutable Forensic Accountability (Contract)</span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-sec)', margin: 0 }}>
            Every System3 prediction must be recorded with its full context: probability, uncertainty,
            evidence, counter-evidence, model version, and frozen data cutoff, for post-trade calibration.
            No production prediction ledger is wired to this dashboard yet — the scanner's gain-rank
            list is not a validated forecast and is not shown here as one.
          </p>
        </div>

        <PENDINGState reason="PREDICTION LEDGER PENDING" />

        <section className="card" style={{ padding: '16px' }}>
          <h2 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>Forensic Audit History</h2>
          <table style={{ width: '100%' }}>
            <thead>
              <tr>
                <th className="thead" style={{ textAlign: 'left' }}>Timestamp</th>
                <th className="thead" style={{ textAlign: 'left' }}>Target</th>
                <th className="thead" style={{ textAlign: 'right' }}>Prob</th>
                <th className="thead" style={{ textAlign: 'right' }}>Score</th>
                <th className="thead" style={{ textAlign: 'right' }}>Outcome</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td colSpan={5} style={{ padding: '40px', textAlign: 'center', color: 'var(--text-mut)', fontSize: '12px' }}>
                  PENDING — DATA SERVICE PENDING
                </td>
              </tr>
            </tbody>
          </table>
        </section>
      </div>
    </div>
  );
};
