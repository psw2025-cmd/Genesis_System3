# Manual Test in Console

## Current Status
- ✅ API_BASE is correctly configured: `http://localhost:8000`
- ✅ App is running in Electron
- ❌ Dashboard is blank
- ❌ No component logs visible

## Immediate Tests to Run

### Test 1: Check if Backend is Running
In the console, paste this:
```javascript
fetch('http://localhost:8000/api/health')
  .then(r => {
    console.log('Status:', r.status);
    return r.json();
  })
  .then(d => {
    console.log('✅ Backend is working!', d);
  })
  .catch(e => {
    console.error('❌ Backend error:', e);
  });
```

**Expected:** Should see status 200 and health data
**If fails:** Backend isn't running

### Test 2: Check if Component is Mounted
```javascript
// Check if React root exists
console.log('Root element:', document.getElementById('root'));

// Check if main content area exists
console.log('Main element:', document.querySelector('main'));

// Check for any React errors
console.log('Window errors:', window.onerror);
```

### Test 3: Manually Trigger Data Fetch
```javascript
// Try to fetch data manually
fetch('http://localhost:8000/api/state')
  .then(r => r.json())
  .then(d => {
    console.log('✅ State data:', d);
    // Check if data looks good
    console.log('Has data:', Object.keys(d).length > 0);
  })
  .catch(e => {
    console.error('❌ State fetch error:', e);
  });
```

### Test 4: Check for JavaScript Errors
Look in the console for:
- Red error messages
- Any "Uncaught" errors
- Any "Failed to load" messages

### Test 5: Check Network Tab
1. Open **Network** tab in DevTools
2. Look for requests to:
   - `/api/state`
   - `/api/health`
   - `/api/perf`
3. Check if they show:
   - Status 200 (success)
   - Status 0 (blocked/CORS)
   - Status 404 (not found)
   - No requests at all (component not running)

## What to Report Back

After running these tests, tell me:
1. ✅ or ❌ for each test
2. Any error messages you see
3. What the Network tab shows
4. Any red errors in console

This will help identify the exact issue!
