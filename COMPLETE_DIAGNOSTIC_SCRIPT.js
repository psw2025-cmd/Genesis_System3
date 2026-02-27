/**
 * COMPLETE DIAGNOSTIC SCRIPT
 * Copy and paste this ENTIRE script into the browser console (F12)
 * It will run all tests and show results
 */

console.log('========================================');
console.log('SYSTEM3 ULTRA COMPLETE DIAGNOSTIC');
console.log('========================================\n');

// Test 1: Backend Health
console.log('TEST 1: Backend Health Check');
fetch('http://localhost:8000/api/health')
  .then(r => {
    console.log('  Status:', r.status);
    if (r.ok) {
      return r.json();
    } else {
      throw new Error(`HTTP ${r.status}`);
    }
  })
  .then(d => {
    console.log('  ✅ Backend is WORKING!');
    console.log('  Data:', d);
  })
  .catch(e => {
    console.error('  ❌ Backend is NOT working');
    console.error('  Error:', e.message);
  })
  .finally(() => {
    // Test 2: State Endpoint
    console.log('\nTEST 2: State Endpoint Check');
    fetch('http://localhost:8000/api/state')
      .then(r => {
        console.log('  Status:', r.status);
        if (r.ok) {
          return r.json();
        } else {
          throw new Error(`HTTP ${r.status}`);
        }
      })
      .then(d => {
        console.log('  ✅ State endpoint is WORKING!');
        console.log('  Data keys:', Object.keys(d));
        console.log('  Has data:', Object.keys(d).length > 0);
      })
      .catch(e => {
        console.error('  ❌ State endpoint FAILED');
        console.error('  Error:', e.message);
      })
      .finally(() => {
        // Test 3: Component Check
        console.log('\nTEST 3: Frontend Component Check');
        const root = document.getElementById('root');
        const main = document.querySelector('main');
        console.log('  Root element:', root ? '✅ EXISTS' : '❌ MISSING');
        console.log('  Main element:', main ? '✅ EXISTS' : '❌ MISSING');
        console.log('  Current URL:', window.location.href);
        console.log('  Current path:', window.location.pathname);
        
        // Test 4: Network Check
        console.log('\nTEST 4: Network Activity');
        console.log('  ⚠️  Check Network tab (F12 > Network) for:');
        console.log('     - Requests to /api/state');
        console.log('     - Requests to /api/health');
        console.log('     - Status codes (200 = good, 0 = blocked, 404 = not found)');
        
        // Test 5: React Check
        console.log('\nTEST 5: React Check');
        if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
          console.log('  ✅ React DevTools available');
        } else {
          console.log('  ⚠️  React DevTools not detected');
        }
        
        // Test 6: API_BASE Check
        console.log('\nTEST 6: API Configuration');
        if (typeof API_BASE !== 'undefined') {
          console.log('  ✅ API_BASE:', API_BASE);
        } else {
          console.log('  ❌ API_BASE not defined');
        }
        
        // Summary
        console.log('\n========================================');
        console.log('DIAGNOSTIC COMPLETE');
        console.log('========================================');
        console.log('\nNext Steps:');
        console.log('1. Check Network tab for API requests');
        console.log('2. Look for red errors in console');
        console.log('3. If backend works but no requests, component may not be rendering');
        console.log('4. Reinstall with new build that has logging');
      });
  });
