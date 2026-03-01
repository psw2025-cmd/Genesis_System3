import socket
import requests

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_api(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code, response.json()
    except Exception as e:
        return None, str(e)

print(f"Checking Dashboard Backend (Port 8000)...")
if check_port(8000):
    print("Port 8000 is OPEN.")
    status, data = check_api("http://localhost:8000/api/state")
    if status == 200:
        print("API is RESPONDING (200 OK).")
        print(f"State Version: {data.get('version', 'N/A')}")
        print(f"Data Source: {data.get('source', 'N/A')}")
    else:
        print(f"API returned status {status}: {data}")
else:
    print("Port 8000 is CLOSED.")

print(f"
Checking Dashboard Frontend (Port 3000)...")
if check_port(3000):
    print("Port 3000 is OPEN.")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("Frontend is RESPONDING (200 OK).")
        else:
            print(f"Frontend returned status {response.status_code}")
    except Exception as e:
        print(f"Frontend check failed: {e}")
else:
    print("Port 3000 is CLOSED.")
