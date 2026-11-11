from pathlib import Path

# 1. Update AGENTS.md
p_agents = Path("AGENTS.md")
text_agents = p_agents.read_text(encoding="utf-8")
if "C:\\Genesis_System3_Clean" not in text_agents:
    text_agents = text_agents.replace("C:\\Genesis_System3_clean", "C:\\Genesis_System3_Clean")
    p_agents.write_text(text_agents, encoding="utf-8")
    print("Updated AGENTS.md with C:\\Genesis_System3_Clean")
else:
    print("C:\\Genesis_System3_Clean already in AGENTS.md")

# 2. Update agent_policy.yaml
p_policy = Path("agent_policy.yaml")
text_policy = p_policy.read_text(encoding="utf-8")
old_url = "https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/"
new_url = "http://127.0.0.1:8000/ui/"
if old_url in text_policy:
    text_policy = text_policy.replace(old_url, new_url)
    p_policy.write_text(text_policy, encoding="utf-8")
    print("Updated agent_policy.yaml to local UI URL")
else:
    print("old_url not found in agent_policy.yaml")
