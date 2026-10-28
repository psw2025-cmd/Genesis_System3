import os

path = os.path.join("dashboard", "frontend", "src", "components", "workspaces", "DataIntegrity.tsx")
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = '<StatusChip label="Dhan login" value={connected ? \'Authenticated\' : \'Not connected\'} status={connected ? \'ok\' : \'error\'} />'
replacement = '<StatusChip label="Dhan login" value={connected ? \'Authenticated\' : \'Not connected\'} status={connected ? \'ok\' : \'error\'} />\n              <StatusChip label="Mode" value={String(state?.mode || health?.mode || \'PAPER LOCKED\')} status="ok" />'

if "PAPER LOCKED" not in text:
    text = text.replace(target, replacement)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("SUCCESS: DataIntegrity.tsx updated with Mode chip")
else:
    print("DataIntegrity.tsx already has PAPER LOCKED")
