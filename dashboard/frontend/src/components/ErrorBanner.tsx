import { AlertTriangle, RefreshCw, Shield } from 'lucide-react'

interface ErrorBannerProps {
  endpoint: string
  status?: number | null
  message: string
  onRetry?: () => void
}

export default function ErrorBanner({ endpoint, status, message, onRetry }: ErrorBannerProps) {
  return (
    <div className="card" style={{
      padding: 12,
      marginBottom: 10,
      borderColor: 'rgba(245,165,36,.34)',
      background: 'linear-gradient(90deg, rgba(245,165,36,.07), rgba(7,18,31,.92) 42%)',
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
        <div style={{ width: 34, height: 34, display: 'grid', placeItems: 'center', borderRadius: 9, flexShrink: 0, color: 'var(--amber)', border: '1px solid rgba(245,165,36,.26)', background: 'rgba(245,165,36,.07)' }}>
          <AlertTriangle size={16} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ color: 'var(--amber)', fontSize: '.68rem', fontWeight: 850 }}>DEGRADED READ-ONLY DATA</span>
            {status && <span className="pill" style={{ color: 'var(--down)', border: '1px solid rgba(255,73,100,.22)', background: 'rgba(255,73,100,.05)' }}>HTTP {status}</span>}
            <span className="pill" style={{ color: 'var(--up)', border: '1px solid rgba(24,215,130,.20)', background: 'rgba(24,215,130,.04)' }}><Shield size={10} /> LIVE OFF</span>
          </div>
          <div style={{ marginTop: 6, display: 'grid', gridTemplateColumns: 'minmax(170px, .7fr) minmax(0, 2fr)', gap: 10, alignItems: 'start' }}>
            <div>
              <div className="metric-label">Endpoint</div>
              <div className="num" style={{ marginTop: 3, color: 'var(--text-sec)', fontSize: '.58rem', overflowWrap: 'anywhere' }}>{endpoint}</div>
            </div>
            <div>
              <div className="metric-label">Runtime message</div>
              <div style={{ marginTop: 3, color: 'var(--text-sec)', fontSize: '.6rem', lineHeight: 1.45 }}>{message}</div>
            </div>
          </div>
        </div>
        {onRetry && (
          <button onClick={onRetry} className="soft-btn" style={{ flexShrink: 0 }}>
            <RefreshCw size={12} /> Retry
          </button>
        )}
      </div>
    </div>
  )
}
