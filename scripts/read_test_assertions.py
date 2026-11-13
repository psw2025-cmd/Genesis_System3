with open('tests/test_ui_p0_recovery_mission.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m1 = re.search(r'def test_p0_08_.*?def ', text, re.DOTALL)
if m1:
    print('=== test_p0_08 ===')
    print(m1.group(0))

m2 = re.search(r'def test_p0_14_.*?(?=\Z|def )', text, re.DOTALL)
if m2:
    print('=== test_p0_14 ===')
    print(m2.group(0))
