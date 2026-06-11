# Debug Instructions - Blank Dashboard

## Current Status
The dashboard is blank and the Network tab shows NO requests, which means the React component isn't making API calls.

## Added Extensive Logging
I've added console.log statements throughout the Overview component to track:
- Component rendering
- useEffect execution
- fetchData calls
- Backend readiness checks
- API call attempts
- Errors

## Next Steps

### 1. Rebuild and Reinstall
```bash
cd desktop_app
npm run build
```
Then reinstall the app.

### 2. Check Console Logs
After launching the app, open DevTools (F12) and check the Console tab. You should see:
- `[Overview] Component rendering...`
- `[Overview] Component mounted, starting data fetch...`
- `[Overview] API_BASE: http://localhost:8000`
- `[Overview] Calling fetchData()...`
- `[Overview] Making API calls...`

### 3. What to Look For

#### If you see NO logs at all:
- Component isn't rendering
- Route isn't matching
- JavaScript error preventing execution
- Check for red errors in console

#### If you see logs but no API calls:
- Backend readiness check is failing
- Network requests are being blocked
- CORS issue
- Check Network tab for blocked requests

#### If you see API calls but they fail:
- Backend not running
- Wrong URL
- CORS issue
- Check Network tab for error status codes

### 4. Manual Test
In the console, try:
```javascript
fetch('http://localhost:8000/api/health')
  .then(r => r.json())
  .then(d => console.log('Backend response:', d))
  .catch(e => console.error('Backend error:', e))
```

This will tell us if:
- Backend is reachable
- CORS is working
- Network is accessible

### 5. Check Backend Status
Open a browser and go to:
```
http://localhost:8000/api/health
```

If this works in browser but not in Electron, it's a CORS or network policy issue.

## Expected Console Output

After the fix, you should see:
```
[Overview] Component rendering...
[Overview] State: {health: null, backendReady: false, error: null}
[Overview] Component mounted, starting data fetch...
[Overview] API_BASE: http://localhost:8000
[Overview] Backend ready state: false
[Overview] Calling fetchData()...
[Overview] fetchData called, retryCount: 0, backendReady: false
[Overview] Backend not ready, checking...
[Overview] Backend ready check result: true/false
[Overview] Making API calls...
[Overview] Fetching from http://localhost:8000/api/state and /api/perf...
[Overview] API calls successful!
```

## Files Changed
- ✅ `dashboard/frontend/src/components/Overview.tsx` - Added extensive logging
- ✅ Frontend rebuilt

---

**Status:** Ready for testing with detailed logging
