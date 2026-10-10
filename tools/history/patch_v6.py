"""v6: HomePod mini at the dining socket, ASUS Wi-Fi 7 AiMesh, Aqara H2 outlets as Thread routers."""
import pathlib, sys
p = pathlib.Path(sys.argv[1]); s = p.read_text()

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:100], s.count(old))
    s = s.replace(old, new)

def splice(start, end, new, keep_end=True):
    """Replace s[start_marker : end_marker) with new (end marker kept)."""
    global s
    a = s.index(start); b = s.index(end, a + len(start))
    assert s.count(start) == 1, ("start not unique", start[:60])
    s = s[:a] + new + (s[b:] if keep_end else s[b + len(end):])

# ---------- storage keys / state
for a, b in (('store.get("pos-v5")', 'store.get("pos-v6")'), ('store.set("pos-v5",', 'store.set("pos-v6",'), ('store.del("pos-v5")', 'store.del("pos-v6")')):
    rep(a, b)
rep('const state = { view: "master", sel: null, wallLoss: 12, paused: false, vb: VB_FULL.slice() };',
    'const state = { view: "master", sel: null, wallLoss: 12, threadMerged: false, paused: false, vb: VB_FULL.slice() };')
rep('const wl = store.get("wallLoss"); if (typeof wl === "number") state.wallLoss = wl;',
    'const wl = store.get("wallLoss"); if (typeof wl === "number") state.wallLoss = wl;\n  if (store.get("threadMerged") === true) state.threadMerged = true;')

# ---------- CSS
rep('#plan .pkt-th { fill: var(--th); }', '''#plan .pkt-th { fill: var(--th); }
#plan .th-mesh { stroke: var(--th); stroke-width: .45; opacity: .35; fill: none; stroke-dasharray: 1 1.6; }
#plan .th-tag { fill: var(--th-ink); font-size: 4.4px; font-weight: 500; text-anchor: middle; paint-order: stroke; stroke: var(--sheet); stroke-width: 1.8px; }
#plan .dev.th-router .collar.th { stroke-width: 1.4; }
#plan .dev.th-apple .collar.th { stroke-dasharray: 3 1.6; }
#plan .wf-assoc { stroke: var(--wf); stroke-width: .7; fill: none; stroke-dasharray: 1.2 1.6; opacity: .85; }
#plan .wf-assoc.marginal { stroke: var(--warn); }
#plan .wf-assoc.weak { stroke: var(--ir); }
#plan .pkt-wf { fill: var(--wf); }
#plan .wf-tag { fill: var(--wf-ink); font-size: 4.4px; font-weight: 600; text-anchor: middle; paint-order: stroke; stroke: var(--sheet); stroke-width: 1.8px; }''')
rep('#plan[data-view="thread"] .dev.th-br .collar.th, #plan[data-view="thread"] .dev.th-end .collar.th,',
    '#plan[data-view="thread"] .dev.th-br .collar.th, #plan[data-view="thread"] .dev.th-end .collar.th, #plan[data-view="thread"] .dev.th-router .collar.th,')
rep('#plan .pkt-zb, #plan .pkt-zb-ring, #plan .pkt-th { display: none; }', '#plan .pkt-zb, #plan .pkt-zb-ring, #plan .pkt-th, #plan .pkt-wf { display: none; }')
rep('.tray strong {', '.tray[hidden] { display: none; }\n.tray strong {')

# ---------- device facts touched by the new kit
rep('eth: "Ethernet + PoE: the desk CAT6 point is in this room (optional)"', 'eth: "Ethernet optional: a spare LAN port on the Gaming BT8, or the room\'s second CAT6 point"')
rep('note: "If the final spot is within cable reach of the desk CAT6 point, use Ethernet: PoE can power it too." });',
    'note: "For Ethernet, use a spare LAN port on the Gaming BT8 (2.5G LAN + 2 × 1G LAN). The BT8\'s spec lists no PoE, so power the M200 over USB-C." });')
rep('note: "Wi-Fi 2.4 GHz only and there\'s no CAT6 point in Master, so it runs on Wi-Fi. Any spot works if it has a socket and a clear view of the AC\'s front." });',
    'note: "Wi-Fi 2.4 GHz only and there\'s no CAT6 point in Master, so it runs on Wi-Fi. The window-side bedside H2\'s USB-C port can power it (USB-C to Micro-USB cable); keep that USB port switched on." });')

