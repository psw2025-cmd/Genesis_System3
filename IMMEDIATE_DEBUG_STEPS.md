# Immediate Debug Steps

## Critical Issue
Network tab shows **NO requests**, meaning the React component isn't executing or making API calls.

## What I've Done
✅ Added extensive console logging to track component execution
✅ Frontend rebuilt with logging
✅ Electron app rebuild in progress

## While Waiting for Rebuild

### Test Backend Manually
1. Open a browser (Chrome/Edge)
2. Go to: `http://localhost:8000/api/health`
3. **If this works**: Backend is running, issue is in Electron/frontend
4. **If this fails**: Backend isn't running, need to start it

### Check Current App Console
Even with the old build, check the console (F12) for:
- Any red error messages
- Any warnings
- Check if `API_BASE` is logged

### Manual API Test in Console
In the DevTools console, paste:
```javascript
fetch('http://localhost:8000/api/health')
  .then(r => {
    console.log('Status:', r.status);
    return r.json();
  })
  .then(d => console.log('Data:', d))
  .catch(e => console.error('Error:', e))
```

This will tell us:
- ✅ If backend is reachable from Electron
- ✅ If CORS is working
- ✅ If network requests work at all

## After Rebuild Completes

1. **Reinstall** the app
2. **Launch** and immediately open DevTools (F12)
3. **Check Console** - you should see logs like:
   ```
   [Overview] Component rendering...
   [Overview] Component mounted, starting data fetch...
   [Overview] API_BASE: http://localhost:8000
   [Overview] Calling fetchData()...
   ```

4. **If you see NO logs**:
   - Component isn't rendering
   - Route issue
   - JavaScript error blocking execution

5. **If you see logs but no Network requests**:
   - Backend check is failing
   - Requests are being blocked
   - Check Network tab for blocked requests

6. **If you see Network requests but they fail**:
   - Backend not running
   - Wrong URL
   - CORS issue
   - Check status codes in Network tab

## Quick Fix to Try

If backend is running but component isn't fetching, try this in console:
```javascript
// Force trigger fetch
window.location.reload()
```

Or manually trigger:
```javascript
// Check if component is mounted
document.querySelector('main') // Should exist
```

## Expected Behavior After Fix

1. Console shows: `[Overview] Component rendering...`
2. Console shows: `[Overview] Calling fetchData()...`
3. Network tab shows requests to `/api/state` and `/api/perf`
4. Dashboard shows data within 5 seconds

---

**Status:** Rebuild in progress, ready for detailed debugging
