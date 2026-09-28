"""extract_comments.py <pdf>: every markup annotation with its page, the words under it and its comment."""
import re, zlib, html, sys, subprocess
P = sys.argv[1]
d = open(P, "rb").read()
objs = {}
# IN FILE ORDER, LATEST DEFINITION WINS. A PDF saved with comments is written as
# incremental updates: a page and its /Annots are redefined later in the file,
# often inside a compressed object stream. Letting an older plain copy of an
# object win over a newer one in a stream hid 11 of 27 highlights on 28 Sep.
for m in re.finditer(rb'(\d+)\s+0\s+obj(.*?)endobj', d, re.S):
    n, body = int(m.group(1)), m.group(2)
    objs[n] = body
    if re.search(rb'/Type\s*/ObjStm', body):
        hdr = body[:body.find(b'stream')]
        N = int(re.search(rb'/N\s+(\d+)', hdr).group(1)); F = int(re.search(rb'/First\s+(\d+)', hdr).group(1))
        s = body.find(b'stream') + 6
        while body[s:s+1] in (b'\r', b'\n'): s += 1
        try: raw = zlib.decompress(body[s:body.rfind(b'endstream')])
        except Exception: continue
        pairs = list(map(int, raw[:F].split())); offs = [(pairs[i], pairs[i+1]) for i in range(0, 2*N, 2)]
        for k, (on, off) in enumerate(offs):
            end = offs[k+1][1] if k+1 < len(offs) else len(raw) - F
            objs[on] = raw[F+off:F+end]
def lit(s):
    if s.startswith(b'<'): h = bytes.fromhex(re.sub(rb'\s', b'', s[1:-1]).decode())
    else:
        b = s[1:-1]; out = bytearray(); i = 0
        while i < len(b):
            c = b[i]
            if c == 92:
                i += 1; n = b[i]
                if 48 <= n <= 55:
                    j = i; v = b''
                    while j < len(b) and j < i+3 and 48 <= b[j] <= 55: v += bytes([b[j]]); j += 1
                    out.append(int(v, 8)); i = j-1
                elif n in (13, 10): pass
                else: out += {110: b'\n', 114: b'\r', 116: b'\t'}.get(n, bytes([n]))
            else: out.append(c)
            i += 1
        h = bytes(out)
    return h[2:].decode('utf-16-be', 'replace') if h.startswith(b'\xfe\xff') else h.decode('latin-1')
STR = rb'(\((?:\\.|[^\\()]|\((?:\\.|[^\\()])*\))*\)|<[0-9A-Fa-f\s]*>)'
# page order from the page tree
root = re.search(rb'/Root\s+(\d+)\s+0\s+R', d)
cat = objs[int(root.group(1))]
def kids(n):
    o = objs[n]
    if re.search(rb'/Type\s*/Pages', o):
        out = []
        for k in re.findall(rb'(\d+)\s+0\s+R', re.search(rb'/Kids\s*\[([^\]]*)\]', o).group(1)): out += kids(int(k))
        return out
    return [n]
order = kids(int(re.search(rb'/Pages\s+(\d+)\s+0\s+R', cat).group(1)))
H = 792.0
for pi, pn in enumerate(order, 1):
    am = re.search(rb'/Annots\s*\[([^\]]*)\]', objs[pn])
    if not am:
        ar = re.search(rb'/Annots\s+(\d+)\s+0\s+R', objs[pn])
        if not ar: continue
        am = re.search(rb'\[([^\]]*)\]', objs[int(ar.group(1))])
    refs = [int(x) for x in re.findall(rb'(\d+)\s+0\s+R', am.group(1))]
    marks = [r for r in refs if r in objs and re.search(rb'/Subtype\s*/(Highlight|StrikeOut|Underline|Squiggly|Text|FreeText|Caret)', objs[r])]
    if not marks: continue
    bb = subprocess.run(['pdftotext', '-f', str(pi), '-l', str(pi), '-bbox', P, '-'], capture_output=True, text=True).stdout
    words = [(float(a), H-float(b), float(c), H-float(e), html.unescape(w)) for a, b, c, e, w in
             re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', bb)]
    for r in marks:
        o = objs[r]
        st = re.search(rb'/Subtype\s*/(\w+)', o).group(1).decode()
        cm = re.search(rb'/Contents\s*' + STR, o)
        q = re.search(rb'/QuadPoints\s*\[([^\]]*)\]', o)
        under = []
        if q:
            nums = [float(x) for x in q.group(1).split()]
            for i in range(0, len(nums), 8):
                xs = nums[i:i+8:2]; ys = nums[i+1:i+8:2]
                for (a, b, c, e, w) in words:
                    if min(xs)-1 <= (a+c)/2 <= max(xs)+1 and min(ys)-1 <= (b+e)/2 <= max(ys)+1: under.append(w)
        else:
            rc = re.search(rb'/Rect\s*\[([^\]]*)\]', o); nums = [float(x) for x in rc.group(1).split()]
            near = sorted(words, key=lambda w: abs((w[0]+w[2])/2-nums[0])+abs((w[1]+w[3])/2-nums[1]))[:6]
            under = ["[near: " + " ".join(w[4] for w in near) + "]"]
        pos = ""
        if q:
            pos = f" [x {min(nums[0::2]):.0f}-{max(nums[0::2]):.0f}, y {min(nums[1::2]):.0f}-{max(nums[1::2]):.0f}]"
        print(f"p{pi} {st}{pos}: «{' '.join(under)}»\n     -> {lit(cm.group(1)) if cm else '(no comment)'}\n")