rep('\n// Thread / Matter sensors', r'''
// Aqara Wall Outlet H2 UK in Matter (Thread) mode, at M&E socket points: mains-powered Thread routers
const H2 = (id, x, y, room, short, where) => add({ id, kind: "outlet", cap: "H2", short, name: `Aqara Wall Outlet H2 · ${short}`, x, y, room, status: "drawing",
  th: "router", nets: ["thread", "matter"], loads: where,
  roles: "Matter-over-Thread outlet · mains powered, so expected to act as a Thread router (not on Zigbee)",
  source: "Owner: Aqara Wall Outlet H2, used via Matter. Socket position from the M&E sheet" });
H2("h2-sofa", 381, 243, "living", "sofa", "Floor socket under the Living sofa (marked ON FLOOR on the M&E sheet)");
H2("h2-bed-w", 919.5, 218, "master", "bed, window side", "Bedside socket, window side (HT 600 mm)");
H2("h2-bed-d", 919.5, 366, "master", "bed, door side", "Bedside socket, door side (HT 600 mm)");
byId("h2-sofa").note = "A floor box takes the H2 only if it fits a 146 × 86 mm wall-outlet module at least 25 mm deep. A metal floor-box lid over it will cut its radio.";

// Apple Home and the Wi-Fi 7 mesh
add({ id: "homepod", kind: "homepod", cap: "HomePod", short: "HomePod mini", name: "HomePod mini", x: 357, y: 479, room: "living", status: "owner",
  th: "br", apple: true, wifi: "Wi-Fi · 2.4 / 5 GHz", nets: ["thread", "wifi", "matter"],
  roles: "Apple Home hub · Thread Border Router (Apple's Thread network) · Matter controller",
  source: "Owner: on a plug-point mount at the dining-table socket (HT 800 mm on the M&E sheet)",
  note: "It doesn't replace the M200 for Aqara automations. It only carries Aqara's P2s and H2s if it and the M200 run one Thread network." });
add({ id: "ap-main", kind: "ap", cap: "RT-BE92U", short: "RT-BE92U", name: "ASUS RT-BE92U · main router", x: 542, y: 300, room: "living", status: "owner",
  ap: true, wifi: "Wi-Fi 7 · tri-band", nets: ["wifi"],
  roles: "Main router where the fibre comes in · AiMesh router · BE9700, 2.4 / 5 / 6 GHz",
  source: "Owner: in the TV-area cabinet, where the fibre comes in (beside the Living CAT6 point on the M&E sheet)",
  note: "Inside a closed cabinet or behind the TV, Wi-Fi drops noticeably. Leave the front open or vented, with the four antennas up and clear of the TV's metal bracket." });
add({ id: "ap-bed2", kind: "ap", cap: "BT8", short: "Bedroom 2 BT8", name: "ASUS ZenWiFi BT8 · Bedroom 2", x: 252, y: 238, room: "bed2", status: "proposed",
  ap: true, wifi: "Wi-Fi 7 · tri-band", nets: ["wifi"],
  roles: "AiMesh node on CAT6 backhaul · BE14000, 2.4 / 5 / 6 GHz",
  source: "Owner: a CAT6 run was added to Bedroom 2 (not on the drawings). Placed at the 300 mm socket on the Living-side wall; drag it to the real CAT6 point",
  note: "Networking, not an Aqara device, so Bedroom 2 stays 'No Aqara devices planned'." });
add({ id: "ap-gm", kind: "ap", cap: "BT8", short: "Gaming BT8", name: "ASUS ZenWiFi BT8 · Gaming", x: 712, y: 236, room: "bed1", status: "owner",
  ap: true, wifi: "Wi-Fi 7 · tri-band", nets: ["wifi"],
  roles: "AiMesh node on CAT6 backhaul · BE14000, 2.4 / 5 / 6 GHz",
  source: "Owner: on one of the Gaming room's two CAT6 points. Placed at the desk CAT6 point on the M&E sheet; the second point isn't on the drawings",
  note: "Spare LAN ports (2.5G + 2 × 1G) can wire the PC, or the M200." });

// Thread / Matter sensors''')

splice("// Unplaced (tray)\nconst UNPLACED = [", "const CAT6 = [", "// Unplaced (tray): everything is on the plan now\nconst UNPLACED = [];\n")

# ---------- icons, classes, collars
rep('    case "homepod":', '''    case "outlet":
      el("rect", { x: -4.6, y: -4.6, width: 9.2, height: 9.2, rx: 1.4 }, ico);
      el("rect", { x: -.55, y: -3.1, width: 1.1, height: 2.2, rx: .2, class: "f" }, ico);
      el("rect", { x: -3.2, y: .7, width: 2.2, height: 1.1, rx: .2, class: "f" }, ico);
      el("rect", { x: 1, y: .7, width: 2.2, height: 1.1, rx: .2, class: "f" }, ico); break;
    case "homepod":''')
