with open(r'content/app/templates/premium.html', 'rb') as f:
    raw = f.read()

import re
matches = re.findall(b'.{0,5}23,440\\.80.{0,5}', raw)
for m in matches:
    print('Raw bytes:', m)
    print('Decoded utf-8:', m.decode('utf-8', errors='replace'))
