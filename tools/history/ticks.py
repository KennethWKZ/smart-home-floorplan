import sys, math, collections
import pymupdf as fitz
page = fitz.open(sys.argv[1])[1]
def col(c): return tuple(round(x,2) for x in c) if c else None
c = collections.Counter(); ex = []
for p in page.get_drawings():
    r = fitz.Rect(p['rect'])
    if col(p.get('color')) == (0.0,0.0,0.0) and p['type']=='s' and r.width < 12 and r.height < 12 and 160 < r.y0 < 600 and 55 < r.x0 < 950:
        c[(len(p['items']), tuple(i[0] for i in p['items']), round(p.get('width') or 0,2))] += 1
        if len(ex) < 4: ex.append((p['items'], round(r.width,1), round(r.height,1)))
print(c.most_common(10)); print(ex)
