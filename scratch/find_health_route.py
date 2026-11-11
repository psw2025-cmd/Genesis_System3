with open('c:/Genesis_System3_clean/dashboard/backend/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('@app.get("/api/health")')
if pos != -1:
    line_start = text.rfind('\n', 0, pos)
    print(text[pos:pos+1500])
else:
    print("Not found")
