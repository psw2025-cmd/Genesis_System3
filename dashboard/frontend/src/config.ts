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

// Sent on every request via axios's shared global instance (all components
// import the default `axios` export, none create a local instance). No-op
// until the backend has REQUIRE_API_KEY=true and a matching API_KEY set -
// see the comment in dashboard/backend/app.py next to _enforce_api_key.
const apiKey = import.meta.env.VITE_API_KEY
if (apiKey && apiKey.trim()) {
  axios.defaults.headers.common['X-API-Key'] = apiKey.trim()
}
