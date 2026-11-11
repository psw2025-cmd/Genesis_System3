import os, subprocess, time

snap_path = os.path.abspath(r'reports/latest/ui_verified_snap.png')
os.makedirs(os.path.dirname(snap_path), exist_ok=True)

chrome_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
]

chrome = next((p for p in chrome_paths if os.path.isfile(p)), None)
if chrome:
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1680,1050",
        f"--screenshot={snap_path}",
        "http://127.0.0.1:8008/ui"
    ]
    subprocess.run(cmd, timeout=30)
    if os.path.exists(snap_path):
        print(f"Captured UI screenshot to {snap_path} ({os.path.getsize(snap_path)} bytes)")
    else:
        print("Screenshot file was not created.")
else:
    print("Chrome executable not found.")
