from pathlib import Path

p = Path("AGENTS.md")
raw = p.read_bytes()
if b"\x97" in raw:
    fixed = raw.replace(b"\x97", b"-")
    p.write_bytes(fixed)
    print("Fixed non-UTF8 byte in AGENTS.md")
else:
    print("Byte 0x97 not found in AGENTS.md")
