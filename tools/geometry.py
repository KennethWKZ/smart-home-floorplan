"""Extract plan geometry from sheet 2 (M&E) of the PDF into SVG path data (PDF pt coordinates)."""
import sys, json, math
import pymupdf as fitz
src = fitz.open(sys.argv[1]); out = sys.argv[2]
page = src[1]
CLIP = fitz.Rect(55, 160, 950, 600)          # plan area incl. walls, excl. dims/legend/title
def col(c): return tuple(round(x, 2) for x in c) if c else None
def f(v): return f"{v:.1f}".rstrip('0').rstrip('.')
def path_d(p, close_fill=False):
    d = []; cur = None
    for it in p['items']:
        k = it[0]
        if k == 'l':
            a, b = it[1], it[2]
            if cur is None or abs(cur.x - a.x) > .05 or abs(cur.y - a.y) > .05:
                d.append(f"M{f(a.x)} {f(a.y)}")
            d.append(f"L{f(b.x)} {f(b.y)}"); cur = b
        elif k == 'c':
            a, c1, c2, b = it[1:5]
            if cur is None or abs(cur.x - a.x) > .05 or abs(cur.y - a.y) > .05:
                d.append(f"M{f(a.x)} {f(a.y)}")
            d.append(f"C{f(c1.x)} {f(c1.y)} {f(c2.x)} {f(c2.y)} {f(b.x)} {f(b.y)}"); cur = b
        elif k == 're':
            r = it[1]; d.append(f"M{f(r.x0)} {f(r.y0)}H{f(r.x1)}V{f(r.y1)}H{f(r.x0)}Z"); cur = None
        elif k == 'qu':
            q = it[1]; d.append(f"M{f(q.ul.x)} {f(q.ul.y)}L{f(q.ur.x)} {f(q.ur.y)}L{f(q.lr.x)} {f(q.lr.y)}L{f(q.ll.x)} {f(q.ll.y)}Z"); cur = None
    if close_fill or p.get('closePath'): d.append("Z")
    return "".join(d)
walls, outline, furn = [], [], []
skipped = 0
for p in page.get_drawings():
    r = fitz.Rect(p['rect'])
    if not CLIP.contains(r): skipped += 1; continue
    fc, sc = col(p.get('fill')), col(p.get('color'))
    if fc in ((0.46, 0.46, 0.46), (0.5, 0.5, 0.5)):
        # dimension tick marks are small 45-degree filled slivers in the same grey
        if r.width < 7 and r.height < 7 and abs(r.width - r.height) < 1.5:
            skipped += 1; continue
        walls.append(path_d(p, True))
    elif p['type'] == 's' and sc == (0.0, 0.0, 0.0):
        # drop the stray long diagonal construction line in the kitchen
        if r.width > 100 and r.height > 5: skipped += 1; continue
        # drop dimension tick marks: a single short diagonal stroke
        its = p['items']
        if len(its) == 1 and its[0][0] == 'l':
            a, b = its[0][1], its[0][2]
            if abs(a.x - b.x) > 1 and abs(a.y - b.y) > 1 and math.hypot(a.x - b.x, a.y - b.y) < 9:
                skipped += 1; continue
        outline.append(path_d(p))
    elif p['type'] == 's' and sc == (0.6, 0.6, 0.6):
        furn.append(path_d(p))
    else:
        skipped += 1
geo = {"viewBox": [CLIP.x0, CLIP.y0, CLIP.width, CLIP.height],
       "walls": "".join(walls), "outline": "".join(outline), "furniture": "".join(furn),
       "mmPerPt": 15385 / (937.0 - 64.0)}
json.dump(geo, open(out, "w"))
print(len(walls), "walls", len(outline), "outline", len(furn), "furniture", skipped, "skipped")
print({k: len(v) for k, v in geo.items() if isinstance(v, str)})
