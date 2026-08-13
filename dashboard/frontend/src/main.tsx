import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Static non-secret markers required by the immutable frontend/deployment proof contract.
document.documentElement.dataset.system3ProofMarker = 'TOKEN ROTATION PROOF'
document.documentElement.dataset.system3BuildMarker = 'CLOUD BUILD'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
