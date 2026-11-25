import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

handlers = re.findall(r'onclick="([^"]+)"', text)
print(f"Total onclick handlers: {len(handlers)}")
unique = sorted(set(handlers))
for h in unique:
    print("  ", h)
