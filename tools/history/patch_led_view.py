"""Add the LED power view (sixth tab) to the plan, fed by the LED strip power table's live numbers."""
import pathlib, sys, re
root = pathlib.Path(sys.argv[1])
p = root / "src/template.html"; s = p.read_text()
q = root / "src/led-section.html"; t = q.read_text()

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:90], s.count(old)); s = s.replace(old, new)
def rp(old, new, n=1):
    global t
    assert t.count(old) == n, (old[:90], t.count(old)); t = t.replace(old, new)

# ---------- LED table: share its numbers with the plan
rp("  let last = [];\n  function update() {", "  let last = [], lastG = DEF;\n  const subs = [];\n  function update() {")
rp("    last = STRIPS.map(s => calc(s, g));", "    last = STRIPS.map(s => calc(s, g)); lastG = g;")
rp('    $("led-summary").innerHTML = parts.join("");\n  }', '''    $("led-summary").innerHTML = parts.join("");
    subs.forEach(fn => { try { fn(); } catch (e) { /* a listener failing must not break the table */ } });
  }
  window.planLed = {
    results: () => last.map(r => ({ k: r.s.k, name: r.s.name, type: r.s.type, len: r.s.len, wpm: r.wpm, load: r.load, pct: r.pct, supply: r.supply, psuFit: r.psuFit, n: r.n, loop: !!r.s.loop, psu: lastG.psu, derate: lastG.derate })),
    subscribe: fn => subs.push(fn)
  };''')
# installed feeders: the length is only for the drop estimate; a meter reading settles it
rp('<span class="assumed" data-assumed="fl">assumed length</span>', '<span class="assumed" data-assumed="fl">optional: for the drop estimate</span>')
rp('        <li><b>Supplies:</b>', '        <li><b>Feeders already installed?</b> Then skip the cable inputs and measure instead: with the strip on full white, read the voltage at its far end. 23.3 V or more means the drop is under 3%.</li>\n        <li><b>Supplies:</b>')
q.write_text(t)

# ---------- tokens: a lighting hue distinct from the four network colours and the amber warning
rep("  --warn: #b88200;    --warn-ink: #855e00;", "  --warn: #b88200;    --warn-ink: #855e00;\n  --led: #d6338a;     --led-ink: #b0216f;")
rep("    --warn: #e3b341; --warn-ink: #edc565;", "    --warn: #e3b341; --warn-ink: #edc565;\n    --led: #ff6eb4; --led-ink: #ff8cc4;")
rep("\n  --warn: #e3b341; --warn-ink: #edc565;", "\n  --warn: #e3b341; --warn-ink: #edc565;\n  --led: #ff6eb4; --led-ink: #ff8cc4;")

# ---------- tab + layer
ir_tab = re.search(r'    <button class="tab" role="tab" data-view="ir".*?</button>\n', s).group(0)
rep(ir_tab, ir_tab + '    <button class="tab" role="tab" data-view="led" aria-selected="false"><svg class="sw" viewBox="0 0 22 10" aria-hidden="true"><rect x="2" y="3.5" width="18" height="3" rx="1.5" fill="var(--led)"/><circle cx="6" cy="5" r=".9" fill="var(--sheet)"/><circle cx="11" cy="5" r=".9" fill="var(--sheet)"/><circle cx="16" cy="5" r=".9" fill="var(--sheet)"/></svg><span class="lbl-long">LED power</span><span class="lbl-short" aria-hidden="true">LED</span></button>\n')
rep('        <g id="wifi" class="layer"></g>', '        <g id="wifi" class="layer"></g>\n        <g id="ledpower" class="layer"></g>')

