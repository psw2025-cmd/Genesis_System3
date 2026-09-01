// CREATED_BY=unknown-original | LAST_EDITED_BY=Codex | TASK_OR_ISSUE=#442 | CHANGE_NOTE=Fail closed when local deploy identity is absent
import { useStore } from '../store'
import { formatIstStamp } from '../lib/formatLive'
import { safeDeployTruth } from '../lib/dashboardTruth'

export function DeploymentTruthFooter() {
  const { deployInfo, health, marketOpen, lastSync } = useStore()
  const deploy = safeDeployTruth(deployInfo)

  return (
    <footer data-testid="deployment-truth-footer" style={{ flexShrink: 0, display: 'flex', flexWrap: 'wrap', gap: '8px 20px', justifyContent: 'space-between', alignItems: 'center', padding: '6px 14px', borderTop: '1px solid rgba(59, 140, 255, 0.22)', background: 'linear-gradient(180deg, rgba(5,12,22,.92), rgba(3,8,16,.98))', fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-mut)' }}>
      <span>
        Deploy truth · {deploy.target} · {deploy.region} · SHA{' '}
        <strong style={{ color: deploy.proven ? 'var(--accent-2)' : 'var(--amber)' }}>{deploy.shortSha}</strong>
        {deploy.sha.length > 8 ? ` (${deploy.sha})` : ''}
      </span>
      <span>
        Market {marketOpen ? 'OPEN' : 'CLOSED'} · Sync {formatIstStamp(lastSync)} · Health QC {String(health?.qc_status || health?.qc?.status || '—')} · LIVE {deployInfo?.live_trading_enabled ? 'ON' : 'OFF'}
      </span>
    </footer>
  )
}
