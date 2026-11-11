import urllib.request
import re

url = "https://genesis-system3-web-802404398783.asia-south1.run.app/ui"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        print("Status Code:", resp.status)
        print("HTML Length:", len(html))
        
        # Check Title
        titles = re.findall(r"<title>(.*?)</title>", html, re.I)
        print("Title:", titles)
        
        # Check scripts
        scripts = re.findall(r"<script[^>]+src=[\"'](.*?)[\"']", html, re.I)
        print("Scripts:", scripts)
        
        # Check stylesheets
        links = re.findall(r"<link[^>]+href=[\"'](.*?)[\"']", html, re.I)
        print("Stylesheets/Links:", links)
        
        # Check if it has a root element or specific components
        root = re.findall(r"<div[^>]+id=[\"']root[\"']", html, re.I)
        print("Has root div:", bool(root))
        
        # Save sample
        with open("scratch/cloud_ui_sample.html", "w", encoding="utf-8") as f:
            f.write(html[:5000])
        print("Wrote first 5000 bytes to scratch/cloud_ui_sample.html")
except Exception as e:
    print("Error fetching UI:", type(e).__name__, e)
