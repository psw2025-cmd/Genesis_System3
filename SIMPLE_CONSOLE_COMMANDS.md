# Simple Console Commands - Type These Manually

## Step 1: Allow Pasting
Type this first:
```
allow pasting
```

## Step 2: Test Backend (Type This)
```javascript
fetch('http://localhost:8000/api/health').then(r => r.json()).then(d => console.log('Backend:', d)).catch(e => console.error('Error:', e))
```

## Step 3: Test State (Type This)
```javascript
fetch('http://localhost:8000/api/state').then(r => r.json()).then(d => console.log('State:', d)).catch(e => console.error('Error:', e))
```

## Step 4: Reload Page (Type This)
```javascript
window.location.reload()
```

## Step 5: Check Network Tab
1. Click **Network** tab
2. Press **F5** or **Ctrl+R** to reload
3. Look for requests to `/api/state` or `/api/health`
4. Tell me what status codes you see

## Full Diagnostic (After Allowing Pasting)
Once you type "allow pasting", you can paste the full script from `COMPLETE_DIAGNOSTIC_SCRIPT.js`

---

**Start with Step 1, then Step 2 and 3 to test if backend is reachable from the app!**
