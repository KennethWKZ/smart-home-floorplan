import sys
import pymupdf as fitz
page = fitz.open(sys.argv[1])[2]
def col(c): return tuple(round(x, 2) for x in c) if c else None
segs = []
for p in page.get_drawings():
    if col(p.get("fill")) == (1.0, 0.5, 0.0) or col(p.get("color")) == (1.0, 0.5, 0.0):
        r = fitz.Rect(p["rect"])
        if 480 < r.x0 < 600 and 180 < r.y0 < 440: segs.append(r)
print(len(segs), "orange LED-strip marks near the TV wall")
if segs:
    u = segs[0]
    for r in segs[1:]: u |= r
    print("extent:", [round(v, 1) for v in u])
    xs = sorted({round((r.x0 + r.x1) / 2) for r in segs}); ys = sorted({round((r.y0 + r.y1) / 2) for r in segs})
    print("x centres:", xs[:12], "... y range", ys[0], ys[-1])
pix = page.get_pixmap(dpi=300, clip=fitz.Rect(470, 180, 600, 440)); pix.save(sys.argv[2])
