import os
import subprocess
import json

print('=== 1. C:\\content Purpose & Anatomy ===')
print('Exists:', os.path.exists(r'C:\content'))
if os.path.exists(r'C:\content'):
    print('Entries:', os.listdir(r'C:\content'))
    for root, dirs, files in os.walk(r'C:\content'):
        print(' ', root, 'dirs:', dirs, 'files:', files)

print('\n=== 2. C:\\Genesis_System3_clean Purpose & Anatomy ===')
print('Exists:', os.path.exists(r'C:\Genesis_System3_clean'))
print('Git dir exists:', os.path.exists(r'C:\Genesis_System3_clean\.git'))

print('\n=== 3. Current Working Directory & Repository ===')
print('Current cwd:', os.getcwd())

print('\n=== 4. Port 8008 Running Process ===')
try:
    cmd = 'powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8008 -State Listen | ForEach-Object { $p = $_.OwningProcess; Get-CimInstance Win32_Process -Filter \\"ProcessId = $p\\" | Select-Object ProcessId, CommandLine, ExecutablePath } | ConvertTo-Json"'
    res = subprocess.check_output(cmd, shell=True).decode()
    print('Process info:\n', res)
except Exception as e:
    print('Failed to get process info:', e)
