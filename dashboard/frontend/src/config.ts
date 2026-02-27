// API Configuration - Auto-detect backend URL
const getApiBase = (): string => {
  // Check if running in Electron (file:// protocol)
  const isElectron = window.location.protocol === 'file:' || 
                     (window as any).electronAPI !== undefined ||
                     navigator.userAgent.includes('Electron')
  
  // In Electron or file:// protocol, ALWAYS use localhost:8000 for backend
  if (isElectron || window.location.protocol === 'file:') {
    const apiBase = 'http://localhost:8000'
    console.log('Electron detected - using API_BASE:', apiBase)
    return apiBase
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
  console.warn('Unknown protocol, defaulting to localhost:8000')
  return 'http://localhost:8000'
}

export const API_BASE = getApiBase()

// Log for debugging
console.log('API_BASE configured as:', API_BASE)
console.log('Window location:', window.location.href)
console.log('Protocol:', window.location.protocol)
console.log('Running in Electron:', window.location.protocol === 'file:' || (window as any).electronAPI !== undefined)