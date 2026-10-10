import sys
import pymupdf as fitz
page = fitz.open(sys.argv[1])[1]
def col(c): return tuple(round(x,2) for x in c) if c else None
rs = [fitz.Rect(p['rect']) for p in page.get_drawings() if col(p.get('fill')) == (1.0,0.0,0.25) or (p['type']=='s' and col(p.get('color')) == (1.0,0.0,0.25))]
cl = []
for r in rs:
    if r.y0 < 150 or r.width > 30: continue
    for c in cl:
        e = fitz.Rect(c); e.x0-=2; e.y0-=2; e.x1+=2; e.y1+=2
        if e.intersects(r): c |= r; break
    else: cl.append(fitz.Rect(r))
for c in sorted(cl, key=lambda c: (c.x0, c.y0)):
    cx, cy = (c.x0+c.x1)/2, (c.y0+c.y1)/2
    if (360 < cx < 400 and 230 < cy < 260) or (900 < cx < 935 and (205 < cy < 235 or 350 < cy < 380)) or (340 < cx < 420 and 470 < cy < 490):
        print(f"({cx:.1f},{cy:.1f}) {c.width:.1f}x{c.height:.1f}")
