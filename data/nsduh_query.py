#!/usr/bin/env python3
"""Query the NSDUH detailed-tables HTML: list captions, or dump one table."""
import re, html, glob, sys
from html.parser import HTMLParser


def captions():
    out = []
    for f in sorted(glob.glob('*sect*pe.htm')):
        t = open(f, encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'<caption>(.*?)</caption>', t, re.S):
            c = html.unescape(re.sub(r'<[^>]+>', '', m.group(1)))
            out.append((f, " ".join(c.split())))
    return out


class T(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.cur, self.cell, self.intab, self.incell = [], [], [], False, False

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.intab = True
        elif tag == 'tr' and self.intab:
            self.cur = []
        elif tag in ('td', 'th') and self.intab:
            self.incell, self.cell = True, []

    def handle_endtag(self, tag):
        if tag == 'table':
            self.intab = False
        elif tag == 'tr' and self.intab:
            if self.cur:
                self.rows.append(self.cur)
            self.cur = []
        elif tag in ('td', 'th') and self.intab:
            self.cur.append(" ".join("".join(self.cell).split()))
            self.incell = False

    def handle_data(self, d):
        if self.incell:
            self.cell.append(d)


def dump(needle):
    for f in sorted(glob.glob('*sect*pe.htm')):
        t = open(f, encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'<table class="rti">(.*?)</table>', t, re.S):
            blk = m.group(1)
            cm = re.search(r'<caption>(.*?)</caption>', blk, re.S)
            if not cm:
                continue
            cap = " ".join(html.unescape(re.sub(r'<[^>]+>', '', cm.group(1))).split())
            if needle.lower() not in cap.lower():
                continue
            print("=" * 100)
            print(cap)
            print("=" * 100)
            p = T()
            p.feed("<table>" + blk + "</table>")
            for r in p.rows:
                print(" | ".join(x[:34] for x in r))
            return
    print(f"no table matching {needle!r}", file=sys.stderr)


if __name__ == '__main__':
    if sys.argv[1] == '--list':
        pat = sys.argv[2] if len(sys.argv) > 2 else ''
        for f, c in captions():
            if re.search(pat, c, re.I):
                print(f"[{f.split('sect')[1][:3]}] {c[:175]}")
    else:
        dump(sys.argv[1])
