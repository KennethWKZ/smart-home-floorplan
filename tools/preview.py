import sys, json
geo = json.load(open(sys.argv[1])); out = sys.argv[2]
x, y, w, h = geo["viewBox"]
grid = []
for gx in range(int(x)//10*10, int(x+w)+1, 10):
    major = gx % 50 == 0
    grid.append(f'<line x1="{gx}" y1="{y}" x2="{gx}" y2="{y+h}" stroke="{"#f55" if major else "#fcc"}" stroke-width="{0.3 if major else 0.15}"/>')
    if major: grid.append(f'<text x="{gx+0.5}" y="{y+5}" font-size="4" fill="#d00">{gx}</text>')
for gy in range(int(y)//10*10, int(y+h)+1, 10):
    major = gy % 50 == 0
    grid.append(f'<line x1="{x}" y1="{gy}" x2="{x+w}" y2="{gy}" stroke="{"#f55" if major else "#fcc"}" stroke-width="{0.3 if major else 0.15}"/>')
    if major: grid.append(f'<text x="{x+0.5}" y="{gy-0.5}" font-size="4" fill="#d00">{gy}</text>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{w*3}" height="{h*3}">
<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff"/>{''.join(grid)}
<path d="{geo['furniture']}" fill="none" stroke="#aaa" stroke-width="0.3"/>
<path d="{geo['outline']}" fill="none" stroke="#000" stroke-width="0.5"/>
<path d="{geo['walls']}" fill="#333"/></svg>'''
open(out, "w").write(svg)
