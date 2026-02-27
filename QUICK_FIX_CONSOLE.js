/**
 * QUICK FIX - Run this in console to manually load data
 * Copy and paste this entire script into the browser console (F12)
 */

console.log('🔧 QUICK FIX: Manually loading dashboard data...');

// Fetch data from backend
Promise.all([
  fetch('http://localhost:8000/api/state').then(r => r.json()),
  fetch('http://localhost:8000/api/perf').then(r => r.json()),
  fetch('http://localhost:8000/api/health').then(r => r.json())
])
.then(([state, perf, health]) => {
  console.log('✅ Data fetched successfully!');
  console.log('State:', state);
  console.log('Perf:', perf);
  console.log('Health:', health);
  
  // Try to trigger React component update
  // This might work if component is mounted but not fetching
  const event = new CustomEvent('forceRefresh');
  window.dispatchEvent(event);
  
  // Also try to reload the page
  console.log('💡 If dashboard is still blank, try: window.location.reload()');
  
  return { state, perf, health };
})
.catch(error => {
  console.error('❌ Error fetching data:', error);
  console.log('💡 Backend might not be running. Check: http://localhost:8000/api/health');
});

// Also check if component is rendering
setTimeout(() => {
  console.log('\n📊 Component Check:');
  const root = document.getElementById('root');
  const main = document.querySelector('main');
  console.log('Root exists:', !!root);
  console.log('Main exists:', !!main);
  console.log('Current route:', window.location.pathname);
  
  if (!main || main.innerHTML.trim() === '') {
    console.log('⚠️  Main content is empty - component may not be rendering');
    console.log('💡 Try: window.location.reload()');
  }
}, 1000);
