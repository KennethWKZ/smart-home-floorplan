import sys
import pymupdf as fitz
src = fitz.open(sys.argv[1]); outdir=sys.argv[2]
def col(c): return tuple(round(x,2) for x in c) if c else None
def draw(shape, p):
    for it in p['items']:
        k=it[0]
        if k=='l': shape.draw_line(it[1],it[2])
        elif k=='c': shape.draw_bezier(it[1],it[2],it[3],it[4])
        elif k=='re': shape.draw_rect(it[1])
        elif k=='qu': shape.draw_quad(it[1])
for pno in (0,1,2):
    page=src[pno]; d=page.get_drawings()
    walls=[p for p in d if p.get('fill') and col(p['fill']) in ((0.46,0.46,0.46),(0.5,0.5,0.5))]
    import functools
    r=functools.reduce(lambda a,b:a|b,[fitz.Rect(p['rect']) for p in walls])
    print("page",pno+1,"walls",len(walls),"bbox",[round(v,1) for v in r])
# render category preview for page 2 (M&E) region
page=src[1]; d=page.get_drawings()
out=fitz.open(); np_=out.new_page(width=1191,height=842)
cats={
 'g06s':((0.6,0.6,0.6),None,'#999'),
 'g046s':((0.46,0.46,0.46),None,'#0a0'),
 'blk':((0.0,0.0,0.0),None,'#00f'),
}
for p in d:
    c=col(p.get('color')); f=col(p.get('fill'))
    sh=np_.new_shape()
    draw(sh,p)
    if f in ((0.46,0.46,0.46),(0.5,0.5,0.5)): sh.finish(fill=(0.2,0.2,0.2),color=None)
    elif p['type']=='s' and c==(0.6,0.6,0.6): sh.finish(color=(0.6,0.6,0.6),width=0.4)
    elif p['type']=='s' and c==(0.46,0.46,0.46): sh.finish(color=(0,0.7,0),width=0.6)
    elif p['type']=='s' and c==(0,0,0): sh.finish(color=(0,0,1),width=p.get('width') or 0.5)
    elif f and f[0]>0.9 and f[1]<0.1: sh.finish(fill=(1,0,0),color=None)
    else: sh.finish(color=(1,0,1),width=0.5)
    sh.commit()
pix=np_.get_pixmap(dpi=110, clip=fitz.Rect(40,120,1000,640)); pix.save(outdir+"/cat-p2.png")
