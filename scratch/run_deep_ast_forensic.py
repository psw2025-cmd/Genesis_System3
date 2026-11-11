import os
import ast
import json
import re
import pathlib

ROOT = pathlib.Path(r"C:\Genesis_System3_clean")

# 1. Parse all Python files
py_targets = []
for p in ROOT.rglob("*.py"):
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    if any(x in rel for x in ["node_modules", ".venv", ".pytest_tmp", "scratch"]):
        continue
    py_targets.append((rel, p))

py_ast_errors = []
py_route_endpoints = []
py_sensitive_calls = []

for rel, p in py_targets:
    try:
        content = p.read_text(encoding="utf-8-sig", errors="replace")
        tree = ast.parse(content, filename=rel)
        for node in ast.walk(tree):
            # Check route decorators
            if isinstance(node, ast.FunctionDef):
                for dec in node.decorator_list:
                    dec_call = ""
                    if isinstance(dec, ast.Call):
                        fn = dec.func
                        dec_call = fn.attr if isinstance(fn, ast.Attribute) else fn.id if isinstance(fn, ast.Name) else ""
                        if dec_call in ["get", "post", "put", "delete", "route", "patch"]:
                            args_str = [ast.unparse(a) for a in dec.args] if hasattr(ast, 'unparse') else []
                            py_route_endpoints.append({"file": rel, "func": node.name, "line": node.lineno, "method": dec_call, "args": args_str})
                    elif isinstance(dec, ast.Attribute):
                        dec_call = dec.attr
                    elif isinstance(dec, ast.Name):
                        dec_call = dec.id
            # Check sensitive calls
            if isinstance(node, ast.Call):
                fn = node.func
                call_name = fn.attr if isinstance(fn, ast.Attribute) else fn.id if isinstance(fn, ast.Name) else ""
                if call_name in ["place_order", "cancel_order", "modify_order", "generate_token", "renew_token"]:
                    py_sensitive_calls.append({"file": rel, "line": node.lineno, "call": call_name})
    except (SyntaxError, IndentationError) as e:
        py_ast_errors.append({"file": rel, "line": e.lineno, "error": str(e.msg)})
    except Exception as e:
        py_ast_errors.append({"file": rel, "error": str(e)})

# 2. Check TypeScript / TSX files in dashboard/frontend/src
ts_targets = []
for p in (ROOT / "dashboard/frontend/src").rglob("*.[t|j]s*"):
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    ts_targets.append((rel, p))

ts_file_stats = []
ts_api_calls = []
ts_component_renders = []

for rel, p in ts_targets:
    try:
        content = p.read_text(encoding="utf-8-sig", errors="replace")
        # Find all API fetch/axios endpoints
        apis = re.findall(r'[\'"`](/api/[^\'"`\s\?]+)', content)
        for ep in set(apis):
            ts_api_calls.append({"file": rel, "endpoint": ep})
        
        # Check for Recharts ResponsiveContainer
        if "ResponsiveContainer" in content:
            ts_component_renders.append({"file": rel, "feature": "Recharts.ResponsiveContainer"})
        if "overflow-x-auto" in content or "overflowY" in content:
            ts_component_renders.append({"file": rel, "feature": "ScrollContainer"})
        if "ready_for_live" in content:
            ts_component_renders.append({"file": rel, "feature": "LifecycleReadyForLive"})
        
        ts_file_stats.append({"file": rel, "size": len(content), "lines": len(content.splitlines())})
    except Exception as e:
        pass

result = {
    "python_scanned": len(py_targets),
    "python_ast_errors_count": len(py_ast_errors),
    "python_ast_errors": py_ast_errors,
    "python_routes_count": len(py_route_endpoints),
    "python_sensitive_calls_count": len(py_sensitive_calls),
    "python_sensitive_calls": py_sensitive_calls[:20],
    "ts_files_scanned": len(ts_targets),
    "ts_api_calls_count": len(ts_api_calls),
    "ts_api_endpoints": sorted(list(set(x["endpoint"] for x in ts_api_calls))),
    "ts_component_features": ts_component_renders,
}

out_path = ROOT / "scratch/deep_ast_forensic_results.json"
out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"Deep AST Scan Completed: {len(py_targets)} Python files, {len(ts_targets)} TS/TSX files. Errors: {len(py_ast_errors)}")
