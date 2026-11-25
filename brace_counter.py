with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Let's count open and close braces in each top-level function
open_braces = 0
for idx, line in enumerate(lines[1140:], 1141):
    # remove strings
    clean = line
    # simple clean of comments
    if '//' in clean:
        clean = clean[:clean.index('//')]
    
    # count braces
    for ch in clean:
        if ch == '{':
            open_braces += 1
        elif ch == '}':
            open_braces -= 1
            if open_braces < 0:
                print(f"Negative brace count at line {idx}: {line.strip()} (count={open_braces})")
                open_braces = 0

print("Final open_braces count at end of script:", open_braces)
