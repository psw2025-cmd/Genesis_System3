from pathlib import Path

p = Path(r"C:\Genesis_System3_clean\content\app\templates\premium.html")
text = p.read_text(encoding="utf-8")

old_code = """          var formatted = "₹" + q.price.toLocaleString("en-IN",{maximumFractionDigits:2,minimumFractionDigits:2});
          put(entry[1], formatted);
          put(entry[2], q.status + " | last trade " + q.last_trade_ist + " (" + Math.round(q.age_seconds || 0) + "s ago)");"""

new_code = """          var formatted = "₹" + q.price.toLocaleString("en-IN",{maximumFractionDigits:2,minimumFractionDigits:2});
          put(entry[1], formatted);
          put(entry[2], q.status + " " + q.price.toFixed(2) + " | last trade " + q.last_trade_ist + " (" + Math.round(q.age_seconds || 0) + "s ago)");"""

text_norm = text.replace("\r\n", "\n")
old_norm = old_code.replace("\r\n", "\n")
new_norm = new_code.replace("\r\n", "\n")

if old_norm in text_norm:
    text_norm = text_norm.replace(old_norm, new_norm, 1)
    p.write_text(text_norm, encoding="utf-8")
    print("Successfully updated entry[2] in premium.html")
else:
    print("old_code not found in premium.html!")
