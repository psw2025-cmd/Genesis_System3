# GENESIS SYSTEM 3

Automated trading system initialized.

## Genesis Dashboard Deployment

### Local backend
```powershell
.\.venv\Scripts\python.exe -m uvicorn dashboard.backend.app:app --host 127.0.0.1 --port 8000
```

### Local Streamlit console
```powershell
.\.venv\Scripts\streamlit.exe run dashboard\app.py --server.address 127.0.0.1 --server.port 8501
```

### Render web service
The `Procfile` starts the production FastAPI backend:
```text
web: uvicorn dashboard.backend.app:app --host 0.0.0.0 --port $PORT
```

### Docker
```powershell
docker build -t genesis-system3 .
docker run --env-file .env.example -p 8000:8000 genesis-system3
```

### Safety Defaults
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `SYSTEM3_REAL_ONLY=1`
- Real order placement remains blocked unless proof gates and explicit live flags pass.

### Final Operator Message
`I AM ALIVE. I AM LEARNING. ANALYZER MODE IS RUNNING. REAL EARNING IS NOT CLAIMED UNTIL PAPER AND LIVE PROOF PASS.`