# ---------- CSS
rep('#plan .ir-cone { stroke: none; }', '''#plan .ir-cone { stroke: none; }
/* LED power */
#plan .led-glow { fill: none; stroke: var(--led); stroke-width: 6; opacity: .16; stroke-linecap: round; stroke-linejoin: round; }
#plan .led-run { fill: none; stroke: var(--led); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
#plan .led-flow { fill: none; stroke: var(--sheet); stroke-width: .9; stroke-dasharray: 1.2 5; stroke-linecap: round; animation: ledFlow 1.6s linear infinite; }
#plan .led-wire { fill: none; stroke: var(--led); stroke-width: 1.1; stroke-linecap: round; }
#plan .led-wire-flow { fill: none; stroke: var(--sheet); stroke-width: .6; stroke-dasharray: 1 3.2; animation: ledFlow 1.6s linear infinite; }
#plan .led-leader { fill: none; stroke: var(--led); stroke-width: .5; stroke-dasharray: 1.2 1.4; opacity: .8; }
@keyframes ledFlow { to { stroke-dashoffset: -12.4; } }
#plan .psu rect { fill: var(--sheet); stroke-width: 1; }
#plan .psu.ok rect { stroke: var(--wf); } #plan .psu.tight rect { stroke: var(--warn); } #plan .psu.over rect { stroke: var(--ir); }
#plan .psu text { fill: var(--ink); font-size: 3.6px; font-weight: 600; text-anchor: middle; dominant-baseline: central; }
#plan .led-card rect.bg { fill: var(--sheet); stroke: var(--sheet-edge); stroke-width: .5; }
#plan .led-card text { font-size: 4.4px; fill: var(--ink-2); }
#plan .led-card text.t { fill: var(--ink); font-weight: 600; font-size: 4.8px; }
#plan .led-card text.ok { fill: var(--wf-ink); font-weight: 600; } #plan .led-card text.tight { fill: var(--warn-ink); font-weight: 600; } #plan .led-card text.over { fill: var(--ir-ink); font-weight: 600; }
#plan .led-card .bar { fill: var(--led); }
#plan .led-card .bar-dot { fill: var(--sheet); }
#plan .led-feed { fill: var(--led); stroke: var(--sheet); stroke-width: .8; }
#plan .led-tag { fill: var(--led-ink); font-size: 4.2px; font-weight: 600; paint-order: stroke; stroke: var(--sheet); stroke-width: 1.8px; }
#plan[data-view="led"] .dev.led-drv .collar.zb { opacity: 1; stroke: var(--led); stroke-dasharray: none; stroke-width: 1.2; }''')
rep('  #plan .ir-axis { animation: none; }', '  #plan .ir-axis { animation: none; }\n  #plan .led-flow, #plan .led-wire-flow { animation: none; }')

# ---------- device class, view, plumbing
rep('  if (d.irRole === "ac") c.push("ir-ac");', '  if (d.irRole === "ac") c.push("ir-ac");\n  if (d.kind === "driver") c.push("led-drv");')
rep('  ir:     { show: ["ir"], devs: d => !!(d.ir || d.irRole) }\n};', '  ir:     { show: ["ir"], devs: d => !!(d.ir || d.irRole) },\n  led:    { show: ["ledpower"], devs: d => d.kind === "driver" }\n};')
rep('for (const id of ["zigbee", "thread", "wifi", "ir"])', 'for (const id of ["zigbee", "thread", "wifi", "ir", "ledpower"])', 2)
rep("  drawZigbee(); scheduleThread(fast); drawWifi(fast); drawIR();", "  drawZigbee(); scheduleThread(fast); drawWifi(fast); drawIR(); drawLED();")
rep("solveZigbee(); drawZigbee(); scheduleThread(true); drawWifi(true); drawIR();", "solveZigbee(); drawZigbee(); scheduleThread(true); drawWifi(true); drawIR(); drawLED();")
rep("solveZigbee(); drawZigbee(); drawThread(false); drawWifi(false); drawIR();", '''solveZigbee(); drawZigbee(); drawThread(false); drawWifi(false); drawIR(); drawLED();
window.planLed && window.planLed.subscribe(() => { drawLED(); if (state.view === "led") renderViewPanel(); });''')
rep('wifi: "Wi-Fi / LAN plan", ir: "IR / aircon plan"', 'wifi: "Wi-Fi / LAN plan", ir: "IR / aircon plan", led: "LED strip power plan"')

