import axios from 'axios'

const normalizeApiBase = (value: string): string => value.replace(/\/+$/, '')

const getApiBase = (): string => {
  const configuredBase = import.meta.env.VITE_API_BASE_URL

  if (configuredBase && configuredBase.trim()) {
    return normalizeApiBase(configuredBase.trim())
  }

  if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
    return ''
  }

  return [window.location.protocol.replace(':', ''), '//', window.location.hostname || '127.0.0.1', ':8000'].join('')
}

export const API_BASE = getApiBase()
console.log('API_BASE configured as:', API_BASE || '(relative origin)')

export const API_KEY = (import.meta.env.VITE_API_KEY || '').trim()
export const API_HEADERS: Record<string, string> = API_KEY ? { 'X-API-Key': API_KEY } : {}

axios.defaults.withCredentials = true
axios.defaults.headers.common.Accept = 'application/json'

if (API_KEY) {
  axios.defaults.headers.common['X-API-Key'] = API_KEY
}

