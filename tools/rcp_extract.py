"""Trace the switching layout from the RCP (sheet 3) into build/rcp.json.

Sheet 3 shares the plan's coordinate frame (the H1 positions came from its switch dots), so paths are copied as-is.
Output: fixture paths by type, the red dashed switch legs grouped into chains, each chain tagged with the
circuit labels (L01, F02, ...) it rings, and the label positions.
usage: rcp_extract.py <drawings.pdf> <out.json>
"""
import json, math, re, sys
import pymupdf as fitz

BOX = (65, 190, 937, 592)          # apartment outline in plan points
GAP = 3.2                          # dash gap on the RCP: segments closer than this belong to one chain

src, out = sys.argv[1], sys.argv[2]
page = fitz.open(src)[2]

def rgb(c): return tuple(round(v, 2) for v in c) if c else None
def inside(r): return r.x1 >= BOX[0] and r.x0 <= BOX[2] and r.y1 >= BOX[1] and r.y0 <= BOX[3]
def f(v): return f"{v:.1f}".rstrip("0").rstrip(".")

def to_d(items):
    d, cur = [], None
    for it in items:
        k = it[0]
        if k == "l":
            a, b = it[1], it[2]
            if cur is None or math.hypot(cur.x - a.x, cur.y - a.y) > .05: d.append(f"M{f(a.x)} {f(a.y)}")
            d.append(f"L{f(b.x)} {f(b.y)}"); cur = b
        elif k == "c":
            a, c1, c2, b = it[1], it[2], it[3], it[4]
            if cur is None or math.hypot(cur.x - a.x, cur.y - a.y) > .05: d.append(f"M{f(a.x)} {f(a.y)}")
            d.append(f"C{f(c1.x)} {f(c1.y)} {f(c2.x)} {f(c2.y)} {f(b.x)} {f(b.y)}"); cur = b
        elif k == "re":
            r = it[1]; d.append(f"M{f(r.x0)} {f(r.y0)}H{f(r.x1)}V{f(r.y1)}H{f(r.x0)}Z"); cur = None
        elif k == "qu":
            q = it[1]; d.append(f"M{f(q.ul.x)} {f(q.ul.y)}L{f(q.ur.x)} {f(q.ur.y)}L{f(q.lr.x)} {f(q.lr.y)}L{f(q.ll.x)} {f(q.ll.y)}Z"); cur = None
    return "".join(d)

# stroke / fill colour -> fixture class (from the RCP legend colours)
FIXTURE = {
    (0.0, 0.25, 1.0): "pc",       # recessed downlights (PC)
    (0.0, 0.22, 0.87): "pc",
    (1.0, 0.5, 0.0): "led",       # LED strip runs (orange dashes)
    (0.26, 0.6, 0.08): "t5",      # T5 / cove lines (green dashes)
    (0.75, 0.5, 1.0): "wall",     # wall lights and pendants (purple)
    (0.0, 0.5, 1.0): "fan",       # ceiling fan (blue)
}
fixtures = {}                      # "<class>_f" filled, "<class>_s" stroked
legs = []                          # (path, endpoints)
for p in page.get_drawings():
    r = p["rect"]
    if not inside(r): continue
    col, fill = rgb(p.get("color")), rgb(p.get("fill"))
    if col == (0.87, 0.0, 0.0) and fill is None:
        pts = []
        for it in p["items"]:
            if it[0] == "l": pts += [it[1], it[2]]
            elif it[0] == "c": pts += [it[1], it[4]]
        legs.append((to_d(p["items"]), pts, r))
        continue
    key = fill if fill in FIXTURE else col if col in FIXTURE else None
    if key: fixtures.setdefault(FIXTURE[key] + ("_f" if fill in FIXTURE else "_s"), []).append(to_d(p["items"]))

# chain the dashes: union-find on endpoint proximity
parent = list(range(len(legs)))
def find(i):
    while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
    return i
ends = [(i, q) for i, (_, pts, _) in enumerate(legs) for q in pts]
cell = {}
for i, q in ends: cell.setdefault((int(q.x // GAP), int(q.y // GAP)), []).append((i, q))
for i, q in ends:
    cx, cy = int(q.x // GAP), int(q.y // GAP)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for j, w in cell.get((cx + dx, cy + dy), []):
                if j != i and math.hypot(q.x - w.x, q.y - w.y) <= GAP: parent[find(i)] = find(j)

# circuit labels (red text inside the dashed rings)
labels = []
for b in page.get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        for s in l["spans"]:
            t = s["text"].strip(); c = s["color"]
            if (c >> 16 & 255, c >> 8 & 255, c & 255) != (221, 0, 0) or not re.fullmatch(r"[LF]\d{2}", t): continue
            x0, y0, x1, y1 = s["bbox"]; x, y = (x0 + x1) / 2, (y0 + y1) / 2
            if BOX[0] <= x <= BOX[2] and BOX[1] <= y <= BOX[3]: labels.append({"t": t, "x": round(x, 1), "y": round(y, 1)})

groups = {}
for i, (d, pts, r) in enumerate(legs): groups.setdefault(find(i), []).append(i)
chains = []
for g in groups.values():
    pts = [q for i in g for q in legs[i][1]]
    # a chain belongs to a label when it rings it: dash points on several sides within ~12 pt
    tags = []
    for L in labels:
        near = [q for q in pts if math.hypot(q.x - L["x"], q.y - L["y"]) <= 12]
        if len(near) >= 4 and max(q.x for q in near) > L["x"] + 3 and min(q.x for q in near) < L["x"] - 3: tags.append(L["t"])
    step = max(1, len(pts) // 60)    # sample points: the switch links attach to the nearest one
    chains.append({"c": sorted(set(tags)), "d": "".join(legs[i][0] for i in g), "n": len(g),
                   "p": [[round(q.x, 1), round(q.y, 1)] for q in pts[::step]]})

json.dump({"fixtures": {k: "".join(v) for k, v in fixtures.items()}, "chains": chains, "labels": labels},
          open(out, "w"), separators=(",", ":"))
tagged = [c for c in chains if c["c"]]
print(f"legs {len(legs)} -> chains {len(chains)} ({len(tagged)} tagged, {sum(len(c['c']) > 1 for c in chains)} multi) | labels {len(labels)}")
print("fixture paths:", {k: len(v) for k, v in fixtures.items()})
print("tags:", sorted({t for c in chains for t in c["c"]}))
print("untagged chains by size:", sorted((c["n"] for c in chains if not c["c"]), reverse=True)[:15])
print("multi:", [c["c"] for c in chains if len(c["c"]) > 1])
