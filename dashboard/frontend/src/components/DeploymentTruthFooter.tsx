import { useStore } from '../store'
import { shortSha, formatIstStamp } from '../lib/formatLive'

export function DeploymentTruthFooter() {
  const { deployInfo, health, marketOpen, lastSync } = useStore()
  const sha = String(deployInfo?.git_sha || '')
  const target = String(deployInfo?.deploy_target || 'unknown')
  const region = String(deployInfo?.region || 'asia-south1')

  return (
    <footer
      data-testid="deployment-truth-footer"
      style={{
        flexShrink: 0,
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px 20px',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '6px 14px',
        borderTop: '1px solid rgba(59, 140, 255, 0.22)',
        background: 'linear-gradient(180deg, rgba(5,12,22,.92), rgba(3,8,16,.98))',
        fontFamily: 'var(--font-mono)',
        fontSize: 10,
        color: 'var(--text-mut)',
      }}
    >
      <span>
        Deploy truth · {target} · {region} · SHA{' '}
        <strong style={{ color: 'var(--accent-2)' }}>{shortSha(sha)}</strong>
        {sha.length > 8 ? ` (${sha})` : ''}
      </span>
      <span>
        Market {marketOpen ? 'OPEN' : 'CLOSED'}
        {' · '}
        Sync {formatIstStamp(lastSync)}
        {' · '}
        Health QC {String(health?.qc_status || health?.qc?.status || '—')}
        {' · '}
        LIVE {deployInfo?.live_trading_enabled ? 'ON' : 'OFF'}
      </span>
    </footer>
  )
}
