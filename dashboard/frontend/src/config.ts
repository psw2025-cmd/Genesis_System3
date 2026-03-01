// API Configuration - Auto-detect backend URL
const getApiBase = (): string => {
  // Check if running in Electron (file:// protocol)
  const isElectron = window.location.protocol === 'file:' || 
                     (window as any).electronAPI !== undefined ||
                     navigator.userAgent.includes('Electron')
  
  // In Electron or file:// protocol, ALWAYS use localhost:8000 for backend
  if (isElectron || window.location.protocol === 'file:') {
    return 'http://localhost:8000'
  }
  
  // Use the same hostname as the frontend for backend
  const hostname = window.location.hostname
  const protocol = window.location.protocol
  
  // If localhost, use localhost for backend
  if (hostname === 'localhost' || hostname === '127.0.0.1' || !hostname || hostname === '') {
    return 'http://localhost:8000'
  }
  
  // If network IP, use same IP for backend (but ensure http:// protocol)
  if (protocol === 'http:' || protocol === 'https:') {
    return `${protocol}//${hostname}:8000`
  }
  
  // Fallback: always use localhost:8000
  return 'http://localhost:8000'
}

export const API_BASE = getApiBase()

// Debug logs (suppress in production via VITE_DEBUG=0)
export const DEBUG = import.meta.env.VITE_DEBUG !== '0'
if (DEBUG) {
  console.log('API_BASE:', API_BASE)
}