/**
 * Quick verification script to check if API_BASE is correct
 * Run this in the browser console after opening the app
 */

console.log('=== Dashboard API_BASE Verification ===');
console.log('Window location:', window.location.href);
console.log('Protocol:', window.location.protocol);
console.log('Hostname:', window.location.hostname);
console.log('Electron API available:', typeof window.electronAPI !== 'undefined');
console.log('User Agent:', navigator.userAgent);

// Check if API_BASE is imported (if using module system)
if (typeof API_BASE !== 'undefined') {
  console.log('API_BASE:', API_BASE);
  if (API_BASE === 'http://localhost:8000') {
    console.log('✅ API_BASE is CORRECT');
  } else {
    console.log('❌ API_BASE is INCORRECT:', API_BASE);
    console.log('Expected: http://localhost:8000');
  }
} else {
  console.log('⚠️ API_BASE not found in global scope');
  console.log('Check the config.ts file or import statement');
}

// Test backend connection
fetch('http://localhost:8000/api/health')
  .then(response => {
    if (response.ok) {
      console.log('✅ Backend is reachable at http://localhost:8000');
      return response.json();
    } else {
      console.log('❌ Backend returned error:', response.status);
    }
  })
  .then(data => {
    if (data) {
      console.log('✅ Backend health check:', data);
    }
  })
  .catch(error => {
    console.log('❌ Cannot reach backend:', error.message);
    console.log('Make sure backend is running on port 8000');
  });
