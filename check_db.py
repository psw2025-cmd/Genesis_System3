import sqlite3
import os

db_path = 'c:/Genesis_System3_clean/data/genesis_daily_storage.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT symbol, date, spot, atm_strike FROM OPTION_CHAIN_MASTER ORDER BY date DESC LIMIT 10')
    rows = cur.fetchall()
    print("Found rows in OPTION_CHAIN_MASTER:")
    for r in rows:
        print(r)
    conn.close()
else:
    print("db_path does not exist!")
