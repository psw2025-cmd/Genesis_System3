from pathlib import Path

p = Path(r"C:\Genesis_System3_clean\content\app\templates\premium.html")
text = p.read_text(encoding="utf-8")

old_code = """      var prof = d.profile || {};
      var funds = d.funds || {};
      var hsum = d.holdings_summary || {};"""

new_code = """      var authStatus = document.getElementById("broker-auth-status");
      if (authStatus) {
        authStatus.textContent = "CONNECTED (DhanHQ)";
        authStatus.className = "up";
        authStatus.style.color = "#00ff88";
      }
      var authState = document.getElementById("broker-auth-state");
      if (authState) {
        authState.textContent = "CONNECTED (DhanHQ)";
        authState.className = "up";
        authState.style.color = "#00ff88";
      }
      var errBanner = document.getElementById("dhan-err-banner");
      if (errBanner) {
        errBanner.style.display = "none";
      }

      var prof = d.profile || {};
      var funds = d.funds || {};
      var hsum = d.holdings_summary || {};"""

text_norm = text.replace("\r\n", "\n")
old_norm = old_code.replace("\r\n", "\n")
new_norm = new_code.replace("\r\n", "\n")

if old_norm in text_norm:
    text_norm = text_norm.replace(old_norm, new_norm, 1)
    p.write_text(text_norm, encoding="utf-8")
    print("Successfully updated broker-auth-status dynamic binding in premium.html")
else:
    print("old_code not found in premium.html!")
