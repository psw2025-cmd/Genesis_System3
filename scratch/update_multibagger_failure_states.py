from pathlib import Path

p = Path("dashboard/frontend/src/components/workspaces/MultibaggerResearch.tsx")
text = p.read_text(encoding="utf-8")

# 1. Add error state to MultibaggerResearch
old_state = """  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [activeHorizon, setActiveHorizon] = useState<HorizonType>('ALL')"""

new_state = """  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [activeHorizon, setActiveHorizon] = useState<HorizonType>('ALL')"""

# 2. Update fetchMultibagger with error handling
old_fetch = """  const fetchMultibagger = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/multibagger', {
        credentials: 'include',
        headers: { Accept: 'application/json', ...API_HEADERS },
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = await res.json()
      const ranked = rankMultibagger(json, useStore.getState().research)
      setData(ranked.value)
      if (Array.isArray(ranked.value?.candidates) && ranked.value.candidates.length > 0) {
        useStore.getState().setResearch(ranked.value)
      }
    } catch (err) {
      console.warn('Failed to fetch /api/multibagger:', err)
    } finally {
      setLoading(false)
    }
  }"""

new_fetch = """  const fetchMultibagger = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/multibagger', {
        credentials: 'include',
        headers: { Accept: 'application/json', ...API_HEADERS },
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}: Multibagger Research API offline`)
      const json = await res.json()
      const ranked = rankMultibagger(json, useStore.getState().research)
      setData(ranked.value)
      if (Array.isArray(ranked.value?.candidates) && ranked.value.candidates.length > 0) {
        useStore.getState().setResearch(ranked.value)
      }
    } catch (err: any) {
      console.warn('Failed to fetch /api/multibagger:', err)
      setError(err?.message || 'Multibagger research feed temporarily unavailable')
    } finally {
      setLoading(false)
    }
  }"""

# 3. Add error banner before the table
old_section = """        {/* Candidates Table */}
        <section className="elevated-panel" style={{ padding: 20, overflowX: 'auto', background: 'var(--surface-2)', borderRadius: 8, border: '1px solid var(--border)' }}>"""

new_section = """        {error && (
          <div style={{ padding: '14px 18px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontWeight: 700, color: '#ef4444', fontSize: 13 }}>Research Service Notice</div>
              <div style={{ fontSize: 12, color: 'var(--text-sec)', marginTop: 2 }}>{error}. Showing cached research universe baseline.</div>
            </div>
            <button onClick={fetchMultibagger} disabled={loading} style={{ padding: '6px 14px', background: 'var(--surface-3)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12, cursor: 'pointer', color: 'var(--text-pri)', fontWeight: 600 }}>
              {loading ? 'Retrying...' : 'Retry'}
            </button>
          </div>
        )}

        {/* Candidates Table */}
        <section className="elevated-panel" style={{ padding: 20, overflowX: 'auto', background: 'var(--surface-2)', borderRadius: 8, border: '1px solid var(--border)' }}>"""

# 4. Update tbody to render loading & human-friendly empty states
old_tbody = """            <tbody>
              {displayedCandidates.map((row, idx) => {"""

new_tbody = """            <tbody>
              {loading && displayedCandidates.length === 0 && (
                <tr>
                  <td colSpan={10} style={{ padding: '36px 12px', textAlign: 'center', color: 'var(--text-sec)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                      <RefreshCw size={16} className="animate-spin" />
                      <span>Scanning Multi-Horizon Research Universe...</span>
                    </div>
                  </td>
                </tr>
              )}
              {!loading && displayedCandidates.length === 0 && (
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
              )}
              {displayedCandidates.map((row, idx) => {"""

if old_state in text and old_fetch in text and old_section in text and old_tbody in text:
    text = text.replace(old_state, new_state, 1)
    text = text.replace(old_fetch, new_fetch, 1)
    text = text.replace(old_section, new_section, 1)
    text = text.replace(old_tbody, new_tbody, 1)
    p.write_text(text, encoding="utf-8")
    print("Multibagger failure states implemented successfully")
else:
    print("Could not match all blocks in MultibaggerResearch.tsx")