rep('  if (d.kind === "switch") return el("rect", { class: "tile", x: -6.4,', '  if (d.kind === "switch" || d.kind === "outlet") return el("rect", { class: "tile", x: -6.4,')
rep('const t = kind === "switch" ? el("rect", { x: -6.4,', 'const t = (kind === "switch" || kind === "outlet") ? el("rect", { x: -6.4,')
rep('  if (d.th === "br") c.push("th-br"); else if (d.th === "end") c.push("th-end");',
    '  if (d.th === "br") c.push("th-br"); else if (d.th === "end") c.push("th-end"); else if (d.th === "router") c.push("th-router");\n  if (d.apple) c.push("th-apple");\n  if (d.ap) c.push("wf-ap");')
rep('''el("circle", { class: "collar th", r: cr + 2.6, style: "stroke-width:.7;stroke-dasharray:none" }, grp); }''',
    '''el("circle", { class: "collar th", r: cr + 2.6, style: "stroke-width:.7;stroke-dasharray:none" }, grp); }
    if (d.ap) el("circle", { class: "collar wf", r: cr + 2.6, style: "stroke-width:.7" }, grp);''')

# ---------- thread layer: routed mesh through the H2 outlets
splice("let heatTimer = null;", "/* ================= layer: wifi ================= */", r'''let heatTimer = null;
// signal map: for each floor cell, the best path loss to any source (nearest first; stop once no source can win)
function heatmap(sources, step, tint) {
  const x0 = 65, y0 = 190, W = Math.ceil((937 - x0) / step), H = Math.ceil((592 - y0) / step);
  const c = document.createElement("canvas"); c.width = W; c.height = H;
  const g = c.getContext("2d"), img = g.createImageData(W, H);
  const css = getComputedStyle(document.documentElement);
  const hex = v => { const s = css.getPropertyValue(v).trim(); const n = parseInt(s.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
  const base = hex(tint), warn = hex("--warn"), ir = hex("--ir");
  for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
    const p = { x: x0 + (i + .5) * step, y: y0 + (j + .5) * step };
    if (isWall(p.x, p.y)) continue;
    const order = sources.map(A => ({ A, d: Math.max(.5, metres(A, p)) })).sort((a, b) => a.d - b.d);
    let pl = Infinity;
    for (const o of order) { if (39.6 + 28 * Math.log10(o.d) >= pl) break; pl = Math.min(pl, link(o.A, p).pl); }
    const k = (j * W + i) * 4;
    let rgb = base, a = 0;
    if (pl <= 68) a = 46; else if (pl <= 80) a = 24; else if (pl <= 88) { rgb = warn; a = 40; } else { rgb = ir; a = 34; }
    img.data[k] = rgb[0]; img.data[k + 1] = rgb[1]; img.data[k + 2] = rgb[2]; img.data[k + 3] = a;
  }
  g.putImageData(img, 0, 0);
  const o = document.createElement("canvas"); o.width = W; o.height = H;
  const og = o.getContext("2d"); og.filter = `blur(${Math.max(1, 4 / step).toFixed(1)}px)`; og.drawImage(c, 0, 0);
  return { url: o.toDataURL(), x: x0, y: y0, w: W * step, h: H * step };
}
// a dot that travels a multi-hop path, pausing briefly at each relay
function packet(g, pts, cls, begin, minCycle) {
  if (pts.length < 2) return;
  const segs = []; let total = 0;
  for (let k = 1; k < pts.length; k++) { const l = Math.hypot(pts[k].x - pts[k - 1].x, pts[k].y - pts[k - 1].y); segs.push(l); total += l; }
  if (total < 1) return;
  const travel = Math.max(.9, total / 150), dwell = .22, dur = travel + dwell * (pts.length - 2), cycle = Math.max(minCycle, dur + 1.2);
  const kp = [0], kt = [0]; let acc = 0, t = 0;
  for (let k = 0; k < segs.length; k++) {
    acc += segs[k]; t += travel * segs[k] / total;
    kp.push(acc / total); kt.push(t / cycle);
    if (k < segs.length - 1) { t += dwell; kp.push(acc / total); kt.push(t / cycle); }
  }
  kp.push(1); kt.push(1);
  for (let k = 1; k < kt.length; k++) if (kt[k] <= kt[k - 1] + 1e-4) kt[k] = kt[k - 1] + 1e-4;
  kt[kt.length - 1] = 1;
  const dpath = "M" + pts.map(q => `${q.x.toFixed(1)} ${q.y.toFixed(1)}`).join("L");
  const c = el("circle", { r: 1.7, class: cls, opacity: 0 }, g), b = (begin % cycle).toFixed(2) + "s";
  el("animateMotion", { dur: cycle + "s", repeatCount: "indefinite", path: dpath, keyPoints: kp.map(v => Math.min(1, v).toFixed(4)).join(";"), keyTimes: kt.map(v => v.toFixed(5)).join(";"), calcMode: "linear", begin: b }, c);
  el("animate", { attributeName: "opacity", dur: cycle + "s", repeatCount: "indefinite", begin: b, values: "0;1;1;0;0", keyTimes: `0;0.02;${(dur / cycle * .97).toFixed(3)};${(dur / cycle).toFixed(3)};1` }, c);
}

// Thread: border routers are roots; H2 outlets route; P2s attach to the router with the best link
let TH = { parent: {}, routes: {}, hops: {}, linkTo: {}, nodes: [] };
const threadBRs = () => D.filter(d => d.th === "br" && (!d.apple || state.threadMerged));
const thName = d => !d ? "—" : d.kind === "outlet" ? `H2 (${d.short})` : d.cap;
function solveThread() {
  const roots = threadBRs(), nodes = [...roots, ...D.filter(d => d.th === "router")];
  const dist = new Map(nodes.map(n => [n.id, Infinity])), prev = new Map();
  roots.forEach(r => dist.set(r.id, 0));
  const open = new Set(nodes.map(n => n.id));
  while (open.size) {
    let u = null, best = Infinity;
    for (const id of open) if (dist.get(id) < best) { best = dist.get(id); u = id; }
    if (u === null) break;
    open.delete(u);
    for (const v of nodes) {
      if (!open.has(v.id)) continue;
      const c = linkCost(link(anchor(byId(u)), anchor(v)).pl); if (!isFinite(c)) continue;
      if (best + c + .01 < dist.get(v.id)) { dist.set(v.id, best + c + .01); prev.set(v.id, u); }
    }
  }
  const parent = {}, routes = {}, hops = {}, linkTo = {};
  for (const n of nodes) if (prev.has(n.id)) parent[n.id] = prev.get(n.id);
  for (const e of D.filter(d => d.th === "end")) {
    let best = null;
    for (const n of nodes) {
      if (!isFinite(dist.get(n.id))) continue;
      const L = link(anchor(e), anchor(n)), c = linkCost(L.pl);
      if (!isFinite(c)) continue;
      if (!best || c < best.c || (c === best.c && dist.get(n.id) < best.dist) || (c === best.c && dist.get(n.id) === best.dist && L.pl < best.pl)) best = { id: n.id, c, dist: dist.get(n.id), pl: L.pl };
    }
    if (best) parent[e.id] = best.id;
  }
  const rootIds = new Set(roots.map(r => r.id));
  for (const id in parent) {
    const path = [id]; let cur = id, guard = 0;
    while (parent[cur] && guard++ < 30) { cur = parent[cur]; path.push(cur); }
    if (rootIds.has(cur)) { routes[id] = path; hops[id] = path.length - 1; }
    linkTo[id] = link(anchor(byId(id)), anchor(byId(parent[id])));
  }
  TH = { parent, routes, hops, linkTo, nodes };
}
const viaThread = id => TH.routes[id] ? TH.routes[id].slice(1).map(n => thName(byId(n))).join(" → ") : "no route to a border router";
function drawThread(fast) {
  solveThread();
  const g = G("thread"); g.textContent = "";
  const live = TH.nodes.filter(n => n.th === "br" || TH.routes[n.id]);
  const hm = heatmap(live.map(anchor), fast ? 8 : 4, "--th");
  el("image", { href: hm.url, x: hm.x, y: hm.y, width: hm.w, height: hm.h, preserveAspectRatio: "none", class: "th-heat", "clip-path": "url(#clip-apartment)", style: "image-rendering:auto" }, g);
  // the room holding the weakest P2 link is the zone to validate after install
  const far = farZone(), fz = far && ROOMS.find(r => r.id === far.room);
  if (fz) {
    const xs = fz.poly.map(q => q[0]), ys = fz.poly.map(q => q[1]);
    el("path", { class: "validate-zone", d: "M" + fz.poly.map(q => q.join(" ")).join("L") + "Z", opacity: .9 }, g);
    const vl = el("text", { class: "validate-label", x: (Math.min(...xs) + Math.max(...xs)) / 2, y: Math.min(...ys) + 22 }, g); vl.textContent = "Weakest Thread link · validate after install";
  }
  // wavefronts from each active border router
  for (const br of threadBRs()) {
    const A = anchor(br), rings = el("g", { transform: `translate(${A.x} ${A.y})` }, el("g", { "clip-path": "url(#clip-apartment)" }, g));
    for (let k = 0; k < 3; k++) el("circle", { class: "th-ring", r: br.apple ? 260 : 420 }, rings);
  }
  // router-to-router neighbours the mesh can fail over to
  for (let i = 0; i < live.length; i++) for (let j = i + 1; j < live.length; j++) {
    const a = live[i], b = live[j];
    if (TH.parent[a.id] === b.id || TH.parent[b.id] === a.id) continue;
    const A = anchor(a), B = anchor(b);
    if (link(A, B).pl <= 80) el("path", { class: "th-mesh", d: `M${A.x} ${A.y}L${B.x} ${B.y}` }, g);
  }
  // parent links: P2 → router, router → router → border router (never through H1 switches)
  for (const id in TH.parent) {
    const d = byId(id), B = anchor(d), A = anchor(byId(TH.parent[id])), L = TH.linkTo[id];
    el("path", { class: "th-link " + grade(L.pl), d: `M${B.x} ${B.y}L${A.x} ${A.y}` }, g);
    if (d.th !== "end") continue;
    const ux = A.x - B.x, uy = A.y - B.y, ul = Math.hypot(ux, uy) || 1, side = uy / ul > 0 ? 1 : -1;
    let mx = B.x + ux * .42 + (-uy / ul) * 7 * side, my = B.y + uy * .42 + (ux / ul) * 7 * side;
    if (ul < 110) { mx = B.x; my = B.y + 19; }
    const lab = el("g", { class: "th-label", transform: `translate(${mx} ${my})` }, g);
    const txt = `${L.pl.toFixed(0)} dB · ${L.d.toFixed(1)} m · ${L.w} wall${L.w === 1 ? "" : "s"}`;
    el("rect", { x: -txt.length * 1.32, y: -4, width: txt.length * 2.64, height: 8, rx: 2 }, lab);
    const t = el("text", {}, lab); t.textContent = txt;
  }
  let i = 0;
  for (const d of D.filter(x => x.th === "end")) { const r = TH.routes[d.id]; if (r) packet(g, r.map(n => anchor(byId(n))), "pkt-th", i++ * 1.1, 4.4); }
  const hp = byId("homepod");
  if (hp && !state.threadMerged) { const A = anchor(hp); const t = el("text", { class: "th-tag", x: A.x, y: A.y - 14.5 }, g); t.textContent = "Apple Thread network · separate"; }
  const t = el("text", { class: "no-thread-tag", x: 690, y: 470 }, g); t.textContent = "H1 switches don't repeat Thread: hidden in this view";
}
function scheduleThread(fast) {
  if (fast) { drawThread(true); clearTimeout(heatTimer); heatTimer = setTimeout(() => drawThread(false), 180); }
  else drawThread(false);
}

function farZone() {
  return D.filter(d => d.th === "end" && TH.linkTo[d.id]).map(d => ({ room: d.room, d, L: TH.linkTo[d.id], via: byId(TH.parent[d.id]) })).sort((a, b) => b.L.pl - a.L.pl)[0];
}

''')

