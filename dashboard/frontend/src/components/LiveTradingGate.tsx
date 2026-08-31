import { useEffect, useMemo, useState } from "react"

interface AutoGate {
  gate_id?: string
  pass?: boolean
  status?: string
  note?: string
  blocker_id?: string | null
  auto_action?: string
}

interface AutoGateStatus {
  gates?: Record<string, AutoGate>
  gates_passing?: number
  gates_total?: number
  production_live_ready?: boolean
  technical_gates_still_required?: string[]
  open_blockers?: string[]
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
  live_blockers?: string[]
  safety?: {
    execution_mode?: string
    live_trading_enabled?: boolean
  }
}

function truthBadge(pass: boolean | null, yes: string, no: string, pending = "CHECKING") {
  if (pass === null) return { label: pending, color: "var(--amber)" }
  return { label: pass ? yes : no, color: pass ? "var(--up)" : "var(--amber)" }
}

export function LiveTradingGate() {
  const [autoGates, setAutoGates] = useState<AutoGateStatus | null>(null)
  const [approval, setApproval] = useState<ApprovalStatus | null>(null)
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const [autoGateResponse, approvalResponse, healthResponse] = await Promise.all([
          fetch("/api/auto_gates"),
          fetch("/api/approval/status"),
          fetch("/api/health"),
        ])
        if (!autoGateResponse.ok) throw new Error(`Technical readiness proof unavailable (HTTP ${autoGateResponse.status})`)
        if (!approvalResponse.ok) throw new Error(`Owner approval proof unavailable (HTTP ${approvalResponse.status})`)
        if (!healthResponse.ok) throw new Error(`Execution mode proof unavailable (HTTP ${healthResponse.status})`)

        setAutoGates(await autoGateResponse.json())
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

  const technicalGates = useMemo(
    () => Object.entries(autoGates?.gates ?? {}).map(([name, gate]) => ({
      name,
      passed: gate.pass === true,
      detail: gate.note ?? gate.auto_action ?? gate.blocker_id ?? "No detail supplied",
      blocker: gate.blocker_id ?? null,
    })),
    [autoGates],
  )

  const technicalReady = autoGates
    ? autoGates.production_live_ready === true || (
        Number(autoGates.gates_total ?? 0) > 0 &&
        Number(autoGates.gates_passing ?? 0) === Number(autoGates.gates_total ?? 0)
      )
    : null
  const ownerApproved = approval ? approval.human_approval === true : null
  const liveArmed = approval ? approval.live_trading_env_flip_authorized === true : null
  const runtimeLiveEnabled = Boolean(health?.live_trading_enabled ?? health?.safety?.live_trading_enabled ?? health?.live_allowed)
  const executionMode = String(health?.mode ?? health?.safety?.execution_mode ?? "UNKNOWN").toUpperCase()

  const ownerBadge = truthBadge(ownerApproved, "APPROVED", "PENDING")
  const readinessBadge = truthBadge(technicalReady, "PASSED", "NOT READY")
  const armingBadge = truthBadge(liveArmed, "ARMED", "NOT ARMED")
  const overallLabel = runtimeLiveEnabled
    ? "LIVE ENABLED"
    : technicalReady
      ? "PAPER · LIVE TECH READY"
      : "PAPER · LIVE NOT READY"

  const truthCards = [
    {
      title: "Execution Mode",
      value: loading ? "CHECKING" : executionMode,
      color: runtimeLiveEnabled ? "var(--down)" : "var(--up)",
      detail: runtimeLiveEnabled
        ? "Real-order runtime is enabled. All independent locks must remain satisfied."
        : "PAPER/ANALYZER runtime is active; broker order placement remains separate and locked.",
    },
    {
      title: "Owner Sign-off",
      value: ownerBadge.label,
      color: ownerBadge.color,
      detail: approval?.dashboard_reason ?? "Owner approval is read only from /api/approval/status.",
    },
    {
      title: "Technical Readiness",
      value: readinessBadge.label,
      color: readinessBadge.color,
      detail: autoGates
        ? `${autoGates.gates_passing ?? 0}/${autoGates.gates_total ?? 0} canonical auto-gates passed${(autoGates.open_blockers ?? []).length ? ` · blockers: ${(autoGates.open_blockers ?? []).join(", ")}` : ""}.`
        : "Canonical /api/auto_gates proof is loading.",
    },
    {
      title: "LIVE Arming",
      value: armingBadge.label,
      color: armingBadge.color,
      detail: liveArmed
        ? `Owner LIVE arming authorization is recorded. Runtime LIVE enabled=${String(runtimeLiveEnabled)}.`
        : "Expected safe state for PAPER/ANALYZER. This is independent of owner development/PAPER sign-off.",
    },
  ]

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      {error && (
        <div className="card p-4" style={{ color: "var(--down)" }}>
          {error}. Real-money LIVE execution remains locked.
        </div>
      )}

      <div className="card p-4" style={{ borderColor: runtimeLiveEnabled ? "var(--down)" : "var(--border)", borderWidth: "2px" }}>
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--text-pri)" }}>
              Execution Truth & Live Gate
            </h2>
            <p style={{ fontSize: ".75rem", color: "var(--text-mut)", marginTop: "4px" }}>
              Execution mode, owner sign-off, technical readiness and LIVE arming are four independent truths.
            </p>
          </div>
          <div style={{
            padding: "8px 16px",
            borderRadius: "6px",
            fontWeight: 700,
            fontSize: ".8rem",
            fontFamily: "var(--font-mono)",
            background: runtimeLiveEnabled ? "var(--down)" : "var(--surface-3)",
            color: runtimeLiveEnabled ? "#000" : "var(--text-pri)",
          }}>
            {loading ? "CHECKING" : overallLabel}
          </div>
        </div>
        <p style={{ marginTop: "8px", fontSize: ".75rem", color: "var(--text-mut)" }}>
          Technical readiness comes from the canonical auto-gate evaluator; owner sign-off and LIVE arming are never inferred from each other.
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
            Canonical Technical Readiness Gates
          </h3>
        </div>
        {technicalGates.map((g, i) => (
          <div key={`${g.name}-${i}`} style={{
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
                {g.name}
              </div>
              <div style={{ fontSize: ".7rem", color: "var(--text-mut)", marginTop: "2px" }}>
                {g.detail}{g.blocker ? ` · blocker=${g.blocker}` : ""}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="card p-4" style={{ borderColor: "var(--border)" }}>
        <p style={{ fontSize: ".75rem", color: "var(--text-mut)" }}>
          This public Cloud Run dashboard is read-only. Existing owner sign-off covers development/PAPER operation; it does not authorize or enable real-money execution. Explicit LIVE arming and protected runtime LIVE enablement remain separate controls.
        </p>
      </div>
    </div>
  )
}
