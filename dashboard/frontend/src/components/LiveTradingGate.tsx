import { useState, useEffect } from "react"
import { cn } from "../lib/utils"

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
  const [approving, setApproving] = useState(false)
  const [phrase, setPhrase] = useState("")
  const [approvalResult, setApprovalResult] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const r = await fetch("/api/live-trading/gate")
        setStatus(await r.json())
      } catch { /* network error */ }
      finally { setLoading(false) }
    }
    load()
    const t = setInterval(load, 30000)
    return () => clearInterval(t)
  }, [])

  const handleApprove = async () => {
    setApproving(true)
    try {
      const r = await fetch("/api/live-trading/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ approval_phrase: phrase })
      })
      const d = await r.json()
      setApprovalResult(d.message)
    } catch (e) {
      setApprovalResult("Error: " + e)
    } finally { setApproving(false) }
  }

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      {/* Header */}
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

      {status?.gates?.every(g => g.gate !== "human_approved" || !g.passed) &&
       status?.gates?.filter(g => g.gate !== "human_approved").every(g => g.passed) && (
        <div className="card p-4" style={{ borderColor: "var(--up)" }}>
          <h3 style={{ fontSize: ".8rem", fontWeight: 700, color: "var(--up)",
                       marginBottom: "12px" }}>
            🔓 All Technical Gates Passed — Human Approval Required
          </h3>
          <p style={{ fontSize: ".75rem", color: "var(--text-mut)", marginBottom: "12px" }}>
            Type the exact approval phrase to record your consent. This does NOT
            enable live trading automatically — you must also change
            LIVE_TRADING_ENABLED=1 manually on Render dashboard.
          </p>
          <input
            value={phrase}
            onChange={e => setPhrase(e.target.value)}
            placeholder="I APPROVE LIVE TRADING WITH MAX LOSS RS 5000"
            style={{
              width: "100%", padding: "8px 12px", borderRadius: "6px",
              background: "var(--surface-2)", border: "1px solid var(--border)",
              color: "var(--text-pri)", fontSize: ".75rem",
              fontFamily: "var(--font-mono)", marginBottom: "8px"
            }}
          />
          <button
            onClick={handleApprove}
            disabled={approving || !phrase.trim()}
            style={{
              padding: "8px 20px", borderRadius: "6px", fontWeight: 700,
              fontSize: ".75rem", cursor: "pointer",
              background: approving ? "var(--surface-3)" : "var(--up)",
              color: "#000", border: "none"
            }}
          >
            {approving ? "Recording..." : "Record Approval"}
          </button>
          {approvalResult && (
            <p style={{ fontSize: ".75rem", color: "var(--amber)", marginTop: "8px" }}>
              {approvalResult}
            </p>
          )}
        </div>
      )}

      {/* Always visible warning */}
      <div className="card p-4" style={{ borderColor: "var(--surface-3)" }}>
        <p style={{ fontSize: ".7rem", color: "var(--text-mut)" }}>
          <strong>Live trading remains OFF</strong> until all gates pass,
          human approval is recorded, AND LIVE_TRADING_ENABLED is manually
          set to 1 on Render. Max daily loss: ₹5,000.
          System halts automatically when limit is hit.
        </p>
      </div>
    </div>
  )
}
