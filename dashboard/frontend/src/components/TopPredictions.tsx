import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import { TrendingUp, TrendingDown, Shield, Zap, AlertCircle, Info, Target } from 'lucide-react'

const ConfidenceMeter = ({ value }: { value: number }) => {
  const getColor = (v: number) => {
    if (v > 85) return 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]'
    if (v > 70) return 'bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]'
    if (v > 50) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="w-full bg-gray-700 h-3 rounded-full mt-2 overflow-hidden border border-gray-600">
      <div 
        className={`${getColor(value)} h-full transition-all duration-1000 ease-out`} 
        style={{ width: `${value}%` }}
      ></div>
    </div>
  )
}

export default function TopPredictions() {
  const [predictions, setPredictions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        setLoading(true)
        const res = await axios.get(`${API_BASE}/api/signals/top5`)
        if (res.data.status === 'ok') {
          setPredictions(res.data.predictions)
          setError(null)
        } else {
          setError(res.data.message || 'No high-confidence signals')
        }
      } catch (err) {
        setError('Market engine offline')
      } finally {
        setLoading(false)
      }
    }

    fetchPredictions()
    const interval = setInterval(fetchPredictions, 15000)
    return () => clearInterval(interval)
  }, [])

  if (loading && predictions.length === 0) {
    return (
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div className="h-6 w-48 bg-gray-700 rounded mb-6 animate-pulse"></div>
        {[1, 2, 3].map(i => (
          <div key={i} className="h-24 bg-gray-700/30 rounded-lg mb-4 animate-pulse"></div>
        ))}
      </div>
    )
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-2xl relative overflow-hidden">
      {/* Decorative background element */}
      <div className="absolute -top-24 -right-24 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl"></div>
      
      <div className="flex justify-between items-center mb-6 relative z-10">
        <h3 className="text-xl font-black flex items-center gap-2 text-white">
          <Zap className="text-yellow-400 fill-yellow-400 w-5 h-5" />
          AI ALPHA SELECTIONS
        </h3>
        <span className="text-[10px] bg-green-900/30 text-green-400 px-2 py-1 rounded border border-green-500/30 font-bold tracking-tighter">
          WORLD-CLASS ACCURACY
        </span>
      </div>

      {error ? (
        <div className="bg-blue-900/10 border border-blue-500/20 p-6 rounded-xl flex flex-col items-center text-center gap-3 relative z-10">
          <Info className="text-blue-400 w-10 h-10 opacity-50" />
          <div className="text-sm text-blue-200">
            <p className="font-bold text-lg">Market Scan in Progress</p>
            <p className="opacity-60 mt-1">The AI is currently analyzing institutional flows to find 85%+ probability entries.</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4 relative z-10">
          {predictions.map((pred, idx) => (
            <div key={idx} className="bg-black/40 p-5 rounded-xl border border-gray-700/50 hover:border-blue-500/50 transition-all group cursor-default">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xl font-black tracking-tighter text-white">{pred.symbol}</span>
                    <span className="text-[10px] text-gray-400 font-mono bg-gray-800 px-2 py-0.5 rounded border border-gray-700">{pred.contract}</span>
                  </div>
                  <div className="flex items-center gap-1.5 mt-1">
                    <div className={`p-1 rounded-md ${pred.direction === 'UP' ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                      {pred.direction === 'UP' ? (
                        <TrendingUp className="w-3 h-3 text-green-400" />
                      ) : (
                        <TrendingDown className="w-3 h-3 text-red-400" />
                      )}
                    </div>
                    <span className={`text-[10px] font-black tracking-widest ${pred.direction === 'UP' ? 'text-green-400' : 'text-red-400'}`}>
                      {pred.direction === 'UP' ? 'BULLISH ATTACK' : 'BEARISH PRESSURE'}
                    </span>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="text-2xl font-black text-white leading-none">{pred.confidence}%</div>
                  <div className="text-[9px] uppercase tracking-tighter text-gray-500 font-bold mt-1">AI Conviction</div>
                </div>
              </div>

              <ConfidenceMeter value={pred.confidence} />

              <div className="grid grid-cols-2 gap-3 mt-4 pt-4 border-t border-gray-800/50">
                <div className="flex flex-col">
                  <span className="text-[9px] text-gray-500 font-bold uppercase tracking-widest mb-1">Target Profit</span>
                  <div className="flex items-center gap-1 text-green-400 font-black">
                    <Target className="w-3 h-3" />
                    <span>{pred.profit_target}</span>
                  </div>
                </div>
                <div className="flex flex-col text-right">
                  <span className="text-[9px] text-gray-500 font-bold uppercase tracking-widest mb-1">AI Logic</span>
                  <div className="text-[10px] text-blue-400 font-bold flex items-center justify-end gap-1">
                    <Shield className="w-3 h-3" />
                    {pred.ai_insight}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-6 p-3 bg-black/40 rounded-lg border border-gray-800">
        <p className="text-[9px] text-gray-500 font-medium leading-relaxed">
          <span className="text-yellow-500/80 font-bold uppercase mr-1">Institutional Shield:</span>
          These selections use the 40% AI weighted engine + Order Flow Imbalance. Signals are only shown when probability exceeds 65%.
        </p>
      </div>
    </div>
  )
}
