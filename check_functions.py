import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract script content
scripts = re.findall(r'<script\b[^>]*>([\s\S]*?)<\/script>', text)
combined_script = "\n".join(scripts)

handlers = re.findall(r'onclick="([^"(]+)', text)
unique_funcs = sorted(set([h.strip() for h in handlers if h.strip() and not h.startswith('window.')]))

print("Checking existence of handler functions:")
for fn in unique_funcs:
    # check if 'function fn' or 'const fn =' or 'let fn =' or 'var fn ='
    pattern = rf'(function\s+{re.escape(fn)}\b|\b{re.escape(fn)}\s*=\s*(?:function|\([^)]*\)\s*=>))'
    match = re.search(pattern, combined_script)
    if match:
        print(f"  [OK] {fn}")
    else:
        print(f"  [MISSING!] {fn}")
