with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, l in enumerate(lines):
    if i == 1529: # line 1530
        print('Skipping line 1530:', repr(l))
        continue
    if i == 1823: # line 1824
        print('Skipping line 1824:', repr(l))
        continue
    new_lines.append(l)

text = ''.join(new_lines)

import re
scripts = list(re.finditer(r'<script\b[^>]*>([\s\S]*?)<\/script>', text))
m = scripts[-1]
script = m.group(1)
script_start_line = text[:m.start(1)].count('\n') + 1

NORMAL = 0
IN_S_QUOTE = 1
IN_D_QUOTE = 2
IN_TEMPLATE = 3
IN_LINE_COMMENT = 4
IN_BLOCK_COMMENT = 5

state = NORMAL
template_brace_stack = []
brace_stack = []
i = 0
n = len(script)
line = 1
col = 1
errors = []

while i < n:
    c = script[i]
    next_c = script[i+1] if i + 1 < n else ''
    cur_file_line = script_start_line + line - 1
    
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
            brace_stack.append((cur_file_line, col))
        elif c == '}':
            if template_brace_stack and template_brace_stack[-1] == len(brace_stack):
                template_brace_stack.pop()
                state = IN_TEMPLATE
            if brace_stack:
                brace_stack.pop()
            else:
                errors.append(f"UNMATCHED CLOSING BRACE at {cur_file_line}:{col}")
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
            template_brace_stack.append(len(brace_stack) + 1)
            brace_stack.append((cur_file_line, col))
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

print("Remaining unclosed count:", len(brace_stack))
print("Errors count:", len(errors))
for e in errors:
    print("  ", e)
