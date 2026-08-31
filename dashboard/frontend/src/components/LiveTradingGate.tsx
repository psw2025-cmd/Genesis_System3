import { useEffect, useMemo, useState } from "react"

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

interface ApprovalStatus {
  human_approval?: boolean
  approved_by?: string | null
  approved_utc?: string | null
  live_trading_env_flip_authorized?: boolean
  dashboard_reason?: string
}

interface HealthStatus {
  mode?: string
  live_allowed?: boolean
  live_trading_enabled?: boolean
  safety?: {
    execution_mode?: string
    live_trading_enabled?: boolean
  }
}

const LEGACY_LIVE_ARMING_GATE = "human_approved"
const NON_TECHNICAL_GATE_NAMES = new Set(["env_live_disabled", LEGACY_LIVE_ARMING_GATE])

function truthBadge(pass: boolean | null, yes: string, no: string, pending = "CHECKING") {
  if (pass === null) return { label: pending, color: "var(--amber)" }
  return { label: pass ? yes : no, color: pass ? "var(--up)" : "var(--amber)" }
}

export function LiveTradingGate() {
  const [status, setStatus] = useState<GateStatus | null>(null)
  const [approval, setApproval] = useState<ApprovalStatus | null>(null)
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const [gateResponse, approvalResponse, healthResponse] = await Promise.all([
          fetch("/api/live-trading/gate"),
          fetch("/api/approval/status"),
          fetch("/api/health"),
        ])
        if (!gateResponse.ok) throw new Error(`Gate proof unavailable (HTTP ${gateResponse.status})`)
        if (!approvalResponse.ok) throw new Error(`Owner approval proof unavailable (HTTP ${approvalResponse.status})`)
        if (!healthResponse.ok) throw new Error(`Execution mode proof unavailable (HTTP ${healthResponse.status})`)

        setStatus(await gateResponse.json())
        setApproval(await approvalResponse.json())
        setHealth(await healthResponse.json())
        setError(null)
      } catch (err: any) {
        setError(err?.message || "Execution truth unavailable")
      } finally {
        setLoading(false)
      }
    }

    load()
    const t = setInterval(load, 30000)
    return () => clearInterval(t)
  }, [])

  const legacyLiveArmingGate = useMemo(
    () => status?.gates?.find((g) => g.gate === LEGACY_LIVE_ARMING_GATE) ?? null,
    [status],
  )
  const technicalGates = useMemo(
    () => (status?.gates ?? []).filter((g) => !NON_TECHNICAL_GATE_NAMES.has(g.gate)),
    [status],
  )
  const technicalReady = status ? technicalGates.length > 0 && technicalGates.every((g) => g.passed) : null
  const ownerApproved = approval ? approval.human_approval === true : null
  const liveArmed = approval && legacyLiveArmingGate
    ? approval.live_trading_env_flip_authorized === true && legacyLiveArmingGate.passed === true
    : null
  const executionMode = String(health?.mode ?? health?.safety?.execution_mode ?? "UNKNOWN").toUpperCase()

  const ownerBadge = truthBadge(ownerApproved, "APPROVED", "PENDING")
  const readinessBadge = truthBadge(technicalReady, "PASSED", "PENDING")
  const armingBadge = truthBadge(liveArmed, "ARMED", "NOT ARMED")

  const truthCards = [
    {
      title: "Execution Mode",
      value: loading ? "CHECKING" : executionMode,
      color: executionMode === "LIVE" ? "var(--down)" : "var(--up)",
      detail: executionMode === "LIVE"
        ? "Real-order mode. Requires every independent live lock to be satisfied."
        : "PAPER/ANALYZER execution is separated from real-money LIVE arming.",
    },
    {
      title: "Owner Sign-off",
      value: ownerBadge.label,
      color: ownerBadge.color,
      detail: approval?.dashboard_reason ?? "Owner approval is read from /api/approval/status, not from the LIVE arming flag.",
    },
    {
      title: "Technical Readiness",
      value: readinessBadge.label,
      color: readinessBadge.color,
      detail: status
        ? `${technicalGates.filter((g) => g.passed).length}/${technicalGates.length} live-readiness technical checks passed.`
        : "Technical gate proof is loading.",
    },
    {
      title: "LIVE Arming",
      value: armingBadge.label,
      color: armingBadge.color,
      detail: liveArmed
        ? "Explicit LIVE arming is recorded. Runtime LIVE enablement is still a separate protected operation."
        : "Expected safe state for PAPER/ANALYZER. This is not the same as owner sign-off.",
    },
  ]

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      {error && (
        <div className="card p-4" style={{ color: "var(--down)" }}>
          {error}. LIVE trading remains locked.
        </div>
      )}

      <div className="card p-4" style={{ borderColor: status?.gate_open ? "var(--up)" : "var(--border)", borderWidth: "2px" }}>
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--text-pri)" }}>
              Execution Truth & Live Gate
            </h2>
            <p style={{ fontSize: ".75rem", color: "var(--text-mut)", marginTop: "4px" }}>
              Execution mode, owner sign-off, technical readiness and LIVE arming are independent truths.
            </p>
          </div>
          <div style={{
            padding: "8px 16px",
            borderRadius: "6px",
            fontWeight: 700,
            fontSize: ".8rem",
            fontFamily: "var(--font-mono)",
            background: status?.gate_open ? "var(--up)" : "var(--surface-3)",
            color: status?.gate_open ? "#000" : "var(--text-pri)",
          }}>
            {loading ? "CHECKING" : status?.verdict ?? "UNAVAILABLE"}
          </div>
        </div>
        <p style={{ marginTop: "8px", fontSize: ".75rem", color: "var(--text-mut)" }}>
          {status?.message ?? "Loading current live-gate proof..."}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
        {truthCards.map((item) => (
          <div key={item.title} className="card p-4" style={{ borderColor: item.color }}>
            <div style={{ fontSize: ".68rem", color: "var(--text-mut)", textTransform: "uppercase", fontWeight: 700 }}>
              {item.title}
            </div>
            <div style={{ marginTop: "6px", fontSize: "1rem", fontWeight: 800, color: item.color, fontFamily: "var(--font-mono)" }}>
              {item.value}
            </div>
            <div style={{ marginTop: "6px", fontSize: ".7rem", color: "var(--text-mut)", lineHeight: 1.4 }}>
              {item.detail}
            </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ overflow: "hidden" }}>
        <div style={{ padding: "8px 16px", borderBottom: "1px solid var(--border)", background: "var(--surface-2)" }}>
          <h3 style={{ fontSize: ".75rem", fontWeight: 700, color: "var(--text-pri)", textTransform: "uppercase" }}>
            Technical / Safety Preconditions
          </h3>
        </div>
        {technicalGates.map((g, i) => (
          <div key={`${g.gate}-${i}`} style={{
            padding: "12px 16px",
            borderBottom: "1px solid var(--border)",
            display: "flex",
            alignItems: "flex-start",
            gap: "12px",
          }}>
            <span style={{ fontSize: "1rem", flexShrink: 0 }}>{g.passed ? "✅" : "❌"}</span>
            <div>
              <div style={{
                fontSize: ".8rem",
                fontWeight: 600,
                color: g.passed ? "var(--up)" : "var(--down)",
                fontFamily: "var(--font-mono)",
              }}>
                {g.gate}
              </div>
              <div style={{ fontSize: ".7rem", color: "var(--text-mut)", marginTop: "2px" }}>{g.detail}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="card p-4" style={{ borderColor: "var(--border)" }}>
        <p style={{ fontSize: ".75rem", color: "var(--text-mut)" }}>
          This public Cloud Run dashboard is read-only. Owner sign-off already recorded for development/PAPER operation does not arm real-money execution. LIVE arming and the protected runtime LIVE enablement remain separate controls.
        </p>
      </div>

      <div className="card p-4" style={{ borderColor: "var(--surface-3)" }}>
        <p style={{ fontSize: ".7rem", color: "var(--text-mut)" }}>
          <strong>Real-money LIVE execution remains OFF</strong> unless technical readiness passes, owner sign-off is present, explicit LIVE arming is recorded, and the protected Cloud Run operation enables LIVE. Max daily loss protection remains independent.
        </p>
      </div>
    </div>
  )
}
