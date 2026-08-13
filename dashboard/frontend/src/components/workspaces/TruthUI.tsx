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

export const StatusChip: React.FC<StatusChipProps> = ({ label, status = 'mut', value }) => {
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
  title?: string;
  tone?: 'warn' | 'mut';
}

export const PENDINGState: React.FC<PENDINGStateProps> = ({
  reason = 'DATA SERVICE PENDING',
  dataTestId,
  title,
  tone = 'warn',
}) => {
  const warn = tone === 'warn'
  return (
    <div
      data-testid={dataTestId}
      role="status"
      style={{
        padding: '24px',
        textAlign: 'center',
        background: warn ? 'rgba(245, 158, 11, 0.05)' : 'rgba(88, 112, 141, 0.08)',
        border: warn ? '1px dashed var(--amber)' : '1px dashed var(--border)',
        borderRadius: '8px',
        color: warn ? 'var(--amber)' : 'var(--text-sec)',
        fontSize: '12px',
        fontWeight: 600,
        letterSpacing: '0.05em',
      }}
    >
      <div style={{ marginBottom: '8px', textTransform: 'uppercase' }}>
        {title || (warn ? '⚠️ PENDING' : 'NO VERIFIED CONTRACT')}
      </div>
      <div style={{ textTransform: 'none', fontWeight: 500, color: 'var(--text-sec)' }}>{reason}</div>
    </div>
  )
}

export const MetricTile: React.FC<{
  label: string
  value: string
  sub?: string
  tone?: 'ok' | 'warn' | 'error' | 'mut'
}> = ({ label, value, sub, tone = 'mut' }) => {
  const color = tone === 'ok' ? 'var(--up)' : tone === 'warn' ? 'var(--amber)' : tone === 'error' ? 'var(--down)' : 'var(--text-pri)'
  return (
    <div className="card" style={{ padding: '14px 16px' }}>
      <div className="metric-label">{label}</div>
      <div className="num" style={{ marginTop: 6, fontSize: '1.15rem', fontWeight: 800, color }}>{value}</div>
      {sub ? <div style={{ marginTop: 4, fontSize: 11, color: 'var(--text-mut)' }}>{sub}</div> : null}
    </div>
  )
}

interface EvidenceProps {
  label: string;
  items: string[];
  type: 'pro' | 'con';
}

export const EvidenceList: React.FC<EvidenceProps> = ({ label, items, type }) => (
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
