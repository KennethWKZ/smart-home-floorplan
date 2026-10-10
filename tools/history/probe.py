import sys, collections
import fitz
doc = fitz.open(sys.argv[1])
for pno in range(len(doc)):
    page = doc[pno]
    d = page.get_drawings()
    print(f"--- page {pno+1}: {len(d)} drawings, rect={page.rect}")
    c = collections.Counter()
    for p in d:
        key = (p.get('type'), tuple(round(x,2) for x in p['fill']) if p.get('fill') else None,
               tuple(round(x,2) for x in p['color']) if p.get('color') else None,
               round(p.get('width') or 0,2), p.get('dashes'))
        c[key]+=1
    for k,v in c.most_common(30):
        print(v, k)
    imgs = page.get_images()
    print("images:", len(imgs))
