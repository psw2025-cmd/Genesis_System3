import os, time, pyotp
from dotenv import load_dotenv
from dhanhq import DhanLogin

load_dotenv(r'C:\Genesis_System3_clean\.secrets\dhan.env', override=True)

cid = os.getenv('DHAN_CLIENT_ID')
pin = os.getenv('DHAN_PIN')
totp_secret = os.getenv('DHAN_TOTP_SECRET')

print("System Time:", time.strftime("%Y-%m-%d %H:%M:%S"))
if not totp_secret:
    print("MISSING: DHAN_TOTP_SECRET in .env")
elif not pin:
    print("MISSING: DHAN_PIN in .env")
else:
    totp = pyotp.TOTP(totp_secret.strip()).now()
    print("Generated TOTP:", totp)
    try:
        res = DhanLogin(cid).generate_token(pin, totp)
        print("Response:", res)
    except Exception as e:
        print("Exception:", e)