# ---------- wifi layer: AiMesh with wired backhaul
splice("function drawWifi() {", "/* ================= layer: IR ================= */", r'''let WF = { assoc: {} }, wfHeat = { key: "", hm: null };
const band = d => d.ap ? "Wi-Fi 7" : d.wifi.includes("5") ? "2.4 / 5 GHz" : "2.4 GHz";
function bestAP(p) { let best = null; for (const a of D.filter(x => x.ap)) { const L = link(anchor(a), p); if (!best || L.pl < best.L.pl) best = { ap: a, L }; } return best; }
function drawWifi(fast) {
  const g = G("wifi"); g.textContent = "";
  const aps = D.filter(d => d.ap), main = byId("ap-main"), M = anchor(main);
  if (state.view === "wifi") {
    const step = fast ? 8 : 4, theme = document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const key = aps.map(a => { const q = anchor(a); return q.x.toFixed(0) + "," + q.y.toFixed(0); }).join("|") + `|${state.wallLoss}|${step}|${theme}`;
    if (wfHeat.key !== key) wfHeat = { key, hm: heatmap(aps.map(anchor), step, "--wf") };
    const hm = wfHeat.hm;
    el("image", { href: hm.url, x: hm.x, y: hm.y, width: hm.w, height: hm.h, preserveAspectRatio: "none", class: "wf-heat", "clip-path": "url(#clip-apartment)" }, g);
  }
  // wired backhaul from the main router to each node (cable route is schematic)
  for (const a of aps) {
    if (a === main) continue;
    const A = anchor(a);
    el("path", { class: "eth", d: `M${M.x} ${M.y}L${A.x} ${A.y}` }, g);
    const t = el("text", { class: "wf-tag", x: (M.x + A.x) / 2, y: (M.y + A.y) / 2 - 3 }, g); t.textContent = "CAT6 backhaul";
  }
  const ft = el("text", { class: "wf-tag", x: M.x - 4, y: M.y + 22 }, g); ft.textContent = "fibre in";
  // each client joins the node with the best signal; its traffic rides the backhaul to the main router
  WF.assoc = {};
  let i = 0;
  for (const d of D.filter(x => x.wifi && !x.ap)) {
    const A = anchor(d), b = bestAP(A); if (!b) continue;
    WF.assoc[d.id] = b;
    const B = anchor(b.ap);
    el("path", { class: "wf-assoc " + grade(b.L.pl), d: `M${A.x} ${A.y}L${B.x} ${B.y}` }, g);
    packet(g, b.ap === main ? [A, B] : [A, B, M], "pkt-wf", i++ * .7, 5);
  }
  for (const d of D.filter(x => x.wifi)) {
    const A = anchor(d), r0 = 11.5;
    const wg = el("g", { transform: `translate(${A.x} ${A.y - r0})` }, g);
    [[3, "a1"], [5.6, "a2"], [8.2, "a3"]].forEach(([r, c]) => el("path", { class: "wf-arc " + c, d: `M${-r * .72} ${-r * .55}A${r} ${r} 0 0 1 ${r * .72} ${-r * .55}` }, wg));
    const t = el("text", { class: "wf-band", x: A.x + 13, y: A.y + 1.6, "text-anchor": "start" }, g); t.textContent = band(d); t.style.textAnchor = "start";
  }
}

''')

