from pathlib import Path

p = Path(r"C:\Genesis_System3_clean\pyproject.toml")
text = p.read_text(encoding="utf-8")

if "--basetemp=.pytest_tmp" not in text:
    text = text.replace(
        'addopts = "-q --disable-warnings',
        'addopts = "-q --disable-warnings --basetemp=.pytest_tmp'
    )
    p.write_text(text, encoding="utf-8")
    print("Added --basetemp=.pytest_tmp to pyproject.toml")
else:
    print("Already present in pyproject.toml")
