import { useState, useEffect } from "react"

interface Gate {
  gate: string
  passed: boolean
  detail: string
}

interface GateStatus {
  gate_open: boolean
  gates: Gate[]
  summary: string
  verdict: string
  message: string
}

export function LiveTradingGate() {
  const [status, setStatus] = useState<GateStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const r = await fetch("/api/live-trading/gate")
        if (!r.ok) throw new Error(`Gate proof unavailable (HTTP ${r.status})`)
        setStatus(await r.json()); setError(null)
      } catch (err: any) { setError(err?.message || 'Gate proof unavailable') }
      finally { setLoading(false) }
    }
    load()
    const t = setInterval(load, 30000)
    return () => clearInterval(t)
  }, [])

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      {/* Header */}
      {error && <div className="card p-4" style={{ color: 'var(--down)' }}>{error}. Live trading remains locked.</div>}
      <div className="card p-4" style={{
        borderColor: status?.gate_open ? "var(--up)" : "var(--down)",
        borderWidth: "2px"
      }}>
        <div className="flex items-center justify-between">
          <div>
            <h2 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--text-pri)" }}>
              Live Trading Gate
            </h2>
            <p style={{ fontSize: ".75rem", color: "var(--text-mut)", marginTop: "4px" }}>
              {loading ? "Checking..." : status?.summary ?? "—"}
            </p>
          </div>
          <div style={{
            padding: "8px 16px", borderRadius: "6px", fontWeight: 700,
            fontSize: ".8rem", fontFamily: "var(--font-mono)",
            background: status?.gate_open ? "var(--up)" : "var(--down)",
            color: "#000"
          }}>
            {status?.verdict ?? "CHECKING"}
          </div>
        </div>
        <p style={{
          marginTop: "8px", fontSize: ".75rem",
          color: status?.gate_open ? "var(--up)" : "var(--amber)"
        }}>
          {status?.message}
        </p>
      </div>

      {/* Gate checklist */}
      <div className="card" style={{ overflow: "hidden" }}>
        <div style={{ padding: "8px 16px", borderBottom: "1px solid var(--border)",
                      background: "var(--surface-2)" }}>
          <h3 style={{ fontSize: ".75rem", fontWeight: 700, color: "var(--text-pri)",
                       textTransform: "uppercase" }}>
            Gate Checklist
          </h3>
        </div>
        {(status?.gates ?? []).map((g, i) => (
          <div key={i} style={{
            padding: "12px 16px", borderBottom: "1px solid var(--border)",
            display: "flex", alignItems: "flex-start", gap: "12px"
          }}>
            <span style={{ fontSize: "1rem", flexShrink: 0 }}>
              {g.passed ? "✅" : "❌"}
            </span>
            <div>
              <div style={{ fontSize: ".8rem", fontWeight: 600,
                            color: g.passed ? "var(--up)" : "var(--down)",
                            fontFamily: "var(--font-mono)" }}>
                {g.gate}
              </div>
              <div style={{ fontSize: ".7rem", color: "var(--text-mut)", marginTop: "2px" }}>
                {g.detail}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Approval section — only show when all technical gates pass */}
      {status && !status.gate_open && (
        <div className="card p-4" style={{ borderColor: "var(--amber)" }}>
          <p style={{ fontSize: ".8rem", color: "var(--amber)", fontWeight: 600 }}>
            ⚠️ Gates not yet passed
          </p>
          <p style={{ fontSize: ".75rem", color: "var(--text-mut)", marginTop: "6px" }}>
            All technical gates must pass before the approval section appears.
            Continue running in PAPER mode to accumulate proof data.
          </p>
        </div>
      )}

      <div className="card p-4" style={{ borderColor: "var(--border)" }}><p style={{ fontSize: '.75rem', color: 'var(--text-mut)' }}>This public Cloud Run dashboard is read-only. Approval and configuration changes are intentionally unavailable here.</p></div>

      {/* Always visible warning */}
      <div className="card p-4" style={{ borderColor: "var(--surface-3)" }}>
        <p style={{ fontSize: ".7rem", color: "var(--text-mut)" }}>
          <strong>Live trading remains OFF</strong> until all gates pass,
          human approval is recorded, AND LIVE_TRADING_ENABLED is manually
          set to 1 through the protected Cloud Run operations workflow. Max daily loss: ₹5,000.
          System halts automatically when limit is hit.
        </p>
      </div>
    </div>
  )
}
