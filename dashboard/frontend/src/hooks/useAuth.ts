import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
const KEY = 's3_api_key'
;(function patchAxios(){
  axios.interceptors.request.use(cfg=>{
    const k=sessionStorage.getItem(KEY)
    if(k && !cfg.headers['X-API-Key']) cfg.headers['X-API-Key']=k
    return cfg
  })
})()
;(function patchFetch(){
  const orig=window.fetch.bind(window)
  window.fetch=(input: RequestInfo|URL,init?: RequestInit)=>{
    const k=sessionStorage.getItem(KEY)
    if(k){const h=new Headers((init?.headers as HeadersInit)||{});if(!h.has('X-API-Key'))h.set('X-API-Key',k);return orig(input,{credentials:'include',...init,headers:h})}
    return orig(input,{credentials:'include',...init})
  }
})()
export function useAuth(){
  const[auth,setAuth]=useState({checked:false,authenticated:false})
  const check=useCallback(async()=>{
    try{const r=await fetch('/api/auth/status',{credentials:'include'});const d=await r.json().catch(()=>({}));setAuth({checked:true,authenticated:Boolean(d.authenticated)})}
    catch{setAuth({checked:true,authenticated:false})}
  },[])
  useEffect(()=>{check()},[check])
  const login=useCallback(()=>setAuth({checked:true,authenticated:true}),[])
  const logout=useCallback(async()=>{
    sessionStorage.removeItem(KEY)
    try{await fetch('/api/auth/logout',{method:'POST',credentials:'include'})}catch{}
    setAuth({checked:true,authenticated:false})
  },[])
  return{...auth,login,logout}
}