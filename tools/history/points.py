import sys, json, math
import pymupdf as fitz
src=fitz.open(sys.argv[1])
def col(c): return tuple(round(x,2) for x in c) if c else None
def spans(page):
    res=[]
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines",[]):
            for s in l["spans"]:
                t=s["text"].strip()
                if not t: continue
                c=s["color"]; rgb=((c>>16)&255,(c>>8)&255,c&255)
                x0,y0,x1,y1=s["bbox"]; res.append((t,rgb,(x0+x1)/2,(y0+y1)/2,s["size"]))
    return res
p3=src[2]; d3=p3.get_drawings()
dots=[]
for p in d3:
    f=col(p.get('fill'))
    if f==(1.0,0.0,0.0):
        r=p['rect']
        if 3<r.width<9 and 3<r.height<9 and abs(r.width-r.height)<1.5:
            dots.append(((r.x0+r.x1)/2,(r.y0+r.y1)/2,r.width))
# dedupe
ud=[]
for x,y,w in dots:
    if all(math.hypot(x-a,y-b)>2 for a,b,_ in ud): ud.append((x,y,w))
labels=[s for s in spans(p3) if s[1]==(255,0,0) and s[0] in ('1G','2G','3G','4G')]
print("dots",len(ud))
for x,y,w in sorted(ud,key=lambda t:(t[0],t[1])):
    near=sorted(labels,key=lambda s:math.hypot(s[2]-x,s[3]-y))[:2]
    print(f"  dot ({x:.1f},{y:.1f}) w={w:.1f} nearest:",[(s[0],round(s[2],1),round(s[3],1),round(math.hypot(s[2]-x,s[3]-y),1)) for s in near])
p2=src[1]
print("CAT6 / room text p2:")
for t,rgb,x,y,sz in spans(p2):
    if 'CAT' in t or rgb in ((152,152,152),) or t in ('LIVING','DINING','FOYER','KITCHEN','YARD','A/C','ISLAND'):
        if y<640: print(f"  {t!r} {rgb} ({x:.1f},{y:.1f}) sz={sz:.1f}")
print("orange LED clusters p3 (fill 1,0.5,0 dashes):")
pts=[]
for p in d3:
    if col(p.get('fill'))==(1.0,0.5,0.0) or col(p.get('color'))==(1.0,0.5,0.0):
        pts.append(fitz.Rect(p['rect']))
# group into runs by connectivity with gap 8
groups=[]
for r in pts:
    placed=None
    for g in groups:
        e=fitz.Rect(g); e.x0-=8;e.y0-=8;e.x1+=8;e.y1+=8
        if e.intersects(r): g|=r; placed=True; break
    if not placed: groups.append(fitz.Rect(r))
ch=True
while ch:
    ch=False
    for i in range(len(groups)):
        for j in range(i+1,len(groups)):
            e=fitz.Rect(groups[i]); e.x0-=8;e.y0-=8;e.x1+=8;e.y1+=8
            if e.intersects(groups[j]): groups[i]|=groups[j]; groups.pop(j); ch=True; break
        if ch: break
for g in groups:
    if g.width>8 or g.height>8: print("  ",[round(v,1) for v in g])
print("fans / misc p3 text:")
for t,rgb,x,y,sz in spans(p3):
    if t in ('F01','F02','F03','L08','L25','L29','L30','L31','L27','L32','L33','L34','L12','L11','L14','L16'): print(f"  {t} {rgb} ({x:.1f},{y:.1f})")
