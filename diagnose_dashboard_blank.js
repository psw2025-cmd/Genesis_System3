/**
 * Dashboard Blank Screen Diagnostic
 * Run this in the browser console (F12) to diagnose why dashboard is blank
 */

console.log('=== Dashboard Blank Screen Diagnostic ===\n');

// 1. Check API_BASE
console.log('1. API Configuration:');
console.log('   API_BASE:', typeof API_BASE !== 'undefined' ? API_BASE : 'NOT FOUND');
console.log('   Expected: http://localhost:8000');

// 2. Test Backend Connection
console.log('\n2. Testing Backend Connection...');
fetch('http://localhost:8000/api/health')
  .then(response => {
    console.log('   ✅ Backend reachable');
    console.log('   Status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('   Response:', data);
    console.log('   ✅ Backend is working');
  })
  .catch(error => {
    console.log('   ❌ Backend NOT reachable');
    console.log('   Error:', error.message);
    console.log('   Possible causes:');
    console.log('   - Backend not running');
    console.log('   - Firewall blocking port 8000');
    console.log('   - CORS issue');
  });

// 3. Test State Endpoint
console.log('\n3. Testing /api/state endpoint...');
fetch('http://localhost:8000/api/state')
  .then(response => {
    console.log('   Status:', response.status);
    if (response.ok) {
      return response.json();
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  })
  .then(data => {
    console.log('   ✅ State endpoint working');
    console.log('   Data keys:', Object.keys(data));
  })
  .catch(error => {
    console.log('   ❌ State endpoint failed');
    console.log('   Error:', error.message);
  });

// 4. Check for Console Errors
console.log('\n4. Check Console for Errors:');
console.log('   Look for red error messages above');
console.log('   Common errors:');
console.log('   - CORS errors');
console.log('   - Network errors');
console.log('   - 404 Not Found');
console.log('   - Connection refused');

// 5. Check Network Tab
console.log('\n5. Network Tab Check:');
console.log('   Open Network tab (F12 > Network)');
console.log('   Look for requests to:');
console.log('   - http://localhost:8000/api/state');
console.log('   - http://localhost:8000/api/health');
console.log('   - http://localhost:8000/api/perf');
console.log('   Check if they show:');
console.log('   - Status 200 (OK)');
console.log('   - Status 0 (Failed/CORS)');
console.log('   - Status 404 (Not Found)');

// 6. Check React Component State
console.log('\n6. React Component Check:');
console.log('   The Overview component shows "Loading..." when health is null');
console.log('   This means API calls are failing or not completing');

console.log('\n=== Diagnostic Complete ===');
console.log('Share the output above to help diagnose the issue');
