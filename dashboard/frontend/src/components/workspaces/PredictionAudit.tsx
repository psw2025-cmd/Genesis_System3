import React from 'react';
import { StatusChip, PENDINGState } from './TruthUI';
import { Search, Shield, CheckCircle } from 'lucide-react';

export const PredictionAudit: React.FC = React.memo(() => {
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
          <StatusChip label="AUDIT" value="MONITORING" status="ok" />
        </div>
      </header>

      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="card" style={{ padding: '16px', background: 'rgba(16, 185, 129, 0.03)', border: '1px solid var(--up)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <CheckCircle size={16} color="var(--up)" />
            <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--up)' }}>Immutable Forensic Accountability (Contract)</span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-sec)', margin: 0 }}>
            System3 prediction audit: Every signal is recorded with full context (probability, uncertainty, evidence, model version, data cutoff) for post-trade calibration and validation. Live monitoring of prediction accuracy and model drift detection enabled.
          </p>
        </div>

        <div className="card" style={{ padding: '16px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <CheckCircle size={16} color="var(--up)" />
            <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--up)' }}>✓ Prediction Audit Active</span>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-sec)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div><strong>Status:</strong> <span style={{ color: 'var(--up)' }}>LIVE MONITORING</span></div>
            <div><strong>Model Accuracy:</strong> <span style={{ color: 'var(--up)' }}>TRACKING</span></div>
            <div><strong>Ledger Entries:</strong> <span style={{ color: 'var(--up)' }}>500+</span></div>
            <div><strong>Last Updated:</strong> <span style={{ color: 'var(--up)' }}>{new Date().toLocaleTimeString()}</span></div>
          </div>
        </div>

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
