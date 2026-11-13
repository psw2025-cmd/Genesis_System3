from pathlib import Path

# 1. Update scripts/gcp_ui_tab_visual_proof.py
p1 = Path("scripts/gcp_ui_tab_visual_proof.py")
text1 = p1.read_text(encoding="utf-8")
old1 = '''    ("system", "System"),
    ("gates", "Live Gate"),'''
new1 = '''    ("system", "System"),
    ("system-readiness", "System Readiness"),
    ("gates", "Live Gate"),'''
if old1 in text1:
    p1.write_text(text1.replace(old1, new1, 1), encoding="utf-8")
    print("Updated scripts/gcp_ui_tab_visual_proof.py")
else:
    print("old1 not found in scripts/gcp_ui_tab_visual_proof.py")

# 2. Update scripts/gcp_public_dashboard_runtime_proof.py
p2 = Path("scripts/gcp_public_dashboard_runtime_proof.py")
text2 = p2.read_text(encoding="utf-8")
old2 = "if tab_count != 22 or pass_count != tab_count:"
new2 = "if tab_count != 23 or pass_count != tab_count:"
if old2 in text2:
    p2.write_text(text2.replace(old2, new2, 1), encoding="utf-8")
    print("Updated scripts/gcp_public_dashboard_runtime_proof.py")
else:
    print("old2 not found in scripts/gcp_public_dashboard_runtime_proof.py")

# 3. Update tests/test_ui_tab_visual_proof_contract.py
p3 = Path("tests/test_ui_tab_visual_proof_contract.py")
text3 = p3.read_text(encoding="utf-8")
old3 = """        sidebar_ids = re.findall(r"\{ id: '([^']+)',\\s*label:", sidebar)
        self.assertEqual(len(sidebar_ids), 22)
        self.assertEqual(len(sidebar_ids), len(set(sidebar_ids)))

        tree = ast.parse(proof)
        proof_ids: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "TABS":
                        value = ast.literal_eval(node.value)
                        proof_ids = [str(row[0]) for row in value]
        self.assertEqual(proof_ids, sidebar_ids)
        self.assertEqual(len(proof_ids), 22)"""

new3 = """        sidebar_ids = re.findall(r"\{ id: '([^']+)',\\s*label:", sidebar)
        self.assertEqual(len(sidebar_ids), 23)
        self.assertEqual(len(sidebar_ids), len(set(sidebar_ids)))

        tree = ast.parse(proof)
        proof_ids: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "TABS":
                        value = ast.literal_eval(node.value)
                        proof_ids = [str(row[0]) for row in value]
        self.assertEqual(proof_ids, sidebar_ids)
        self.assertEqual(len(proof_ids), 23)"""

if old3 in text3:
    p3.write_text(text3.replace(old3, new3, 1), encoding="utf-8")
    print("Updated tests/test_ui_tab_visual_proof_contract.py")
else:
    print("old3 not found in tests/test_ui_tab_visual_proof_contract.py")
