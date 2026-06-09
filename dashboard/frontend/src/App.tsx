import React, { useState, useEffect } from 'react'
import { BrowserRouter, HashRouter, Routes, Route, Link } from 'react-router-dom'
import Overview from './components/Overview'
import ChainAnalytics from './components/ChainAnalytics'
import Signals from './components/Signals'
import PaperTrading from './components/PaperTrading'
import ModelBehavior from './components/ModelBehavior'
import ControlPlane from './components/ControlPlane'
import Alerts from './components/Alerts'
import RiskDashboard from './components/RiskDashboard'
import AdvancedCharts from './components/AdvancedCharts'
import MLPerformance from './components/MLPerformance'
import AgentConsole from './components/AgentConsole'
import Backtest from './components/Backtest'
import ErrorBoundary from './components/ErrorBoundary'
import BackendConnectivityBanner from './components/BackendConnectivityBanner'
import './App.css'

function App() {
  const [darkMode, setDarkMode] = useState(true)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
  }, [darkMode])

  // Fix for file:// protocol - use HashRouter instead of BrowserRouter
  const Router = window.location.protocol === 'file:' ? HashRouter : BrowserRouter
  
  return (
    <Router>
      <div className={`min-h-screen ${darkMode ? 'dark bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
        <nav className={`${darkMode ? 'bg-gray-800' : 'bg-white'} border-b ${darkMode ? 'border-gray-700' : 'border-gray-200'} px-6 py-4`}>
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">System3 Ultra Dashboard</h1>
            <div className="flex items-center gap-2 flex-wrap">
              <Link to="/" className="px-3 py-1 hover:underline text-sm">Overview</Link>
              <Link to="/chain" className="px-3 py-1 hover:underline text-sm">Chain</Link>
              <Link to="/signals" className="px-3 py-1 hover:underline text-sm">Signals</Link>
              <Link to="/trading" className="px-3 py-1 hover:underline text-sm">Trading</Link>
              <Link to="/backtest" className="px-3 py-1 hover:underline text-sm">Backtest</Link>
              <Link to="/alerts" className="px-3 py-1 hover:underline text-sm">Alerts</Link>
              <Link to="/risk" className="px-3 py-1 hover:underline text-sm">Risk</Link>
              <Link to="/charts" className="px-3 py-1 hover:underline text-sm">Charts</Link>
              <Link to="/ml" className="px-3 py-1 hover:underline text-sm">ML</Link>
              <Link to="/model" className="px-3 py-1 hover:underline text-sm">Model</Link>
              <Link to="/control" className="px-3 py-1 hover:underline text-sm">Control</Link>
              <Link to="/agent" className="px-3 py-1 hover:underline text-sm">Agent</Link>
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="px-3 py-1 border rounded text-sm"
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
            </div>
          </div>
        </nav>

        <main className="p-6">
          <ErrorBoundary>
            <BackendConnectivityBanner />
            <Routes>
              <Route path="/" element={<ErrorBoundary><Overview /></ErrorBoundary>} />
              <Route path="/chain" element={<ErrorBoundary><ChainAnalytics /></ErrorBoundary>} />
              <Route path="/signals" element={<ErrorBoundary><Signals /></ErrorBoundary>} />
              <Route path="/trading" element={<ErrorBoundary><PaperTrading /></ErrorBoundary>} />
              <Route path="/backtest" element={<ErrorBoundary><Backtest /></ErrorBoundary>} />
              <Route path="/alerts" element={<ErrorBoundary><Alerts /></ErrorBoundary>} />
              <Route path="/risk" element={<ErrorBoundary><RiskDashboard /></ErrorBoundary>} />
              <Route path="/charts" element={<ErrorBoundary><AdvancedCharts /></ErrorBoundary>} />
              <Route path="/ml" element={<ErrorBoundary><MLPerformance /></ErrorBoundary>} />
              <Route path="/model" element={<ErrorBoundary><ModelBehavior /></ErrorBoundary>} />
              <Route path="/control" element={<ErrorBoundary><ControlPlane /></ErrorBoundary>} />
              <Route path="/agent" element={<ErrorBoundary><AgentConsole /></ErrorBoundary>} />
            </Routes>
          </ErrorBoundary>
        </main>
      </div>
    </Router>
  )
}

export default App
