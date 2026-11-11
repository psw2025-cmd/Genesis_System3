import re

path = 'content/app/templates/premium.html'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace button type="submit" id="btn-submit-order" with type="button" and onclick
pattern = r'<button\s+type="submit"\s+id="btn-submit-order"'
replacement = '<button type="button" id="btn-submit-order" onclick="submitLiveOrder(event)"'

if re.search(pattern, text):
    new_text = re.sub(pattern, replacement, text, count=1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESS: Button type changed to button with onclick.")
else:
    print("Button already has type='button' or not matched.")
