import sys, json
from playwright.sync_api import sync_playwright
root = sys.argv[1]
JS = r"""() => {
  const m = byId("m200"), p2 = D.filter(d => d.th === "end"), ac = byId("ac-master");
  const evalAt = (x, y) => { moveDevice(m, x, y); solveZigbee();
    return { at: [x, y], p2: Object.fromEntries(p2.map(d => { const L = link({x, y}, anchor(d)); return [d.id, `${L.pl.toFixed(0)} dB ${grade(L.pl)} (${L.d.toFixed(1)} m, ${L.w} walls)`]; })),
      deepest: Math.max(...Object.values(ZB.hops)), routed: Object.keys(ZB.routes).length,
      acLoS: wallsBetween({x, y}, anchor(ac)) === 0, acDist: metres({x, y}, anchor(ac)).toFixed(1) }; };
  const central = evalAt(554, 424);
  const ms = ROOMS.find(r => r.id === "master").poly;
  const inPoly = (p, poly) => { let c = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const [xi, yi] = poly[i], [xj, yj] = poly[j]; if (((yi > p.y) !== (yj > p.y)) && (p.x < (xj - xi) * (p.y - yi) / (yj - yi) + xi)) c = !c; } return c; };
  let best = null, bs = Infinity;
  for (let y = 200; y <= 470; y += 6) for (let x = 752; x <= 926; x += 6) {
    const p = { x, y }; if (!inPoly(p, ms)) continue;
    let near = false; for (let dx = -6; dx <= 6; dx += 3) for (let dy = -6; dy <= 6; dy += 3) if (isWall(x + dx, y + dy)) near = true; if (near) continue;
    if (wallsBetween(p, anchor(ac)) > 0 || metres(p, anchor(ac)) < 1.5) continue;   // must see the AC, not sit under it
    const A = anchor(ac), ang = Math.abs(Math.atan2(p.y - A.y, p.x - A.x)) * 180 / Math.PI;
    if (ang > 55) continue;                                                           // in front of the AC (it faces +x, toward the bed)
    const worst = Math.max(...p2.map(d => link(p, anchor(d)).pl));
    if (worst < bs) { bs = worst; best = p; }
  }
  const master = evalAt(best.x, best.y);
  return { central, master };
}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto(f"file://{root}/index.html"); pg.wait_for_timeout(800)
    print(json.dumps(pg.evaluate(JS), indent=1)); b.close()
