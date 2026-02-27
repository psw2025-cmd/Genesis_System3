/**
 * Preload script for Electron
 * Exposes safe APIs to renderer process
 */
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // Backend control
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
  controlBackend: (action) => ipcRenderer.invoke('control-backend', action),
  
  // Agent memory
  getAgentMemory: () => ipcRenderer.invoke('get-agent-memory'),
  saveAgentMemory: (tasks) => ipcRenderer.invoke('save-agent-memory', tasks),
  
  // Notifications
  showNotification: (options) => ipcRenderer.invoke('show-notification', options),
  
  // Proof pack
  downloadProofPack: () => ipcRenderer.invoke('download-proof-pack'),
  
  // Events
  onBackendStatus: (callback) => {
    ipcRenderer.on('backend-status', (event, data) => callback(data))
  },
  onBackendError: (callback) => {
    ipcRenderer.on('backend-error', (event, data) => callback(data))
  }
})
