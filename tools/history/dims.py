import sys
import pymupdf as fitz
src=fitz.open(sys.argv[1]); page=src[1]
def col(c): return tuple(round(x,2) for x in c) if c else None
segs=[]
for p in page.get_drawings():
    if p['type']=='s' and col(p.get('color'))==(0.46,0.46,0.46):
        for it in p['items']:
            if it[0]=='l':
                a,b=it[1],it[2]
                segs.append((round(a.x,1),round(a.y,1),round(b.x,1),round(b.y,1)))
top=[s for s in segs if s[1]<175 and s[3]<175 and abs(s[1]-s[3])<0.2 and abs(s[0]-s[2])>3]
left=[s for s in segs if s[0]<60 and s[2]<60 and abs(s[0]-s[2])<0.2 and abs(s[1]-s[3])>3]
bot=[s for s in segs if s[1]>600 and s[3]>600 and s[1]<640 and abs(s[1]-s[3])<0.2 and abs(s[0]-s[2])>3]
for name,ss in (("top",top),("left",left),("bottom",bot)):
    print(name); 
    for s in sorted(ss,key=lambda s:(s[1],s[0]) if name!='left' else (s[0],s[1])): print("  ",s)
nums=[]
for b in page.get_text("dict")["blocks"]:
    for l in b.get("lines",[]):
        for s in l["spans"]:
            t=s["text"].strip()
            if t.isdigit():
                x0,y0,x1,y1=s["bbox"]; cx,cy=(x0+x1)/2,(y0+y1)/2
                if cy<175 or cx<60 or (600<cy<640): nums.append((t,round(cx,1),round(cy,1)))
print(sorted(nums,key=lambda n:(n[2],n[1])))
