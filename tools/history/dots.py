import sys, math, collections
import pymupdf as fitz
src=fitz.open(sys.argv[1]); p3=src[2]
def col(c): return tuple(round(x,2) for x in c) if c else None
sz=collections.Counter(); reds=[]
for p in p3.get_drawings():
    if col(p.get('fill'))==(1.0,0.0,0.0):
        r=p['rect']; sz[(round(r.width),round(r.height))]+=1; reds.append(r)
print(sz.most_common(12))
# cluster reds within 1.5pt
cl=[]
for r in reds:
    for c in cl:
        e=fitz.Rect(c); e.x0-=1.5;e.y0-=1.5;e.x1+=1.5;e.y1+=1.5
        if e.intersects(r): c|=r; break
    else: cl.append(fitz.Rect(r))
ch=True
while ch:
    ch=False
    for i in range(len(cl)):
        for j in range(i+1,len(cl)):
            e=fitz.Rect(cl[i]); e.x0-=1.5;e.y0-=1.5;e.x1+=1.5;e.y1+=1.5
            if e.intersects(cl[j]): cl[i]|=cl[j]; cl.pop(j); ch=True; break
        if ch: break
print("clusters",len(cl))
for c in sorted(cl,key=lambda c:(c.x0,c.y0)):
    if c.y1<640: print(f"  ({(c.x0+c.x1)/2:.1f},{(c.y0+c.y1)/2:.1f}) {c.width:.1f}x{c.height:.1f}")
