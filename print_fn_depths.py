with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'<script\b[^>]*>([\s\S]*?)<\/script>', text)
script = m.group(1)

# Check function definitions and brace_depth
lines = script.splitlines()

# We can run the state machine and whenever we hit line start with 'function' or 'async function', print line and brace_depth
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
script_start_line = text[:m.start(1)].count('\n') + 1

while i < n:
    c = script[i]
    next_c = script[i+1] if i + 1 < n else ''
    
    if c == '\n':
        line += 1
        col = 1
        if state == IN_LINE_COMMENT:
            state = NORMAL
        i += 1
        # Check if next line is a function definition
        rest = script[i:i+80].strip()
        if rest.startswith('function ') or rest.startswith('async function '):
            print(f"Line {script_start_line + line - 1}: {rest[:40]} | depth={brace_depth}")
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
