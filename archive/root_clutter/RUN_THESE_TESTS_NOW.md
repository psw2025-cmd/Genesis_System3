# 🔍 Run These Tests in Console RIGHT NOW

## Copy and Paste These One by One

### Test 1: Check Backend
```javascript
fetch('http://localhost:8000/api/health')
  .then(r => { console.log('✅ Status:', r.status); return r.json(); })
  .then(d => console.log('✅ Backend Data:', d))
  .catch(e => console.error('❌ Backend Error:', e));
```

### Test 2: Check State Endpoint
```javascript
fetch('http://localhost:8000/api/state')
  .then(r => { console.log('✅ Status:', r.status); return r.json(); })
  .then(d => { console.log('✅ State Data:', d); console.log('Keys:', Object.keys(d)); })
  .catch(e => console.error('❌ State Error:', e));
```

### Test 3: Check if Component Exists
```javascript
console.log('Root:', document.getElementById('root'));
console.log('Main:', document.querySelector('main'));
console.log('Overview route active?', window.location.hash.includes('overview') || window.location.pathname === '/');
```

### Test 4: Check for Errors
```javascript
// Check for any stored errors
console.log('Window errors:', window.onerror);
// Check React DevTools
console.log('React available?', window.__REACT_DEVTOOLS_GLOBAL_HOOK__);
```

### Test 5: Force Reload Component
```javascript
// Try to trigger a re-render
window.location.reload();
```

## What to Look For

1. **If Test 1 fails**: Backend isn't running - need to start it
2. **If Test 1 works but Test 2 fails**: Backend is running but state endpoint has issues
3. **If both work**: Backend is fine, issue is in frontend
4. **If no logs appear**: Component isn't rendering at all

## After Running Tests

Tell me:
- ✅ or ❌ for each test
- Any error messages
- What you see in Network tab (F12 > Network)

---

**Then reinstall with the new build that has logging!**
