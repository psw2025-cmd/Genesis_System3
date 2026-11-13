from pathlib import Path

path = Path("dashboard/frontend/src/components/workspaces/MultibaggerResearch.tsx")
content = path.read_text(encoding="utf-8")

# 1. Update imports
old_import = "import { resolveFeedQuality } from '../../lib/feedQuality'"
new_import = """import { humanizeContractReason, resolveFeedQuality } from '../../lib/feedQuality'

function humanizeSectionKey(key: string): string {
  const label = key.replace(/_/g, ' ').replace(/\\s+/g, ' ').trim().toLowerCase()
  if (!label) return 'Section'
  return label.charAt(0).toUpperCase() + label.slice(1)
}

function humanizeSectionValue(value: unknown): string {
  const raw = String(value ?? '').trim()
  if (!raw) return 'Not reported'
  if (/^pending$/i.test(raw)) return 'Waiting'
  if (/^ready|ok|pass$/i.test(raw)) return 'Ready'
  if (/^fail|failed|error$/i.test(raw)) return 'Needs attention'
  return raw.replace(/_/g, ' ')
}"""

assert old_import in content, "old_import not found"
content = content.replace(old_import, new_import, 1)

# 2. Update store destructuring
old_store = """    research, state, health, paper, pnl, marketOpen, wsStatus, brokerConnected,
  } = useStore()"""
new_store = """    research, state, health, paper, pnl, marketOpen, wsStatus, brokerConnected, setActiveTab,
  } = useStore()
  const [showCriteria, setShowCriteria] = useState<boolean>(false)
  const [showReadiness, setShowReadiness] = useState<boolean>(false)"""

assert old_store in content, "old_store not found"
content = content.replace(old_store, new_store, 1)

# 3. Add reason computation
old_calc = "  const lastFetch = formatIstStamp(state?.last_fetch_ts_iso || contract.as_of)"
new_calc = """  const lastFetch = formatIstStamp(state?.last_fetch_ts_iso || contract.as_of)
  const reason = humanizeContractReason(contract.reason || (error ? error : undefined))
  const sections = contract.sections && typeof contract.sections === 'object' ? contract.sections : {}
  const sectionEntries = Object.entries(sections)
  const marketLabel = marketOpen ? 'Open' : 'Closed'
  const researchFreshness = feed.label === 'Stale'
    ? 'Stale — waiting for a fresher research scan'
    : contract.status === 'stale'
      ? 'Research contract is stale'
      : totalCandidatesCount > 0
        ? 'Validated candidates available'
        : 'Waiting for the next validated scan'"""

assert old_calc in content, "old_calc not found"
content = content.replace(old_calc, new_calc, 1)

# 4. Replace empty state in table
old_empty = """              {!loading && displayedCandidates.length === 0 && (
                <tr>
                  <td colSpan={10} style={{ padding: '40px 16px', textAlign: 'center' }}>
                    <div style={{ maxWidth: 480, margin: '0 auto' }}>
                      <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-pri)', marginBottom: 6 }}>
                        No {activeHorizon === 'ALL' ? '' : activeHorizon} Candidates Currently Qualified
                      </div>
                      <p style={{ fontSize: 12, color: 'var(--text-sec)', lineHeight: 1.5, margin: 0 }}>
                        Stan Weinstein Stage-2 momentum, base breakout, and delivery volume expansion filters are active. During off-market hours or consolidation regimes, strict admission prevents false breakouts.
                      </p>
                      {activeHorizon !== 'ALL' && (
                        <button
                          onClick={() => setActiveHorizon('ALL')}
                          style={{ marginTop: 12, padding: '6px 14px', background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: 'pointer' }}
                        >
                          View All Candidates ({totalCandidatesCount})
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              )}"""

