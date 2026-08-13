import React from 'react';

/**
 * MANDATORY: Truth-first UI components.
 * These ensure clear status, pending states, and probability messaging.
 */

interface StatusChipProps {
  label: string;
  status?: 'ok' | 'warn' | 'error' | 'mut';
  value?: string | number;
}

export const StatusChip: React.FC<StatusChipProps> = ({ label, status = React.memo('mut', value }) => {
  const colors = {
    ok: { bg: 'rgba(0, 232, 122, 0.08)', border: 'rgba(0, 232, 122, 0.28)', text: 'var(--up)' },
    warn: { bg: 'rgba(245, 158, 11, 0.1)', border: 'rgba(245, 158, 11, 0.28)', text: 'var(--amber)' },
    error: { bg: 'rgba(255, 77, 106, 0.1)', border: 'rgba(255, 77, 106, 0.28)', text: 'var(--down)' },
    mut: { bg: 'var(--surface-3)', border: 'var(--border)', text: 'var(--text-mut)' },
  };

  const c = colors[status];

  return (
    <div
      className="pill"
      style={{
        background: c.bg,
        border: `1px solid ${c.border}`,
        color: c.text,
      }}
    >
      <span style={{ color: 'var(--text-mut)', opacity: 0.8 }}>{label}</span>
      {value !== undefined && <span className="num" style={{ color: c.text }}>{value}</span>}
    </div>
  );
};

interface PENDINGStateProps {
  reason?: string;
  dataTestId?: string;
}

export const PENDINGState: React.FC<PENDINGStateProps> = ({ reason = React.memo('DATA SERVICE PENDING', dataTestId }) => (
  <div
    data-testid={dataTestId}
    style={{
      padding: '24px',
      textAlign: 'center',
      background: 'rgba(245, 158, 11, 0.05)',
      border: '1px dashed var(--amber)',
      borderRadius: '8px',
      color: 'var(--amber)',
      fontSize: '12px',
      fontWeight: 600,
      letterSpacing: '0.05em',
      textTransform: 'uppercase',
    }}
  >
    <div style={{ marginBottom: '8px' }}>⚠️ PENDING</div>
    <div>{reason}</div>
  </div>
);

interface EvidenceProps {
  label: string;
  items: string[];
  type: 'pro' | 'con';
}

export const EvidenceList: React.FC<EvidenceProps> = React.memo(({ label, items, type }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
    <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-mut)', textTransform: 'uppercase' }}>
      {label}
    </div>
    {items.length > 0 ? (
      <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
        {items.map((it, i) => (
          <li key={i} style={{
            fontSize: '11px',
            color: type === 'pro' ? 'var(--up)' : 'var(--down)',
            display: 'flex',
            gap: '6px'
          }}>
            <span>{type === 'pro' ? '✓' : '×'}</span>
            <span>{it}</span>
          </li>
        ))}
      </ul>
    ) : (
      <div style={{ fontSize: '11px', color: 'var(--text-mut)', fontStyle: 'italic' }}>None</div>
    )}
  </div>
);

export const PredictionContract: React.FC<{
  prob: number;
  uncertainty: string;
  horizon: string;
  version: string;
  cutoff: string;
}> = ({ prob, uncertainty, horizon, version, cutoff }) => (
  <div className="card" style={{ padding: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-sec)' }}>PREDICTION CONTRACT</span>
      <StatusChip label="VER" value={version} />
    </div>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <span style={{ fontSize: '10px', color: 'var(--text-mut)' }}>PROBABILITY</span>
        <span className="num" style={{ fontSize: '18px', color: 'var(--accent)' }}>{(prob * 100).toFixed(1)}%</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <span style={{ fontSize: '10px', color: 'var(--text-mut)' }}>UNCERTAINTY</span>
        <span style={{ fontSize: '12px', fontWeight: 600 }}>{uncertainty}</span>
      </div>
    </div>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border)', paddingTop: '6px' }}>
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <span style={{ fontSize: '10px', color: 'var(--text-mut)' }}>HORIZON</span>
        <span style={{ fontSize: '11px', fontWeight: 600 }}>{horizon}</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', textAlign: 'right' }}>
        <span style={{ fontSize: '10px', color: 'var(--text-mut)' }}>DATA CUTOFF</span>
        <span className="num" style={{ fontSize: '11px' }}>{cutoff}</span>
      </div>
    </div>
  </div>
);
