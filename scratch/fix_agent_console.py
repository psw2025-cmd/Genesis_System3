from pathlib import Path

p = Path("dashboard/frontend/src/components/AgentConsole.tsx")
text = p.read_text(encoding="utf-8")
text = text.replace("downloadProofPack: () => Promise<unknown>", "downloadProofPack: () => Promise<any>")
text = text.replace("useState<unknown>(null)", "useState<any>(null)")
p.write_text(text, encoding="utf-8")
print("AgentConsole.tsx updated successfully")
