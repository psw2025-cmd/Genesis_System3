import psutil

try:
    p = psutil.Process(28272)
    print('PID 28272:')
    print('  cwd:', p.cwd())
    print('  exe:', p.exe())
    print('  cmdline:', p.cmdline())
except Exception as e:
    print('psutil error:', e)
