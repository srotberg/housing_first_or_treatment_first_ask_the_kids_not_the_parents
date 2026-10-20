"""ai_chunks.py -- the paper cut for AI detectors (20 October; the author: "split the paper into 4 equal parts ... so i can
feed it to AI detectors", then "i need to break it down the 2000 words at a time").

    python3 writing/tools/ai_chunks.py

From writing/children_first_housing_later.pdf, writes writing/ai_check/chunks_2000/chunk<nn>.pdf and .txt: the text in
chunks of at most 2,000 words, cut between paragraphs, the reference list left out. (The four parts of the first request
were removed from the repo on the author's request, 20 October.)
The text is the PDF's own, with words hyphenated across lines rejoined; equations, footnotes and tables come through
as plain text where they fall on the page. Run it again whenever the paper changes."""
import html, os, re
import pymupdf

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC = os.path.join(ROOT, 'writing', 'children_first_housing_later.pdf')
OUT = os.path.join(ROOT, 'writing', 'ai_check')
LIMIT = 2000
doc = pymupdf.open(SRC)

# chunks of at most LIMIT words, between paragraphs, up to the reference list
paras, stop = [], False
for p in doc:
    for b in p.get_text('blocks', flags=pymupdf.TEXT_DEHYPHENATE | pymupdf.TEXT_PRESERVE_WHITESPACE):
        if b[6] != 0:
            continue
        t = ' '.join(b[4].split())
        if t == 'References':
            stop = True
            break
        if t and not re.fullmatch(r'\d+', t):          # page numbers out
            paras.append(t)
    if stop:
        break
units = []
for t in paras:                                         # a paragraph over the limit is cut between sentences
    if len(t.split()) <= LIMIT:
        units.append(t)
        continue
    cur = []
    for s in re.split(r'(?<=[.!?])\s+', t):
        if cur and len(' '.join(cur + [s]).split()) > LIMIT:
            units.append(' '.join(cur)); cur = []
        cur.append(s)
    units.append(' '.join(cur))
chunks, cur, n = [], [], 0
for u in units:
    k = len(u.split())
    if cur and n + k > LIMIT:
        chunks.append(cur); cur, n = [], 0
    cur.append(u); n += k
if cur:
    chunks.append(cur)
CH = os.path.join(OUT, 'chunks_2000')
os.makedirs(CH, exist_ok=True)
for f in os.listdir(CH):
    os.remove(os.path.join(CH, f))
for i, c in enumerate(chunks, 1):
    base = os.path.join(CH, f'chunk{i:02d}')
    open(base + '.txt', 'w').write('\n\n'.join(c) + '\n')
    story = pymupdf.Story('<body style="font-family: serif; font-size: 11pt;">' +
                          ''.join(f'<p>{html.escape(x)}</p>' for x in c) + '</body>')
    wr = pymupdf.DocumentWriter(base + '.pdf')
    box = pymupdf.paper_rect('letter'); where = box + (72, 72, -72, -72)
    more = 1
    while more:
        dev = wr.begin_page(box); more, _ = story.place(where); story.draw(dev); wr.end_page()
    wr.close()
    print(f'chunk{i:02d}: {sum(len(x.split()) for x in c)} words')