# ---------- view plumbing
rep("  clearTrace();\n  renderViewPanel();", '  if (state.view === "wifi" && !G("wifi").querySelector(".wf-heat")) drawWifi(false);\n  clearTrace();\n  renderViewPanel();')
rep("  drawZigbee(); scheduleThread(fast); drawWifi(); drawIR();", "  drawZigbee(); scheduleThread(fast); drawWifi(fast); drawIR();")
rep("solveZigbee(); drawZigbee(); scheduleThread(true); drawWifi(); drawIR();", "solveZigbee(); drawZigbee(); scheduleThread(true); drawWifi(true); drawIR();")
rep("solveZigbee(); drawZigbee(); drawThread(false); drawWifi(); drawIR();", "solveZigbee(); drawZigbee(); drawThread(false); drawWifi(false); drawIR();")
rep("    drawThread(false); applyView();", "    drawThread(false); drawWifi(false); applyView();")
rep('const others = ["g3", "m2", "magicpad"].map(id => anchor(byId(id)));', 'const others = ["g3", "m2", "magicpad", "homepod", "ap-main", "ap-bed2", "ap-gm"].map(id => anchor(byId(id)));')

# ---------- stats + rows
rep("  const p2 = D.filter(d => d.th === \"end\").map(d => ({ d, L: link(m, anchor(d)) }));",
    "  const p2 = D.filter(d => d.th === \"end\").map(d => ({ d, L: TH.linkTo[d.id] || link(m, anchor(d)), via: byId(TH.parent[d.id]), hops: TH.hops[d.id] || 0 }));")
