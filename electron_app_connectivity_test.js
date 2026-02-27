/**
 * Electron App Connectivity Test
 * Run this in Electron DevTools Console to verify backend connectivity
 */

async function testBackendConnectivity() {
  console.log('='.repeat(80))
  console.log('ELECTRON ↔ BACKEND CONNECTIVITY TEST')
  console.log('='.repeat(80))
  
  const BASE_URL = 'http://localhost:8000'
  const endpoints = [
    { name: 'Health', path: '/api/health' },
    { name: 'State', path: '/api/state' },
    { name: 'Learning Status', path: '/api/learning/status' },
    { name: 'Learning Insights', path: '/api/learning/insights' },
    { name: 'Forensic Report', path: '/api/forensic/report' },
    { name: 'Validation Status', path: '/api/validation/status' },
    { name: 'Chain NIFTY', path: '/api/chain/NIFTY' },
    { name: 'Signal Top', path: '/api/signal/top' },
    { name: 'Positions', path: '/api/positions' },
    { name: 'PnL', path: '/api/pnl' },
    { name: 'Performance', path: '/api/perf' }
  ]
  
  const results = []
  
  for (const endpoint of endpoints) {
    try {
      const response = await fetch(`${BASE_URL}${endpoint.path}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })
      
      const status = response.status
      const data = await response.json()
      
      if (status === 200) {
        console.log(`✅ ${endpoint.name}: HTTP ${status}`)
        results.push({ name: endpoint.name, status: 'OK', http: status })
      } else {
        console.error(`❌ ${endpoint.name}: HTTP ${status}`)
        results.push({ name: endpoint.name, status: 'FAIL', http: status })
      }
    } catch (error) {
      console.error(`❌ ${endpoint.name}: ${error.message}`)
      results.push({ name: endpoint.name, status: 'ERROR', error: error.message })
    }
  }
  
  console.log('\n' + '='.repeat(80))
  console.log('RESULTS SUMMARY')
  console.log('='.repeat(80))
  
  const passed = results.filter(r => r.status === 'OK').length
  const failed = results.filter(r => r.status !== 'OK').length
  
  console.log(`✅ Passed: ${passed}/${results.length}`)
  console.log(`❌ Failed: ${failed}/${results.length}`)
  
  if (failed === 0) {
    console.log('\n🎉 ALL ENDPOINTS WORKING - NO CONNECTIVITY ISSUES')
  } else {
    console.log('\n⚠️ SOME ENDPOINTS FAILED - CHECK ERRORS ABOVE')
    results.filter(r => r.status !== 'OK').forEach(r => {
      console.log(`  - ${r.name}: ${r.status}`)
    })
  }
  
  return results
}

// Run test
testBackendConnectivity().then(results => {
  window.__ELECTRON_CONNECTIVITY_TEST_RESULTS__ = results
  console.log('\nResults saved to window.__ELECTRON_CONNECTIVITY_TEST_RESULTS__')
})
