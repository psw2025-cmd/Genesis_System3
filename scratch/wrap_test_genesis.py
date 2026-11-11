from pathlib import Path

p = Path("tests/test_genesis_500_routes.py")
text = p.read_text(encoding="utf-8")

old_start = """client = TestClient(app, raise_server_exceptions=False)

# 1. Total routes"""

new_start = """client = TestClient(app, raise_server_exceptions=False)

def test_genesis_500_routes():
    # 1. Total routes"""

# We also indent all lines from line 12 downwards
lines = text.splitlines()
idx = lines.index("client = TestClient(app, raise_server_exceptions=False)")
header = lines[:idx+1]
body = lines[idx+1:]
indented_body = ["def test_genesis_500_routes():"]
for line in body:
    if line.strip():
        indented_body.append("    " + line)
    else:
        indented_body.append("")

new_text = "\n".join(header) + "\n\n" + "\n".join(indented_body) + "\n"
p.write_text(new_text, encoding="utf-8")
print("Wrapped test_genesis_500_routes.py in def test_genesis_500_routes()")