# ---------- drawing
rep("/* ================= view switching ================= */", r'''/* ================= layer: LED power ================= */
// strip key in the LED table -> its driver on the plan; card and supply offsets keep labels clear of the drawing
const LED_MAP = {
  tv:     { drv: "drv-tv",     psu: [-18, 0],  card: [-104, -16] },
  mirror: { drv: "drv-mirror", psu: [-16, 10], card: [-110, -20] },
  head:   { drv: "drv-head",   psu: [-16, -12], card: [-110, -14] },
  gaming: { drv: "drv-gm",     psu: [16, 18],  card: null }
};
const GAMING_RUN = [[624, 364], [624, 219], [727, 219], [727, 364], [624, 364]];   // ceiling LED rectangle on the RCP
function drawLED() {
  const g = G("ledpower"); if (!g) return; g.textContent = "";
  const api = window.planLed; if (!api) return;
  const STATUS = { ok: "OK", tight: "Tight", over: "Over" };
  for (const r of api.results()) {
    const m = LED_MAP[r.k], d = m && byId(m.drv); if (!d) continue;
    const D0 = anchor(d), P = { x: D0.x + m.psu[0], y: D0.y + m.psu[1] };
    const pct = r.pct || 0, speed = (2.6 - 1.9 * Math.min(1, pct / 100)).toFixed(2) + "s";   // busier strips flow faster
    // 24 V supply -> driver
    const wire = `M${P.x} ${P.y}L${D0.x} ${D0.y}`;
    el("path", { class: "led-wire", d: wire }, g);
    el("path", { class: "led-wire-flow", d: wire, style: `animation-duration:${speed}` }, g);
    const ps = el("g", { class: "psu " + (r.supply || "ok"), transform: `translate(${P.x} ${P.y})` }, g);
    el("rect", { x: -6.5, y: -4, width: 13, height: 8, rx: 1.4 }, ps);
    el("text", { y: .2 }, ps).textContent = r.psuFit && r.supply !== "ok" ? `${r.psuFit}W` : `${r.psu}W`;
    el("title", {}, ps).textContent = `${r.name}: 24 V supply, ${r.load ? Math.round(r.load) + " W" : "load unknown"}`;
    // the strip: the Gaming rectangle is on the RCP; the other routes aren't drawn anywhere, so they get a card
    if (r.k === "gaming") {
      const run = "M" + GAMING_RUN.map(q => q.join(" ")).join("L");
      el("path", { class: "led-glow", d: run }, g);
      el("path", { class: "led-run", d: run }, g);
      el("path", { class: "led-flow", d: run, style: `animation-duration:${speed}` }, g);
      const C = { x: GAMING_RUN[0][0], y: GAMING_RUN[0][1] };
      el("path", { class: "led-wire", d: `M${D0.x} ${D0.y}L${C.x} ${C.y}` }, g);
      el("circle", { class: "led-feed", cx: C.x, cy: C.y, r: 2.4 }, g);
      el("text", { class: "led-tag", x: C.x + 4, y: C.y + 8 }, g).textContent = "feed both ends here";
    }
    const cw = 98, ch = 27;
    const cx = m.card ? D0.x + m.card[0] : 626, cy = m.card ? D0.y + m.card[1] : 248;
    if (m.card) el("path", { class: "led-leader", d: `M${cx + cw} ${cy + ch / 2}L${D0.x - 8} ${D0.y}` }, g);
    const card = el("g", { class: "led-card", transform: `translate(${cx} ${cy})` }, g);
    el("rect", { class: "bg", width: cw, height: ch, rx: 2.4 }, card);
    el("rect", { class: "bar", x: 4, y: 4.5, width: 14, height: 2.6, rx: 1.3 }, card);
    [7, 11, 15].forEach(x => el("circle", { class: "bar-dot", cx: x, cy: 5.8, r: .5 }, card));
    el("text", { class: "t", x: 21, y: 7.4 }, card).textContent = `${r.name} · ${r.len} m`;
    el("text", { class: r.supply || "", x: 4, y: 15.4 }, card).textContent = r.load === undefined ? "Enter W/m in the LED table"
      : `${r.wpm} W/m · ${Math.round(r.load)} W · ${STATUS[r.supply]} ${Math.round(pct)}% of ${r.psu} W`;
    el("text", { x: 4, y: 22.6 }, card).textContent = (r.n === 1 ? "Feed one end" : r.n === 2 ? (r.loop ? "Feed both ends, same corner" : "Feed both ends") : "Feed both ends and the middle")
      + (r.supply && r.supply !== "ok" && r.psuFit ? ` · fit ${r.psuFit} W` : "");
  }
}

/* ================= view switching ================= */''')

