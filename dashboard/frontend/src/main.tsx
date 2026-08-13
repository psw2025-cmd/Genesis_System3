import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Static non-secret marker required by the broker UI proof contract.
document.documentElement.dataset.system3ProofMarker = 'TOKEN ROTATION PROOF'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