rep("function viaText(id) {", r'''const rowHTML = (d, v, sub) => `<li data-dev="${d.id}"><span class="k">${d.name}</span><span class="v">${v}</span>${sub ? `<span class="s">${sub}</span>` : ""}</li>`;
const p2sub = o => `${o.L.pl.toFixed(0)} dB to ${thName(o.via)} · ${o.L.d.toFixed(1)} m · ${o.L.w} wall${o.L.w === 1 ? "" : "s"}${o.hops > 1 ? ` · ${o.hops} hops to the border router` : ""}`;
const threadRows = s => s.p2.map(o => rowHTML(o.d, gradeHTML(o.L.pl), p2sub(o))).join("") +
  D.filter(d => d.th === "router").map(d => rowHTML(d, TH.routes[d.id] ? gradeHTML(TH.linkTo[d.id].pl) : `<span class="grade g-weak">No route</span>`, "Thread router · " + viaThread(d.id))).join("");
function viaText(id) {''')
rep('''  if (ul) ul.innerHTML = stats().p2.map(o => `<li data-dev="${o.d.id}"><span class="k">${o.d.name}</span><span class="v">${gradeHTML(o.L.pl)}</span><span class="s">${o.L.pl.toFixed(0)} dB path loss · ${o.L.d.toFixed(1)} m · ${o.L.w} wall${o.L.w === 1 ? "" : "s"}</span></li>`).join("");''',
    '''  if (ul) ul.innerHTML = threadRows(stats());''')

