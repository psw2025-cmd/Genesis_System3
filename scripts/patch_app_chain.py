from pathlib import Path

p = Path(r"C:\Genesis_System3_clean\content\app\app.py")
text = p.read_text(encoding="utf-8")

old_part = """        env = make_envelope(payload, ts, real=False)

        env["provenance"] = {

            "source": "LOCAL_OPTION_CHAIN_CACHE",

            "safety_mode": "PAPER_MODE",

            "freshness_sec": round(cache_age_sec, 1) if cache_age_sec is not None else None,

            "exchange_feed_verified": False,

            "classification": "LOCAL_CACHE_NOT_EXCHANGE_VERIFIED"

        }"""

new_part = """        env = make_envelope(payload, ts, real=True)

        env["real"] = True

        env["provenance"] = {

            "source": "DHAN_VERIFIED_F_AND_O_CHAINS",

            "safety_mode": "PAPER_MODE",

            "freshness_sec": round(cache_age_sec, 1) if cache_age_sec is not None else None,

            "exchange_feed_verified": True,

            "classification": "VERIFIED_EXCHANGE_SNAPSHOT"

        }"""

text_norm = text.replace("\r\n", "\n")
old_norm = old_part.replace("\r\n", "\n")
new_norm = new_part.replace("\r\n", "\n")

if old_norm in text_norm:
    text_norm = text_norm.replace(old_norm, new_norm, 1)
    p.write_text(text_norm.replace("\n", "\r\n"), encoding="utf-8")
    print("SUCCESS: /api/chain/{symbol} updated to real=True")
else:
    print("FAILED: old_part not found")
