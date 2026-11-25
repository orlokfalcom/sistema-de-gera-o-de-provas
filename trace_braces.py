with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
scripts = list(re.finditer(r'<script\b[^>]*>([\s\S]*?)<\/script>', text))
m = scripts[-1]
script = m.group(1)
script_start_line = text[:m.start(1)].count('\n') + 1
print(f"Main script starts at line {script_start_line}")

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
            brace_stack.append((cur_file_line, col, False))
        elif c == '}':
            if template_brace_stack and template_brace_stack[-1] == len(brace_stack):
                template_brace_stack.pop()
                state = IN_TEMPLATE
            if brace_stack:
                open_line, open_col, is_tpl = brace_stack.pop()
                if cur_file_line in range(1520, 1535):
                    print(f"Closing brace at file line {cur_file_line}:{col} matched opening from line {open_line}:{open_col}")
            else:
                print(f"UNMATCHED CLOSING BRACE at file line {cur_file_line}:{col}!")
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
            brace_stack.append((cur_file_line, col, True))
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

print("Remaining unclosed braces count:", len(brace_stack))
for l, c, is_tpl in brace_stack:
    print(f"  Unclosed opening from file line {l}:{c} (template={is_tpl})")