# ---------- side panel
rep("  P.innerHTML = html;\n", '''  if (state.view === "led") {
    const api = window.planLed, rows = api ? api.results() : [];
    const pill = r => r.load === undefined ? "—" : `<span class="grade g-${r.supply === "ok" ? "strong" : r.supply === "tight" ? "marginal" : "weak"}">${r.supply === "ok" ? "OK" : r.supply === "tight" ? "Tight" : "Over"} · ${Math.round(r.pct)}%</span>`;
    html = `<h2>${sw("--led")}LED power</h2>
      <p>Each strip runs from its own 24 V supply through an Aqara Smart Light Strip Driver. The flow along each wire speeds up with load. The Gaming rectangle is drawn from the ceiling plan; the other strip routes aren't on the drawings, so they show as cards.</p>
      <ul class="facts">${rows.map(r => `<li data-dev="${(LED_MAP[r.k] || {}).drv || ""}"><span class="k">${r.name}</span><span class="v">${pill(r)}</span><span class="s">${r.len} m × ${r.wpm ?? "?"} W/m${r.load !== undefined ? ` = ${Math.round(r.load)} W on ${r.psu} W` : ""} · ${r.n === 1 ? "one feed" : r.loop && r.n === 2 ? "both ends, same corner" : r.n === 2 ? "both ends" : "both ends + middle"}${r.supply && r.supply !== "ok" && r.psuFit ? ` · fit ${r.psuFit} W` : ""}</span></li>`).join("")}</ul>
      <div class="ctrl"><div class="row-btns"><a class="btn" href="#led">Edit ratings and cables</a></div></div>`;
  }
  P.innerHTML = html;
''', 1)

# ---------- legend
rep('    { t: "Position confidence", c: "--ink-3", rows: [', '''    { t: "LED power", c: "--led", rows: [
      [legendDev("driver", "", { collar: "var(--led)", cw: 1.2 }), "Light Strip Driver", "Aqara driver between the supply and the strip; a Zigbee end device on the M200."],
      [legendSvg(s => { el("rect", { x: -7, y: -4.5, width: 14, height: 9, rx: 1.6, fill: "var(--sheet)", stroke: "var(--wf)" }, s); const t = el("text", { x: 0, y: 1.8, "font-size": 4.6, "text-anchor": "middle", fill: "var(--ink)", "font-weight": 600 }, s); t.textContent = "200W"; }), "24 V supply", "One per strip. Its outline turns amber or red when the load passes the limit."],
      [legendSvg(s => { el("path", { d: "M-18 0H18", stroke: "var(--led)", "stroke-width": 6, opacity: .16, "stroke-linecap": "round" }, s); el("path", { d: "M-18 0H18", stroke: "var(--led)", "stroke-width": 1.8, "stroke-linecap": "round" }, s); }), "Strip run", "Gaming rectangle from the ceiling plan. Routes not on the drawings show as cards."],
      [legendSvg(s => { el("circle", { r: 3, fill: "var(--led)", stroke: "var(--sheet)", "stroke-width": 1 }, s); }), "Feed point", "Where the driver's wires join the strip."]
    ]},
    { t: "Position confidence", c: "--ink-3", rows: [''')
p.write_text(s)

e = root / "tools/export.py"; x = e.read_text()
old = '"ir": "5-ir-aircon"}'
assert x.count(old) == 1
e.write_text(x.replace(old, '"ir": "5-ir-aircon", "led": "6-led-power"}'))
print("ok")
