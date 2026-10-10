import sys, json
import pymupdf as fitz
doc = fitz.open(sys.argv[1])
def col(c): return tuple(round(x,2) for x in c) if c else None
out = {}
for pno in (1,2):
    page = doc[pno]
    td = page.get_text("dict")
    spans=[]
    for b in td["blocks"]:
        for l in b.get("lines",[]):
            for s in l["spans"]:
                t=s["text"].strip()
                if not t: continue
                c=s["color"]; rgb=((c>>16)&255,(c>>8)&255,c&255)
                x0,y0,x1,y1=s["bbox"]
                if x0>1000 and y0<200: continue  # legend
                if y0>700: continue  # title block
                spans.append((t, rgb, round((x0+x1)/2,1), round((y0+y1)/2,1)))
    print(f"=== page {pno+1} text ({len(spans)})")
    for t,rgb,x,y in sorted(spans,key=lambda s:(s[1],s[3],s[2])):
        if rgb==(0,0,0) or rgb==(128,128,128) or rgb==(117,117,117): continue
        print(f"{t!r:28} {rgb} ({x},{y})")
    d = page.get_drawings()
    if pno==2:
        dots=[p for p in d if p.get('fill') and col(p['fill'])==(0.87,0.0,0.0)]
        print("=== switch dots (0.87 red fill)", len(dots))
        for p in dots:
            r=p['rect']; print(f"  ({round((r.x0+r.x1)/2,1)},{round((r.y0+r.y1)/2,1)}) w={round(r.width,1)}")
        for name,c in [("orange-fill",(1.0,0.5,0.0)),("purple",(0.75,0.5,1.0)),("violet",(0.5,0.0,1.0)),("green",(0.26,0.6,0.08))]:
            items=[p for p in d if col(p.get('fill')) ==c or col(p.get('color'))==c]
            # cluster by proximity
            rects=[fitz.Rect(p['rect']) for p in items]
            clusters=[]
            for r in rects:
                rr=fitz.Rect(r)
                for cl in clusters:
                    g=fitz.Rect(cl); g.x0-=12; g.y0-=12; g.x1+=12; g.y1+=12
                    if g.intersects(rr) or g.contains(rr):
                        cl|=rr; break
                else: clusters.append(rr)
            # merge pass
            changed=True
            while changed:
                changed=False
                for i in range(len(clusters)):
                    for j in range(i+1,len(clusters)):
                        g=fitz.Rect(clusters[i]); g.x0-=12; g.y0-=12; g.x1+=12; g.y1+=12
                        if g.intersects(clusters[j]):
                            clusters[i]|=clusters[j]; clusters.pop(j); changed=True; break
                    if changed: break
            print(f"=== {name}: {len(items)} items, {len(clusters)} clusters")
            for cl in clusters: print("  ", [round(v,1) for v in cl])