# ---------- panels
rep('<li><span class="k">Thread sensors (P2)</span><span class="v">${s.p2.length}</span></li>',
    '''<li><span class="k">Thread sensors (P2)</span><span class="v">${s.p2.length}</span></li>
        <li><span class="k">Aqara Wall Outlet H2 (Matter over Thread)</span><span class="v">${D.filter(d => d.kind === "outlet").length}</span><span class="s">Living sofa floor socket · both Master bedsides. Thread routers, not Zigbee.</span></li>
        <li><span class="k">Wi-Fi 7 AiMesh</span><span class="v">${D.filter(d => d.ap).length} units</span><span class="s">RT-BE92U at the TV cabinet (fibre) · ZenWiFi BT8 in Bedroom 2 and Gaming · CAT6 backhaul</span></li>''')
splice('  } else if (state.view === "thread") {', '  } else if (state.view === "ir") {', r'''  } else if (state.view === "thread") {
    html = `<h2>${sw("--th")}Thread / Matter</h2>
      <p>The M200 is the border router. The three H2 outlets run Matter over Thread and are mains powered, so they route: each P2 attaches to the router with the best link, and its messages hop back to the M200. H1 switches don't carry Thread.</p>
      <ul class="facts" id="p2facts">${threadRows(s)}</ul>
      <div class="ctrl">
        <label>HomePod mini's Thread network</label>
        <div class="seg" role="group" aria-label="HomePod mini Thread network"><button type="button" data-merge="0" aria-pressed="${!state.threadMerged}">Separate (safe)</button><button type="button" data-merge="1" aria-pressed="${state.threadMerged}">Shared with M200</button></div>
        <label for="wallLoss"><span>Loss per wall crossed</span><b id="wlv">${state.wallLoss} dB</b></label>
        <input id="wallLoss" type="range" min="6" max="20" step="1" value="${state.wallLoss}">
        <div class="row-btns"><button class="btn" id="btnBest" type="button">Find the best M200 spot in its room</button><button class="btn" id="btnReset" type="button">Reset positions</button></div>
      </div>
      <div class="note"><b>Pair in Aqara Home first.</b> A Matter device joins the Thread network of the app that adds it. Add the H2s and P2s on the M200, then share them to Apple Home.</div>`;
  } else if (state.view === "wifi") {
    const aps = D.filter(d => d.ap), cl = D.filter(d => d.wifi && !d.ap);
    html = `<h2>${sw("--wf")}Wi-Fi / LAN</h2>
      <p>The RT-BE92U at the TV cabinet, where the fibre comes in, leads an AiMesh with two ZenWiFi BT8 nodes on CAT6 backhaul. Each device is drawn to the unit it would most likely join. The P2 sensors and H2 outlets never touch Wi-Fi.</p>
      <ul class="facts">${aps.map(d => devRow(d, "Wi-Fi 7", d.id === "ap-main" ? "Fibre in · CAT6 backhaul to both BT8s" : "CAT6 backhaul to the RT-BE92U")).join("")}
        ${cl.map(d => { const a = WF.assoc[d.id]; return devRow(d, a ? gradeHTML(a.L.pl) : "—", a ? `${band(d)} · joins the ${a.ap.short} · ${a.L.pl.toFixed(0)} dB` : band(d)); }).join("")}
      </ul>
      <div class="note"><b>2.4 GHz estimate.</b> 5 and 6 GHz lose more through walls, and the hubs mostly use 2.4 GHz anyway. Channel and network settings for the smart-home side are in review F.</div>`;
''')
rep('  $("#btnReset", P)?.addEventListener("click", resetPositions);',
    '''  $("#btnReset", P)?.addEventListener("click", resetPositions);
  P.querySelectorAll("[data-merge]").forEach(b => b.addEventListener("click", () => { state.threadMerged = b.dataset.merge === "1"; store.set("threadMerged", state.threadMerged); drawThread(false); renderViewPanel(); renderReview(); if (state.sel) renderSel(); }));''')

# ---------- selection panel
rep('  if (d.th === "br") chips.push(`<span class="chip net-th">Thread Border Router</span>`);',
    '''  if (d.th === "br") chips.push(`<span class="chip net-th">Thread Border Router${d.apple ? " (Apple network)" : ""}</span>`);
  if (d.th === "router") chips.push(`<span class="chip net-th">Thread router (expected)</span>`);
  if (d.ap) chips.push(`<span class="chip net-wf">AiMesh ${d.id === "ap-main" ? "router" : "node"}</span>`);''')
