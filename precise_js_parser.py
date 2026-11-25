with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'<script\b[^>]*>([\s\S]*?)<\/script>', text)
script = m.group(1)

# State machine
NORMAL = 0
IN_S_QUOTE = 1
IN_D_QUOTE = 2
IN_TEMPLATE = 3
IN_LINE_COMMENT = 4
IN_BLOCK_COMMENT = 5

state = NORMAL
template_brace_stack = []
brace_depth = 0
i = 0
n = len(script)
line = 1
col = 1

while i < n:
    c = script[i]
    next_c = script[i+1] if i + 1 < n else ''
    
    if c == '\n':
        line += 1
        col = 1
        if state == IN_LINE_COMMENT:
            state = NORMAL
        i += 1
        continue
    else:
        col += 1
    
    if state == NORMAL:
        if c == '/' and next_c == '/':
            state = IN_LINE_COMMENT
            i += 2
            continue
        elif c == '/' and next_c == '*':
            state = IN_BLOCK_COMMENT
            i += 2
            continue
        elif c == "'":
            state = IN_S_QUOTE
        elif c == '"':
            state = IN_D_QUOTE
        elif c == '`':
            state = IN_TEMPLATE
        elif c == '{':
            brace_depth += 1
        elif c == '}':
            if template_brace_stack and template_brace_stack[-1] == brace_depth:
                template_brace_stack.pop()
                state = IN_TEMPLATE
            brace_depth -= 1
            if brace_depth < 0:
                print(f"ERROR: Extra closing brace '}}' at line {line}:{col}")
                brace_depth = 0
    elif state == IN_S_QUOTE:
        if c == '\\':
            i += 2
            continue
        elif c == "'":
            state = NORMAL
    elif state == IN_D_QUOTE:
        if c == '\\':
            i += 2
            continue
        elif c == '"':
            state = NORMAL
    elif state == IN_TEMPLATE:
        if c == '\\':
            i += 2
            continue
        elif c == '$' and next_c == '{':
            state = NORMAL
            template_brace_stack.append(brace_depth + 1)
            brace_depth += 1
            i += 2
            continue
        elif c == '`':
            state = NORMAL
    elif state == IN_BLOCK_COMMENT:
        if c == '*' and next_c == '/':
            state = NORMAL
            i += 2
            continue
            
    i += 1

print(f"End of script. brace_depth = {brace_depth}")
if brace_depth != 0:
    print(f"ERROR: Unbalanced braces at end of script: {brace_depth}")
