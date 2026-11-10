import axios from 'axios'

export const DASHBOARD_URL = 'http://127.0.0.1:3000'
const LOCAL_API_BASE = 'http://127.0.0.1:8000'

const normalizeApiBase = (value: string): string => value.replace(/\/+$/, '')

const getApiBase = (): string => {
  const configuredBase = import.meta.env.VITE_API_BASE_URL

  if (configuredBase && configuredBase.trim()) {
    const base = normalizeApiBase(configuredBase.trim())
    // Hard-block legacy Render hosts so DNS failures cannot return.
    if (/onrender\.com/i.test(base)) {
      console.warn('Ignoring legacy Render VITE_API_BASE_URL; using local loopback API host')
      return LOCAL_API_BASE
    }
    return base
  }

  if (
    window.location.hostname === '127.0.0.1'
    || window.location.hostname === 'localhost'
  ) {
    if (window.location.port === '3000') {
      return LOCAL_API_BASE
    }
    if (window.location.port === '8000') {
      return ''
    }
  }

  if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
    return ''
  }

  return [window.location.protocol.replace(':', ''), '//', window.location.hostname || '127.0.0.1', ':8000'].join('')
}

export const API_BASE = getApiBase()
console.log('API_BASE configured as:', API_BASE || '(relative origin)')

// Authentication is established through the server-side HttpOnly session
// endpoint. Never compile a reusable API key into browser JavaScript.
export const API_HEADERS: Record<string, string> = {}

axios.defaults.withCredentials = true
axios.defaults.headers.common.Accept = 'application/json'