rep('''  if (d.th === "end") { const L = link(anchor(byId("m200")), anchor(d)); route = `<dt>Thread link</dt><dd>${gradeHTML(L.pl)} · ${L.pl.toFixed(0)} dB · ${L.d.toFixed(1)} m · ${L.w} wall${L.w === 1 ? "" : "s"} to M200</dd>`; }''',
    '''  if ((d.th === "end" || d.th === "router") && TH.linkTo[d.id]) { const L = TH.linkTo[d.id]; route = `<dt>Thread link</dt><dd>${gradeHTML(L.pl)} · ${L.pl.toFixed(0)} dB to ${thName(byId(TH.parent[d.id]))} · ${L.d.toFixed(1)} m · ${L.w} wall${L.w === 1 ? "" : "s"}</dd><dt>Thread route</dt><dd>${TH.routes[d.id] ? TH.routes[d.id].map(n => thName(byId(n))).join(" → ") : "No route to a border router"}</dd>`; }
  if (WF.assoc[d.id]) { const a = WF.assoc[d.id]; route += `<dt>Wi-Fi</dt><dd>${gradeHTML(a.L.pl)} · joins the ${a.ap.short} · ${a.L.pl.toFixed(0)} dB (2.4 GHz estimate)</dd>`; }''')

# ---------- legend
rep('[legendDev("hub", "", { collar: "var(--th)", cw: 2.2, collar2: true }), "Thread Border Router", "M200 bridges Thread to the LAN. HomePod mini can too."],',
    '''[legendDev("hub", "", { collar: "var(--th)", cw: 2.2, collar2: true }), "Thread Border Router", "M200 bridges Aqara's Thread network to the LAN."],
      [legendDev("homepod", "", { collar: "var(--th)", cw: 2.2, collar2: true, dash: "3 1.6" }), "Border router, Apple network", "HomePod mini. Carries Aqara devices only if both run one Thread network."],
      [legendDev("outlet", "", { collar: "var(--th)", cw: 1.4 }), "Thread router", "Aqara Wall Outlet H2 in Matter mode. Mains powered, so it relays for the P2s."],''')
rep('"Thread link", "Direct to the border router. No H1 hops."', '"Thread link", "P2 to its parent router, then router to router back to the M200. Never through H1 switches."')
rep('"Validate after install", "Furthest zone from the border router."', '"Validate after install", "Room with the weakest P2 link."')
splice('    { t: "Wi-Fi / LAN", c: "--wf", rows: [', '    { t: "Infrared", c: "--ir", rows: [', r'''    { t: "Wi-Fi / LAN", c: "--wf", rows: [
      [legendDev("ap", "", { collar: "var(--wf)", cw: 1.2, collar2: true }), "AiMesh router / node", "RT-BE92U at the TV cabinet; ZenWiFi BT8 in Bedroom 2 and Gaming. All Wi-Fi 7."],
      [legendDev("hub", "", { collar: "var(--wf)", cw: 1.2 }), "Wi-Fi device", "M200, G3, M2, S100, HomePod mini, MagicPad."],
      [legendLine("var(--wf)", "1.2 1.6", .8), "Joins this unit", "The mesh unit with the best estimated signal."],
      [legendLine("var(--wf)", "4 1.2 .6 1.2", 1.1), "CAT6 backhaul", "Main router to each BT8. The cable route is schematic."],
      [legendSvg(s => { el("rect", { x: -9, y: -5, width: 18, height: 10, rx: 1.6, fill: "var(--sheet)", stroke: "var(--wf)" }, s); const t = el("text", { x: 0, y: 2, "font-size": 5.4, "text-anchor": "middle", fill: "var(--wf-ink)", "font-weight": 600 }, s); t.textContent = "CAT6"; }), "CAT6 data point", "On the M&E sheet: Living TV wall, Gaming desk. The Bedroom 2 run and the second Gaming point aren't drawn."]
    ]},
''')
rep('"On the drawings", "RCP switch points, CAT6, LED features. Fixed."', '"On the drawings", "RCP switch points, M&E sockets, CAT6, LED features. Fixed."')

# ---------- "where Matter sits" panel
rep("802.15.4 mesh. M200 and HomePod mini are border routers. P2 sensors are battery end devices.",
    "802.15.4 mesh. M200 is the border router (HomePod mini too, if one network). H2 outlets route; P2 sensors are battery end devices.")
rep("IP. M200, G3, M2, HomePod mini, S100 and MagicPad. CAT6 points in Living and Gaming.",
    "IP. RT-BE92U + 2 × ZenWiFi BT8 (Wi-Fi 7, CAT6 backhaul) serving the M200, G3, M2, HomePod mini, S100 and MagicPad.")
rep("Both can admin the same P2 via multi-admin.", "Both can admin the same P2 or H2 via multi-admin.")
rep('<li style="margin:6px 0">H1 switches route Zigbee. They do nothing for Thread.</li>',
    '<li style="margin:6px 0">H1 switches route Zigbee. They do nothing for Thread.</li>\n            <li style="margin:6px 0">H2 outlets (Matter mode) route Thread. They do nothing for Zigbee.</li>')

p.write_text(s)
print("ok")
