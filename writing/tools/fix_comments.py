"""fix_comments.py TRACKED -- track_changes.py marks edits to LaTeX comment lines like prose; a % inside \\del{...} or
\\new{...} then comments out the closing brace. A struck comment is dropped and an inserted one unwrapped (comments
are not typeset)."""
import re, sys
p = sys.argv[1]
s = open(p).read()
s, n1 = re.subn(r'\\del\{(%[^{}\n]*)\}[ ]?', '', s)
s, n2 = re.subn(r'\\new\{(%[^{}]*)\}', r'\1', s)
open(p, 'w').write(s)
print(f'fix_comments: {n1} struck comments dropped, {n2} inserted comments unwrapped')
