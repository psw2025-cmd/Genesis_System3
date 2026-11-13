from pathlib import Path
import ast
p=Path(r'C:\Genesis_System3_clean\content\app\app.py')
s=p.read_text(encoding='utf-8')
old='''    env = make_envelope(data, ts, real=True)
    env["provenance"] = {
        "source": "RECONCILED_DHAN_MASTER_AND_CHAIN_SNAPSHOTS",
        "safety_mode": "PAPER_MODE",
        "freshness_sec": 0,
        "exchange_feed_verified": True,
        "classification": "VERIFIED_EXCHANGE_SNAPSHOT"
    }
    return env'''
new='''    # Inventory counts include local cache and static universe metadata.
    # They are not proof of a fresh exchange quote.
    env = make_envelope(data, ts, real=False)
    env["provenance"] = {
        "source": "LOCAL_CHAIN_CACHE_AND_STATIC_UNIVERSE_METADATA",
        "safety_mode": "PAPER_MODE",
        "freshness_sec": None,
        "exchange_feed_verified": False,
        "classification": "CACHE_COVERAGE_FRESHNESS_NOT_VERIFIED"
    }
    return env'''
assert s.count(old)==1,'Expected original inventory provenance block not found'
s=s.replace(old,new,1)
ast.parse(s)
p.write_text(s,encoding='utf-8')
print('INVENTORY_PROVENANCE_PATCH_OK')
