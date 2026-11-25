with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
script_match = re.search(r'<script\b[^>]*>([\s\S]*?)<\/script>', text)
assert script_match, "No script found"

script = script_match.group(1)

# Tokenize brackets while ignoring strings and comments
i = 0
n = len(script)
line = 1
col = 1
stack = []
errors = []

while i < n:
    c = script[i]
    if c == '\n':
        line += 1
        col = 1
        i += 1
        continue

    # Single-line comment
    if c == '/' and i + 1 < n and script[i+1] == '/':
        i += 2
        while i < n and script[i] != '\n':
            i += 1
        continue

    # Multi-line comment
    if c == '/' and i + 1 < n and script[i+1] == '*':
        i += 2
        while i + 1 < n and not (script[i] == '*' and script[i+1] == '/'):
            if script[i] == '\n':
                line += 1
                col = 1
            else:
                col += 1
            i += 1
        i += 2
        col += 2
        continue

    # Strings: '...', "..."
    if c in ("'", '"'):
        quote = c
        i += 1
        col += 1
        while i < n and script[i] != quote:
            if script[i] == '\\':
                i += 2
                col += 2
            else:
                if script[i] == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
                i += 1
        i += 1
        col += 1
        continue

    # Template literal: `...`
    if c == '`':
        i += 1
        col += 1
        while i < n and script[i] != '`':
            if script[i] == '\\':
                i += 2
                col += 2
            elif script[i] == '$' and i + 1 < n and script[i+1] == '{':
                # interpolation inside template literal
                stack.append(('}', line, col, 'template_interpolation'))
                i += 2
                col += 2
                break
            else:
                if script[i] == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
                i += 1
        else:
            i += 1
            col += 1
        continue

    if c in '{[(':
        stack.append((c, line, col, 'bracket'))
    elif c in '}])':
        if not stack:
            errors.append(f"Unexpected token '{c}' at line {line}:{col}")
        else:
            top_ch, top_l, top_c, kind = stack.pop()
            expected = {'{': '}', '[': ']', '(': ')'}.get(top_ch, '')
            if c != expected and kind == 'bracket':
                errors.append(f"Mismatched '{c}' at line {line}:{col}, expected '{expected}' from {top_l}:{top_c}")

    i += 1
    col += 1

print(f"Total syntax errors found: {len(errors)}")
for err in errors:
    print("  ", err)

if stack:
    print(f"Unclosed remaining ({len(stack)}):")
    for s in stack:
        print("  ", s)
