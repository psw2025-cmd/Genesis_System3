import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'

// Browser authentication is cookie-session only. The reusable API key is used
// once to establish the server-side HttpOnly session and is never persisted or
// replayed by frontend request interceptors.
axios.defaults.withCredentials = true

export function useAuth(){
  const[auth,setAuth]=useState({checked:false,authenticated:false})
  const check=useCallback(async()=>{
    try{
      const r=await fetch('/api/auth/status',{credentials:'include'})
      const d=await r.json().catch(()=>({}))
      setAuth({checked:true,authenticated:Boolean(d.authenticated)})
    } catch {
      setAuth({checked:true,authenticated:false})
    }
  },[])
  useEffect(()=>{check()},[check])
  const login=useCallback(()=>setAuth({checked:true,authenticated:true}),[])
  const logout=useCallback(async()=>{
    try{await fetch('/api/auth/logout',{method:'POST',credentials:'include'})}catch{}
    setAuth({checked:true,authenticated:false})
  },[])
  return{...auth,login,logout}
}
