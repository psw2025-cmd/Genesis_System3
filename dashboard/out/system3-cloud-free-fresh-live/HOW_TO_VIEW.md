# Kaise Dekhna Hai - Step by Step

🔴 **LIVE URL:** [https://psw2025-cmd.github.io/Genesis_System3/dashboard/out/system3-cloud-free-fresh-live/](https://psw2025-cmd.github.io/Genesis_System3/dashboard/out/system3-cloud-free-fresh-live/)

---

### 1. Mobile & Desktop Access
- **Mobile (WhatsApp / Phone Browser):** Upar diye gaye LIVE URL ko copy karke WhatsApp pe kisi ko bhi share kar sakte ho ya direct Chrome/Safari me open kar sakte ho. Pura dashboard responsive hai.
- **Desktop (PC / Laptop):** Chrome / Edge / Firefox me LIVE URL open karo aur `Ctrl + D` dabake bookmark kar lo. 1920x1080 full HD view milega.

---

### 2. Roz Subah Kya Karna Hai (Daily Routine at 9:15 AM)
1. **Roz subah 9:15 AM** market open hote hi LIVE URL kholo.
2. **Section B (Comparison Table)** dekho:
   - **🥇 Gold Winner (Cloudflare Free):** Agar daily 100k requests ke andar hai, to ye sabse fast 20ms Mumbai edge response dega.
   - **🥈 Silver (Oracle Always Free):** Agar Cloudflare 100k reach ho jaye to switch to Oracle Always Free (4 OCPU / 24GB RAM continuous processing).
   - **🥉 Bronze (GitHub Actions EOD):** Shaam ko 3:30 PM market close ke baad EOD ledger reconciliation aur proof audit dekho.
3. **Live Pipeline Status** me Ingestion stream (58k ticks/sec) aur R2 storage active check karo.

---

### 3. Kya Nahi Karna Hai (Strict Invariants)
- ❌ **Laptop pe kuch bhi install mat karo:** Na Python, na Node, na Docker. Ye 100% cloud-native system hai jo GitHub Cloud aur Edge pe chalta hai.
- ❌ **Koi bhi Paid Plan mat lo:** Cloudflare $11, Oracle paid, Google IPv4 $3.65 sab prohibited hain. Ye 100% FREE edition hai ($0.00 forever).
- ❌ **Purana `dashboard/out/` wala folder mat kholna:** Sirf ye naya `dashboard/out/system3-cloud-free-fresh-live/` folder hi valid aur active hai. Purana koi bhi asset reuse nahi kiya gaya hai.
- ❌ **Angel / Non-Dhan broker targets use mat karo:** System strictly DhanHQ sole broker authority pe locked hai.

---

### 4. Agar Error Aaye To Kya Karna Hai
- **Scenario A (Cloudflare 100k quota exhaust ho jaye):**
  System automatically Silver Tier (Oracle Always Free 4 OCPU 24GB) pe failover karta hai. Koi crash nahi hoga.
- **Scenario B (GitHub Pages update delay):**
  Hard refresh karo (`Ctrl + F5` desktop pe, ya mobile browser me incognito tab).
- **Scenario C (Broker token expire):**
  Dhan daily login flow run karo via GitHub Actions free workflow.

---

### 5. 100% Free Kaise Hai (Zero Cost Math)
| Platform Component | Free Allowance | Actual System Consumption | Cost |
| :--- | :--- | :--- | :--- |
| **Cloudflare Workers** | 100,000 requests / day free | ~60,000 requests / day | **$0.00** |
| **Cloudflare R2** | 10 GB storage free / zero egress | 2.5 GB OHLC bars | **$0.00** |
| **Oracle Cloud** | 4 OCPU ARM + 24GB RAM + 200GB NVMe | 1 instance 24/7 forever free | **$0.00** |
| **GitHub Actions** | 2,000 minutes / month free | ~450 minutes / month | **$0.00** |
| **Google Drive** | 15 GB storage free | 4 GB compressed ticks | **$0.00** |
| **HuggingFace** | Unlimited public datasets free | Archival parquet storage | **$0.00** |
| **Google Colab** | Free TPU v2/v3 quota | Weekly model backtest & training | **$0.00** |
| **GitHub Pages** | 100 GB bandwidth / month free | Live UI hosting | **$0.00** |
| **Total Monthly Cost** | | | **$0.00 (Zero)** |

---

### 6. Cloud Me Kaise Chal Raha Hai
1. **DhanHQ Market Stream** live ticks bhejta hai.
2. **60 Cloudflare Workers** Mumbai Edge POP pe 20ms me ticks absorb karte hain.
3. **Cloudflare R2** me 1-min aur 5-min OHLC bars store hoti hain.
4. **Google Drive + HuggingFace + GitHub** me parallel tri-target sync hota hai.
5. **Colab TPU** free tier quant models train karta hai.
6. **GitHub Actions + Pages** automatically live website host karta hai.
