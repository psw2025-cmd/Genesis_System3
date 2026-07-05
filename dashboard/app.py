"""
System3 Ultra Streamlit Dashboard
Connects to backend API (port 8000) for real-time monitoring.
"""

import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="System3 Ultra Dashboard", page_icon="📊", layout="wide")
st.title("System3 Ultra Dashboard")

# Backend health check
with st.container():
    st.subheader("Backend Status")
    try:
        r = requests.get(f"{API_BASE}/api/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            st.success("Backend is running")
            if isinstance(data, dict):
                for k, v in data.items():
                    st.text(f"  {k}: {v}")
        else:
            st.warning(f"Backend returned {r.status_code}")
    except requests.RequestException as e:
        st.error(f"Backend not reachable: {e}")
        st.info("Start the backend with: uvicorn app:app --host 127.0.0.1 --port 8000 (from dashboard/backend)")

st.divider()
st.markdown(f"**API docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)")
st.markdown(f"**React frontend:** [http://127.0.0.1:3000](http://127.0.0.1:3000)")
