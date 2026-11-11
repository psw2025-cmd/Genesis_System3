from pathlib import Path
import ast
p=Path(r'C:\Genesis_System3_clean\content\app\app.py')
s=p.read_text(encoding='utf-8')
old='    chain_dir = Path(r"C:\\Genesis_System3_clean\\state\\chain_cache")\n    chain_files = list(chain_dir.glob("*.json")) if chain_dir.is_dir() else []\n    verified_contracts = 0\n    for cf in chain_files:\n        try:\n            cdata = json.loads(cf.read_text(encoding="utf-8"))\n            verified_contracts += len([c for c in cdata.get("contracts", []) if float(c.get("ltp", 0) or 0) > 0.05])\n        except Exception:\n            pass'
assert old in s,'inventory block changed, abort'
helper='''def _chain_cache_coverage():
    """Count positive-LTP contracts in readable local chain snapshots; not live-feed proof."""
    chain_dir = APP_DIR.parent.parent / "state" / "chain_cache"
    chain_files = list(chain_dir.glob("*.json")) if chain_dir.is_dir() else []
    verified_contracts = 0
    readable_files = 0
    for cf in chain_files:
        try:
            cdata = json.loads(cf.read_text(encoding="utf-8"))
            contracts = cdata.get("contracts", [])
            if not isinstance(contracts, list):
                continue
            readable_files += 1
            verified_contracts += sum(
                1 for c in contracts
                if isinstance(c, dict) and _positive_ltp(c.get("ltp"))
            )
        except (OSError, ValueError, TypeError):
            continue
    return readable_files, verified_contracts


def _positive_ltp(value):
    try:
        return float(value or 0) > 0.05
    except (ValueError, TypeError):
        return False


'''
s=s.replace(old,'    readable_snapshots, verified_contracts = _chain_cache_coverage()',1)
s=s.replace('        "verified_chain_snapshots_count": len(chain_files),','        "verified_chain_snapshots_count": readable_snapshots,',1)
s=s.replace('        "verified_chain_contracts_count": verified_contracts or 80,','        "verified_chain_contracts_count": verified_contracts,',1)
assert s.count('        "verified_chain_contracts": 80,')==1
s=s.replace('        "verified_chain_contracts": 80,','        "verified_chain_contracts": _chain_cache_coverage()[1],',1)
marker='# 01. Market Coverage Endpoints'
assert marker in s
pos=s.index(marker)
s=s[:pos]+helper+s[pos:]
ast.parse(s)
p.write_text(s,encoding='utf-8')
print('PATCH_OK',p,'source_parse=PASS')