new_empty = """              {!loading && displayedCandidates.length === 0 && (
                <tr>
                  <td colSpan={10} style={{ padding: '30px 16px', textAlign: 'center' }}>
                    <div style={{ maxWidth: 540, margin: '0 auto', textAlign: 'left' }}>
                      <h2 className="section-title" style={{ fontSize: 16, marginBottom: 8, color: 'var(--text-pri)' }}>
                        No research candidates are ready
                      </h2>
                      <p className="empty-reason" style={{ fontSize: 13, color: 'var(--text-sec)', marginBottom: 12 }}>
                        {reason}
                      </p>
                      <dl className="empty-facts" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10, fontSize: 12, marginBottom: 16 }}>
                        <div>
                          <dt style={{ color: 'var(--text-mut)' }}>Last research scan</dt>
                          <dd className="num" style={{ fontWeight: 600 }}>{lastFetch}</dd>
                        </div>
                        <div>
                          <dt style={{ color: 'var(--text-mut)' }}>Market status</dt>
                          <dd style={{ fontWeight: 600 }}>{marketLabel}</dd>
                        </div>
                        <div>
                          <dt style={{ color: 'var(--text-mut)' }}>Research data</dt>
                          <dd style={{ fontWeight: 600 }}>{researchFreshness}</dd>
                        </div>
                        <div>
                          <dt style={{ color: 'var(--text-mut)' }}>Feed</dt>
                          <dd style={{ fontWeight: 600 }}>{feed.label} · {brokerIsConnected(health, brokerConnected) ? 'Broker connected' : 'Broker disconnected'}</dd>
                        </div>
                      </dl>

                      <div className="empty-actions" style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 14 }}>
                        <button
                          type="button"
                          className="btn-primary"
                          onClick={() => setActiveTab('data-integrity')}
                          style={{ padding: '6px 14px', background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: 'pointer' }}
                        >
                          View data status
                        </button>
                        <button
                          type="button"
                          className="btn-secondary"
                          onClick={() => setShowCriteria((v) => !v)}
                          aria-expanded={showCriteria}
                          style={{ padding: '6px 14px', background: 'var(--surface-3)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12, color: 'var(--text-pri)', cursor: 'pointer' }}
                        >
                          {showCriteria ? 'Hide how candidates are selected' : 'How candidates are selected'}
                        </button>
                      </div>

                      {showCriteria && (
                        <div className="criteria-panel" role="region" aria-label="How candidates are selected" style={{ padding: 12, background: 'var(--surface-3)', borderRadius: 6, marginBottom: 12 }}>
                          <p style={{ margin: '0 0 8px', fontSize: 12, color: 'var(--text-sec)' }}>
                            Candidates appear only when a producer supplies provenance-valid evidence. Stan Weinstein Stage-2 momentum, base breakout, and delivery volume expansion filters are applied.
                          </p>
                          <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--text-sec)', fontSize: 12, lineHeight: 1.5 }}>
                            <li>Identity: candidate id, symbol, and positive integral rank</li>
                            <li>Price: INR value from an approved source with a fresh observation time</li>
                            <li>Model: name, version, scoring method, and generation timestamp</li>
                            <li>Optional hash proof must be complete before evidence is marked ready</li>
                          </ul>
                        </div>
                      )}

                      <div className="readiness-details" style={{ marginTop: 10 }}>
                        <button
                          type="button"
                          className="btn-secondary"
                          onClick={() => setShowReadiness((v) => !v)}
                          aria-expanded={showReadiness}
                          style={{ padding: '6px 14px', background: 'var(--surface-3)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12, color: 'var(--text-pri)', cursor: 'pointer' }}
                        >
                          {showReadiness ? 'Hide research readiness details' : 'Research readiness details'}
                        </button>
                        {showReadiness && (
                          <div className="criteria-panel" role="region" aria-label="Research readiness details" style={{ marginTop: 8, padding: 12, background: 'var(--surface-3)', borderRadius: 6 }}>
                            <p style={{ margin: '0 0 8px', fontSize: 12, color: 'var(--text-mut)' }}>
                              Pipeline stages for operators. Collapsed by default so the research board stays readable.
                            </p>
                            <div className="section-chips" style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                              {sectionEntries.length > 0 ? (
                                sectionEntries.map(([key, value]) => (
                                  <span key={key} className="quiet-chip" style={{ fontSize: 11, padding: '2px 8px', background: 'var(--surface-2)', borderRadius: 4, border: '1px solid var(--border)' }}>
                                    {humanizeSectionKey(key)} · {humanizeSectionValue(value)}
                                  </span>
                                ))
                              ) : (
                                <span style={{ fontSize: 12, color: 'var(--text-mut)' }}>
                                  Pipeline: ingest · validate · rank · gate
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                </tr>
              )}"""

assert old_empty in content, "old_empty not found"
content = content.replace(old_empty, new_empty, 1)

duplicate_empty = """              {displayedCandidates.length === 0 && !loading && (
                <tr>
                  <td colSpan={10} style={{ textAlign: 'center', padding: 30, color: 'var(--text-mut)' }}>
                    No candidates found for {activeHorizon} horizon.
                  </td>
                </tr>
              )}"""
if duplicate_empty in content:
    content = content.replace(duplicate_empty, "", 1)

path.write_text(content, encoding="utf-8")
print("SUCCESSFULLY_UPDATED_MULTIBAGGER")
