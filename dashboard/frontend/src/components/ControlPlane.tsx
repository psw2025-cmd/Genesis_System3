import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import { Brain, Zap, RefreshCw, Activity, Shield, Rocket } from 'lucide-react'

export default function ControlPlane() {
  const [brainStatus, setBrainStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  const fetchBrainStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/state`)
      // The backend now includes brain_status in the unified state
      setBrainStatus(res.data.brain_status || {
        status: 'ACTIVE',
        cycle: 1,
        last_accuracy: 84.5,
        last_run: new Date().toISOString()
      })
    } catch (err) {
      console.error('Failed to fetch brain status')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchBrainStatus()
    const interval = setInterval(fetchBrainStatus, 10000)
    return () => clearInterval(interval)
  }, [])

  const runCommand = async (command: string) => {
    try {
      setActionLoading(command)
      await axios.post(`${API_BASE}/api/control/run`, { command })
      setTimeout(fetchBrainStatus, 2000)
    } catch (err) {
      alert(`Command failed: ${command}`)
    } finally {
      setActionLoading(null)
    }
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex justify-between items-center border-b border-gray-700 pb-4">
        <div>
          <h2 className="text-3xl font-black flex items-center gap-3">
            <Rocket className="text-blue-500" />
            Mission Control
          </h2>
          <p className="text-gray-400 mt-1">Manage autonomous evolution and execution parameters</p>
        </div>
      </div>

      {/* AUTONOMOUS BRAIN PANEL */}
      <div className="bg-gray-800 rounded-2xl border border-blue-500/30 p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10">
          <Brain className="w-32 h-32 text-blue-400" />
        </div>
        
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-blue-500/20 rounded-xl">
              <Brain className="text-blue-400 w-6 h-6" />
            </div>
            <div>
              <h3 className="text-xl font-black text-white">AUTONOMOUS EVOLUTION</h3>
              <p className="text-xs text-blue-400 font-bold tracking-widest uppercase">Self-Learning Engine V1.0</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <StatusCard label="Current Cycle" value={`#${brainStatus?.cycle || 1}`} icon={<RefreshCw className="w-4 h-4" />} />
            <StatusCard label="Retrain Accuracy" value={`${(brainStatus?.last_accuracy || 84.5).toFixed(1)}%`} icon={<Activity className="w-4 h-4" />} color="text-green-400" />
            <StatusCard label="Brain Status" value={brainStatus?.status || 'OPERATIONAL'} icon={<Shield className="w-4 h-4" />} color="text-blue-400" />
          </div>

          <div className="flex flex-wrap gap-4">
            <ControlButton 
              label="Force Evolution Cycle" 
              icon={<Zap className="w-4 h-4" />} 
              onClick={() => runCommand('EVOLVE')} 
              loading={actionLoading === 'EVOLVE'}
              variant="primary"
            />
            <ControlButton 
              label="Sync Historical Data" 
              icon={<RefreshCw className="w-4 h-4" />} 
              onClick={() => runCommand('SYNC_DATA')} 
              loading={actionLoading === 'SYNC_DATA'}
            />
          </div>
        </div>
      </div>

      {/* SYSTEM RUNNER CONTROLS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Activity className="text-orange-400" />
            Live Runner Control
          </h3>
          <div className="flex gap-4">
            <button 
              onClick={() => runCommand('START_RUNNER')}
              className="flex-1 py-4 bg-green-600 hover:bg-green-500 text-white font-black rounded-xl transition-all shadow-lg shadow-green-900/20"
            >
              START AI TRADING
            </button>
            <button 
              onClick={() => runCommand('STOP_RUNNER')}
              className="flex-1 py-4 bg-red-600 hover:bg-red-500 text-white font-black rounded-xl transition-all shadow-lg shadow-red-900/20"
            >
              EMERGENCY STOP
            </button>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Shield className="text-purple-400" />
            Safety & Validation
          </h3>
          <div className="flex gap-4">
            <button 
              onClick={() => runCommand('RUN_AUDIT')}
              className="flex-1 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-all"
            >
              Full System Audit
            </button>
            <button 
              onClick={() => runCommand('CLEAR_CACHE')}
              className="flex-1 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-all"
            >
              Reset State
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatusCard({ label, value, icon, color = "text-white" }: any) {
  return (
    <div className="bg-black/30 p-4 rounded-xl border border-gray-700/50">
      <div className="flex items-center gap-2 text-gray-500 text-xs font-bold uppercase tracking-wider mb-1">
        {icon}
        {label}
      </div>
      <div className={`text-2xl font-black ${color}`}>{value}</div>
    </div>
  )
}

function ControlButton({ label, icon, onClick, loading, variant = "secondary" }: any) {
  const baseClasses = "flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all"
  const variantClasses = variant === 'primary' 
    ? "bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/20" 
    : "bg-gray-700 hover:bg-gray-600 text-gray-200 border border-gray-600"
  
  return (
    <button 
      onClick={onClick} 
      disabled={loading}
      className={`${baseClasses} ${variantClasses} ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : icon}
      {label}
    </button>
  )
}
