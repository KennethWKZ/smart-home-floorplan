"""Screenshot a plan region with a 10 pt grid: region.py <repo> <out.png> x0 y0 x1 y1"""
import sys
from playwright.sync_api import sync_playwright
root, out = sys.argv[1], sys.argv[2]; x0, y0, x1, y1 = map(float, sys.argv[3:7])
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1600, "height": 1200}, device_scale_factor=5, color_scheme="light")
    pg.goto(f"file://{root}/index.html"); pg.wait_for_timeout(700)
    clip = pg.evaluate("""([x0,y0,x1,y1]) => {
      const s = document.querySelector('#plan'), ns = 'http://www.w3.org/2000/svg', g = document.createElementNS(ns, 'g'); s.appendChild(g);
      const line = (a, w) => { const l = document.createElementNS(ns,'line'); Object.entries(a).forEach(([k,v]) => l.setAttribute(k,v)); l.setAttribute('stroke', '#0a0'); l.setAttribute('stroke-width', w); g.appendChild(l); };
      const text = (x, y, t) => { const e = document.createElementNS(ns,'text'); e.setAttribute('x',x); e.setAttribute('y',y); e.setAttribute('font-size',3); e.setAttribute('fill','#070'); e.textContent=t; g.appendChild(e); };
      for (let x = Math.ceil(x0/10)*10; x <= x1; x += 10) { line({x1:x,x2:x,y1:y0,y2:y1}, x%50?0.12:0.35); text(x+0.4, y0+3.5, x); }
      for (let y = Math.ceil(y0/10)*10; y <= y1; y += 10) { line({x1:x0,x2:x1,y1:y,y2:y}, y%50?0.12:0.35); text(x0+0.4, y-0.4, y); }
      const m = s.getScreenCTM(), P = (x,y) => new DOMPoint(x,y).matrixTransform(m), a = P(x0,y0), c = P(x1,y1);
      return { x: a.x + scrollX, y: a.y + scrollY, width: c.x - a.x, height: c.y - a.y };
    }""", [x0, y0, x1, y1])
    pg.wait_for_timeout(200); pg.screenshot(path=out, clip=clip, full_page=True); b.close()
