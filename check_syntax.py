with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
script_match = re.search(r'<script\b[^>]*>([\s\S]*?)<\/script>', text)
if script_match:
    script = script_match.group(1)
    lines = script.splitlines()
    stack = []
    for line_no, line in enumerate(lines, 1):
        for col_no, ch in enumerate(line, 1):
            if ch in '{[(':
                stack.append((ch, line_no, col_no))
            elif ch in '}])':
                if not stack:
                    print(f"Unmatched closing '{ch}' at line {line_no}:{col_no}: {line}")
                else:
                    open_ch, o_line, o_col = stack.pop()
                    expected = {'{': '}', '[': ']', '(': ')'}[open_ch]
                    if ch != expected:
                        print(f"Mismatched '{ch}' at line {line_no}:{col_no}, expected '{expected}' opened at {o_line}:{o_col}")
    if stack:
        print(f"Unclosed openings remaining: {len(stack)}")
        for ch, l, c in stack[-10:]:
            print(f"  Unclosed '{ch}' opened at line {l}:{c}")
