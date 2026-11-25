with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove line 1530 (index 1529) and line 1824 (index 1823)
# Note: after deleting 1529, index 1823 becomes 1822
print("Line 1530 to remove:", repr(lines[1529]))
print("Line 1824 to remove:", repr(lines[1823]))
