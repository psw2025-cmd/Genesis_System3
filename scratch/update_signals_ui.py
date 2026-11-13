import os

target_path = 'dashboard/frontend/src/components/Signals.tsx'

with open(target_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

clean_lines = lines[:340]
content = ''.join(clean_lines)

gap_table_jsx = '''
      {/* Premarket & Live Gap-Up Runners + ML Predictions */}
      <div className="bg-gray-800 p-6 rounded-lg border border-purple-500/40">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <div>
            <h3 className="text-xl font-bold text-purple-400">⚡ Premarket & Live Gap-Up Runners + ML Predictions</h3>
            <div className="text-xs text-gray-400">Real-time Dhan LTP vs Previous Close + Multi-Model ML Consensus Predictions</div>
          </div>
          <span className="px-3 py-1 bg-purple-900/40 border border-purple-500 text-purple-300 text-xs font-bold rounded">
            {gapRunners.length} Candidates Screened
          </span>
        </div>

        {gapRunners.length === 0 ? (
          <div className="p-4 text-center text-gray-400 text-sm">Scanning option universe for gap-up candidates…</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-gray-700 text-gray-400 uppercase">
                  <th className="py-2 px-3">Symbol</th>
                  <th className="py-2 px-3">LTP / Prev</th>
                  <th className="py-2 px-3">Gap %</th>
                  <th className="py-2 px-3">ML Signal</th>
                  <th className="py-2 px-3">ML Confidence</th>
                  <th className="py-2 px-3">Target Price</th>
                  <th className="py-2 px-3">Rec. Strike</th>
                  <th className="py-2 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {gapRunners.slice(0, 8).map((r: any, idx: number) => {
                  const isUp = (r.gap_pct || 0) >= 0
                  const ml = r.ml_prediction || {}
                  return (
                    <tr key={idx} className="hover:bg-gray-750 transition-colors">
                      <td className="py-2 px-3 font-bold text-white">{r.symbol}</td>
                      <td className="py-2 px-3 text-gray-300">₹{r.ltp} <span className="text-gray-500">/ ₹{r.previous_close}</span></td>
                      <td className={`py-2 px-3 font-bold ${isUp ? 'text-green-400' : 'text-red-400'}`}>
                        {isUp ? '+' : ''}{r.gap_pct}%
                      </td>
                      <td className="py-2 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${ml.signal === 'BUY' ? 'bg-green-900/60 text-green-300 border border-green-600' : 'bg-gray-800 text-gray-400'}`}>
                          {ml.signal || 'WATCH'} {r.direction}
                        </span>
                      </td>
                      <td className="py-2 px-3 font-bold text-indigo-300">{ml.confidence_pct}%</td>
                      <td className="py-2 px-3 text-emerald-400 font-bold">₹{ml.target_price} <span className="text-gray-500 text-[10px]">(+{ml.expected_alpha_pct}%)</span></td>
                      <td className="py-2 px-3 text-amber-300 font-bold">{ml.recommended_strike}</td>
                      <td className="py-2 px-3">
                        <span className="px-2 py-0.5 bg-blue-900/40 text-blue-300 rounded text-[10px]">
                          {r.status}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
'''

# 1. State definition
if 'const [gapRunners, setGapRunners]' not in content:
    content = content.replace(
        'const [qc, setQc] = useState<any>(null)',
        'const [qc, setQc] = useState<any>(null)\n  const [gapRunners, setGapRunners] = useState<any[]>([])',
        1
    )

# 2. Add gapRes to Promise.allSettled
if 'api/opportunity-gap' not in content:
    content = content.replace(
        "axios.get(`${API_BASE}/api/gain_rank`),",
        "axios.get(`${API_BASE}/api/gain_rank`),\n        axios.get(`${API_BASE}/api/opportunity-gap`),",
        1
    )
    content = content.replace(
        "const [stateRes, scannerRes, gainRes] = await Promise.allSettled([",
        "const [stateRes, scannerRes, gainRes, gapRes] = await Promise.allSettled([",
        1
    )

# 3. Add setGapRunners in fetchData
if 'setGapRunners((gapRes' not in content:
    content = content.replace(
        "const candidate = scannerCandidate || gainCandidate",
        "const candidate = scannerCandidate || gainCandidate\n      if (gapRes && gapRes.status === 'fulfilled' && Array.isArray((gapRes.value as any)?.data?.runners)) {\n        setGapRunners((gapRes.value as any).data.runners)\n      }",
        1
    )

# 4. Insert gap_table_jsx right before MarketTopCePeTable
old_table_marker = '<div className="bg-gray-800 rounded-lg overflow-hidden h-[420px]">'
if old_table_marker in content and 'Premarket & Live Gap-Up Runners' not in content:
    content = content.replace(old_table_marker, gap_table_jsx + '\n      ' + old_table_marker, 1)

with open(target_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Successfully updated Signals.tsx! Total chars:', len(content))
