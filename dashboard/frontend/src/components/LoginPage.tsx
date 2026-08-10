import { useState } from 'react'
interface Props { onLogin: () => void }
export function LoginPage({ onLogin }: Props) {
  const [key, setKey] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!key.trim()) return
    setLoading(true); setError('')
    try {
      const r = await fetch('/api/auth/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': key.trim() },
        credentials: 'include',
      })
      const d = await r.json().catch(() => ({}))
      if (r.ok && d.authenticated) {
        sessionStorage.setItem('s3_api_key', key.trim()); onLogin()
      } else {
        setError(d.detail || d.message || 'Invalid API key — check and retry.')
      }
    } catch { setError('Connection failed.') }
    finally { setLoading(false) }
  }
  const ok = !loading && key.trim().length >= 32
  return (
    <div style={{minHeight:"100vh",background:"#070b14",display:"flex",alignItems:"center",justifyContent:"center",fontFamily:"monospace"}}>
      <div style={{background:"#0f172a",border:"1px solid #1e3a5f",borderRadius:12,padding:"40px 36px",width:400,maxWidth:"90vw"}}>
        <div style={{textAlign:"center",marginBottom:32}}>
          <div style={{fontSize:26,fontWeight:800,color:"#60a5fa",letterSpacing:6}}>SYSTEM3</div>
          <div style={{fontSize:11,color:"#4b5563",letterSpacing:3,marginTop:4}}>AI OPTIONS CONTROL</div>
          <div style={{width:36,height:2,background:"#2563eb",margin:"14px auto 0"}} />
        </div>
        <form onSubmit={submit}>
          <div style={{marginBottom:18}}>
            <label style={{display:"block",fontSize:10,color:"#6b7280",letterSpacing:2,marginBottom:8}}>DASHBOARD API KEY</label>
            <input type="password" value={key} onChange={e=>setKey(e.target.value)}
              placeholder="Enter your 64-character API key" autoFocus
              style={{width:"100%",padding:"11px 12px",background:"#0a0e1a",border:"1px solid #1e3a5f",borderRadius:6,color:"#e2e8f0",fontSize:13,fontFamily:"inherit",outline:"none",boxSizing:"border-box"}} />
          </div>
          {error && <div style={{background:"#1a0808",border:"1px solid #7f1d1d",borderRadius:6,padding:"9px 12px",color:"#fca5a5",fontSize:11,marginBottom:14}}>{error}</div>}
          <button type="submit" disabled={!ok}
            style={{width:"100%",padding:11,marginTop:8,background:ok?"#1d4ed8":"#1e293b",color:ok?"#fff":"#4b5563",border:"none",borderRadius:6,fontSize:12,fontWeight:700,letterSpacing:3,cursor:ok?"pointer":"not-allowed"}}>
            {loading ? "AUTHENTICATING…" : "ACCESS DASHBOARD"}
          </button>
        </form>
        <div style={{marginTop:24,padding:"10px 12px",background:"#070b14",borderRadius:6,fontSize:10,color:"#374151",textAlign:"center",letterSpacing:1}}>
          PAPER MODE · LIVE TRADING OFF · SESSION 12 HRS
        </div>
      </div>
    </div>
  )
}