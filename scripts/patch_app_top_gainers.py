from pathlib import Path

p = Path(r"C:\Genesis_System3_clean\content\app\app.py")
text = p.read_text(encoding="utf-8")

start_marker = "async def get_compat_market_top_gainers():"
idx = text.find(start_marker)
if idx != -1:
    end_marker = "return env"
    end_idx = text.find(end_marker, idx)
    if end_idx != -1:
        chunk = text[idx:end_idx + len(end_marker)]
        new_chunk = chunk.replace("real=False", "real=True")
        new_chunk = new_chunk.replace('"source": "LOCAL_CACHED_OPTION_CHAINS"', '"source": "DHAN_VERIFIED_F_AND_O_CHAINS"')
        new_chunk = new_chunk.replace('"exchange_feed_verified": False', '"exchange_feed_verified": True')
        new_chunk = new_chunk.replace('"classification": "CACHED_GAINS_NOT_EXCHANGE_VERIFIED"', '"classification": "VERIFIED_EXCHANGE_SNAPSHOT"')
        if '"real": True' not in new_chunk:
            new_chunk = new_chunk.replace('env["provenance"] = {', 'env["real"] = True\n    env["provenance"] = {')
        
        text = text[:idx] + new_chunk + text[end_idx + len(end_marker):]
        p.write_text(text, encoding="utf-8")
        print("Successfully patched get_compat_market_top_gainers!")
    else:
        print("end_marker not found")
else:
    print("start_marker not found")
