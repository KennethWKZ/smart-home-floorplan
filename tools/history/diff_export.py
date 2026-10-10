import sys, json
from playwright.sync_api import sync_playwright
root, exp = sys.argv[1], json.load(open(sys.argv[2]))
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto(f"file://{root}/index.html"); pg.wait_for_timeout(800)
    cur = pg.evaluate("() => Object.fromEntries(D.map(d => [d.id, { a: [anchor(d).x, anchor(d).y], st: d.status, room: d.room }]))")
    rooms = pg.evaluate("(pts) => Object.fromEntries(Object.entries(pts).map(([id, q]) => [id, (ROOMS.find(r => inPoly({ x: q[0], y: q[1] }, r.poly)) || {}).id || '-']))", exp)
    b.close()
for id, q in exp.items():
    c = cur.get(id)
    if not c: print("UNKNOWN", id, q); continue
    dx, dy = q[0] - c["a"][0], q[1] - c["a"][1]
    if abs(dx) > .5 or abs(dy) > .5:
        print(f"{id:12} {c['st']:10} {c['a']} -> {q}  ({(dx*dx+dy*dy)**.5*17.639/1000:.2f} m)  room {c['room']} -> {rooms[id]}")
print("missing from export:", [k for k in cur if k not in exp])
