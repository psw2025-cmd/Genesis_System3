import React from 'react';
import { Sparkles } from 'lucide-react';
import { PENDINGState, StatusChip } from './TruthUI';

export const MultibaggerResearch: React.FC = () => (
  <div data-testid="multibagger-root" style={{ height: '100%', overflowY: 'auto', background: 'var(--surface)' }}>
    <header style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <Sparkles size={20} color="var(--accent)" />
        <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Multibagger Research V4</h1>
      </div>
      <StatusChip label="RESEARCH" value="PENDING PROOF" status="warn" />
    </header>
    <div style={{ padding: '20px' }}>
      <section className="card" style={{ padding: '20px' }}>
        <h2 style={{ fontSize: '16px', margin: '0 0 10px' }}>Institutional Research Pipeline</h2>
        <p style={{ color: 'var(--text-sec)', fontSize: '12px', margin: '0 0 16px' }}>
          Forecast probabilities, model counts, accuracy, fundamentals, governance, flows, and actual-versus-predicted rows appear only after a production evidence contract supplies them.
        </p>
        <PENDINGState reason="NO VERIFIED MULTIBAGGER RESEARCH DATA CONTRACT AVAILABLE" dataTestId="multibagger-pending" />
      </section>
    </div>
  </div>
);
