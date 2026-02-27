// ONE-LINE TESTS - Type these one at a time in console

// Test 1: Backend health
fetch('http://localhost:8000/api/health').then(r => r.json()).then(d => console.log('✅ Backend:', d)).catch(e => console.error('❌ Error:', e))

// Test 2: State endpoint  
fetch('http://localhost:8000/api/state').then(r => r.json()).then(d => console.log('✅ State:', d, 'Keys:', Object.keys(d))).catch(e => console.error('❌ Error:', e))

// Test 3: Check if component exists
console.log('Root:', document.getElementById('root'), 'Main:', document.querySelector('main'))

// Test 4: Reload page
window.location.reload()

// Test 5: Check Network tab manually (F12 > Network > Reload page)
