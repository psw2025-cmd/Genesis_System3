export function AuthUnlock({ compact = false }: { compact?: boolean }) {
  return (
    <div
      data-testid="public-read-contract-error"
      role="status"
      className={compact ? 'space-y-2' : 'card p-4 border border-down/30 bg-down/5 space-y-2'}
    >
      {!compact && (
        <div className="text-xs text-text-muted uppercase tracking-wider">
          Public read contract error
        </div>
      )}
      <div className="text-sm text-text-primary font-semibold">
        This PAPER/ANALYZER dashboard must be readable without a dashboard key.
      </div>
      <div className="text-xs text-text-muted">
        A read endpoint returned an authentication-style error. Treat this as a backend/deployment regression; do not request or enter credentials here. LIVE remains OFF/LOCKED.
      </div>
    </div>
  )
}
