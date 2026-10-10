"""v6 review text: Thread through the H2 outlets, AiMesh Wi-Fi (section F), updated open items and sources."""
import pathlib, sys
p = pathlib.Path(sys.argv[1]); s = p.read_text()

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:100], s.count(old))
    s = s.replace(old, new)

def splice(start, end, new):
    global s
    assert s.count(start) == 1, ("start", start[:60])
    a = s.index(start); b = s.index(end, a + len(start))
    s = s[:a] + new + s[b:]

# ---------- B. Thread
splice('  <article><div><h3>B. Thread</h3>', '  <article><div><h3>C. IR</h3>', r'''  <article><div><h3>B. Thread</h3><div class="verdict ${["strong", "good"].includes(worstGrade) ? "g-good" : "g-marginal"}">${["strong", "good"].includes(worstGrade) ? "The H2 outlets carry it; confirm they route" : fzRoom + " needs help"}</div></div><div class="body">
    <p>The M200 is the border router. The three Aqara Wall Outlet H2s run Matter over Thread and are mains powered, so they should act as Thread routers: Aqara doesn't state it, but mains-powered Thread devices normally route. That's what fixes the weak spot. The Living P2 now attaches to <span class="live">${thName(liv.via)} at ${liv.L.pl.toFixed(0)} dB</span>, instead of reaching the M200 through the Living | Gaming wall at ${p2m["p2-liv"].pl.toFixed(0)} dB. Gaming <span class="live">${gmP.L.pl.toFixed(0)} dB via ${thName(gmP.via)}</span>, Master <span class="live">${msP.L.pl.toFixed(0)} dB via ${thName(msP.via)}</span>. The weakest link is <span class="live">${fzRoom}, ${fz.L.pl.toFixed(0)} dB (${GRADE_TEXT[worstGrade].toLowerCase()})</span>. H1 switches stay out of it: they don't carry Thread.</p>
    <ol>
      <li><b>Confirm the H2s route.</b> After pairing, check they show as routers in the Aqara app's Thread diagnostics or a Thread scanner app. If one runs as an end device, or its outlet is switched off at the wall, its P2 falls back to the M200 (Living about ${p2m["p2-liv"].pl.toFixed(0)} dB).</li>
      <li><b>Pair in Aqara Home on the M200 first</b>, then share to Apple Home. A Matter device joins the Thread network of the app that adds it, so adding the H2s from Apple Home first would put them on the HomePod mini's network.</li>
      <li><b>HomePod mini at the dining table</b> (${state.threadMerged ? "shown as sharing the M200's network" : "shown as a separate network, the safe assumption"}). If it does share one Thread network, it's a second border router in Living, so Matter control from Apple Home keeps working while the M200 restarts. Aqara automations still need the M200.</li>
      <li><b>Thread mode costs one H2 feature.</b> Aqara's comparison table gives per-socket power readings only in Zigbee mode; in Thread mode you get one combined reading per outlet.</li>
    </ol></div></article>
''')

# ---------- D. obstacles: TV cabinet + floor box
rep('      <li><b>Gaming gear:</b> a PC tower, monitors and consoles are metal boxes. Don\'t tuck the M200 behind the screens at the back of the desk.</li>',
    '''      <li><b>Gaming gear:</b> a PC tower, monitors and consoles are metal boxes. Don't tuck the M200 behind the screens at the back of the desk.</li>
      <li><b>The TV cabinet</b> holds the RT-BE92U. Closed doors and the TV's metal bracket cut its Wi-Fi.</li>
      <li><b>The sofa floor socket:</b> a metal floor-box lid shields the H2's radio, and so does a sofa with a metal base sitting right over it.</li>''')

# ---------- E. M200 placement bullets
rep('      <li><b>Avoid:</b> inside the display shelving or the top-hung cabinet; behind the PC or monitors; on the floor; within 1 m of the Wi-Fi AP, the G3, the M2 or the MagicPad S1 Plus.</li>\n      <li><b>Power and network:</b> USB-C 5 V 2 A over Wi-Fi 6 works. The desk CAT6 point is in this room, so if the final spot is in cable reach, use Ethernet; PoE powers it too.</li>',
    '      <li><b>Avoid:</b> inside the display shelving or the top-hung cabinet; behind the PC or monitors; on the floor; within 1 m of the Gaming BT8 (now <span class="live">${metres(m, anchor(byId("ap-gm"))).toFixed(1)} m</span> away), the G3, the M2 or the MagicPad S1 Plus.</li>\n      <li><b>Power and network:</b> USB-C 5 V 2 A over Wi-Fi works. For Ethernet, run a patch cable to a spare LAN port on the Gaming BT8 (2.5G + 2 × 1G). The BT8\'s spec lists no PoE, so keep USB-C power.</li>')

# ---------- F. Wi-Fi (new)
rep('      <li><b>After install:</b> check the ${fzRoom} P2 link in the Aqara app\'s Thread diagnostics, and test IR to all three ACs from the final controller positions.</li>\n    </ul></div></article>`;',
    r'''      <li><b>After install:</b> check the ${fzRoom} P2 link in the Aqara app's Thread diagnostics, and test IR to all three ACs from the final controller positions.</li>
    </ul></div></article>
  <article><div><h3>F. Wi-Fi</h3><div class="verdict ${cov >= 95 ? "g-strong" : "g-marginal"}">${cov >= 95 ? "Wi-Fi 7 AiMesh covers every room" : "Gaps at " + (100 - cov) + "% of the floor"}</div></div><div class="body">
    <p>The RT-BE92U sits at the TV cabinet where the fibre comes in, with ZenWiFi BT8 nodes in Bedroom 2 and the Gaming room on CAT6 backhaul, so the mesh doesn't spend airtime relaying between units. All three are tri-band Wi-Fi 7 (2.4, 5 and 6 GHz) and list both AiMesh router and node modes. At 2.4 GHz the model puts <span class="live">${cov}% of the floor at good or better</span>. The weakest smart-home device is <span class="live">${weak ? `${weak.d.name}, ${weak.a.L.pl.toFixed(0)} dB to the ${weak.a.ap.short}` : "—"}</span>. 5 and 6 GHz lose more through walls; the hubs mostly use 2.4 GHz anyway.</p>
    <ul>
      <li><b>Backhaul:</b> in AiMesh, set Ethernet backhaul. Plug each BT8's 2.5G WAN port into its CAT6 and the RT-BE92U end into a 2.5G LAN port (it has three), or into a switch if the runs land somewhere else.</li>
      <li><b>Fix the 2.4 GHz channel</b> on 1, 6 or 11 at 20 MHz on all three units, instead of auto. Zigbee 15, 20 and 25 sit in the gaps between those channels; 40 MHz on 2.4 GHz covers the gaps. Give Zigbee one of 15/20/25 and Thread another.</li>
      <li><b>A 2.4 GHz-friendly network for the hubs.</b> The M2 is 2.4 GHz only and Aqara devices pair on 2.4 GHz. Wi-Fi 7 features (MLO, WPA3-only, one name across bands) can block pairing. If a hub won't pair, give the smart-home devices a separate 2.4 GHz network with WPA2/WPA3.</li>
      <li><b>Don't isolate the hubs from your phones.</b> Matter and HomeKit find devices with multicast (mDNS). Put the M200 or HomePod mini on an isolated guest or IoT network and Apple Home control can break. Keep them on the same network as your iPhone, and test after any change.</li>
      <li><b>Spacing:</b> the HomePod mini is <span class="live">${metres(anchor(byId("homepod")), anchor(byId("ap-main"))).toFixed(1)} m</span> from the RT-BE92U and the M200 is <span class="live">${metres(m, anchor(byId("ap-gm"))).toFixed(1)} m</span> from the Gaming BT8. Keep hubs at least 1 m from the mesh units.</li>
      <li><b>Security:</b> keep automatic firmware updates on for the router, both nodes and the hubs, change the router's admin password, and switch off WPS.</li>
    </ul></div></article>`;''')

# ---------- review header computations
rep('''  const fz = farZone(), fzRoom = ROOMS.find(r => r.id === fz.room).name;''',
    '''  const fz = farZone(), fzRoom = fz ? ROOMS.find(r => r.id === fz.room).name : "—";
  const p2m = Object.fromEntries(D.filter(d => d.th === "end").map(d => [d.id, link(m, anchor(d))]));
  const pp = Object.fromEntries(s.p2.map(o => [o.d.id, o])), liv = pp["p2-liv"], gmP = pp["p2-gm"], msP = pp["p2-m"];
  // Wi-Fi: share of floor cells within "good" of the best mesh unit, and the weakest client
  const aps = D.filter(d => d.ap).map(anchor);
  let cells = 0, okCells = 0;
  for (let y = 194; y < 590; y += 7) for (let x = 68; x < 935; x += 7) {
    const q = { x, y };
    if (!inPoly(q, APARTMENT) || isWall(x, y)) continue;
    cells++; if (Math.min(...aps.map(a => link(a, q).pl)) <= 80) okCells++;
  }
  const cov = cells ? Math.round(100 * okCells / cells) : 0;
  const weak = Object.entries(WF.assoc).map(([id, a]) => ({ d: byId(id), a })).sort((x, y) => y.a.L.pl - x.a.L.pl)[0];''')
rep('  const worstGrade = grade(fz.L.pl);', '  const worstGrade = fz ? grade(fz.L.pl) : "weak";')

# ---------- open items
splice('  const items = [\n    ["Build", "S100 desk panel box"', '  $("#openList").innerHTML', r'''  const items = [
    ["Build", "S100 desk panel box", "3D-printed box wired to a UK 3-pin plug. Use flame-retardant filament (PETG or ABS, ideally V-0), a 3 A fused plug and a cord grip, and keep the earth connected. It can be unplugged, so it shouldn't carry Zigbee routes."],
    ["Validate", "H2 outlets routing Thread", "After pairing on the M200, check that all three H2s show as Thread routers. The Living P2 depends on the sofa H2; without it, that link drops to the M200 through a wall."],
    ["Check", "Sofa floor socket for the H2", "The floor box has to take a 146 × 86 mm wall-outlet module at least 25 mm deep (a 10 mm spacer comes in the box). A metal lid shields its radio."],
    ["Confirm", "CAT6 positions", "The Bedroom 2 run and the Gaming room's second point aren't on the drawings. Drag the BT8s to the real points, and note where the runs terminate for the backhaul."],
    ["Confirm", "M2 spot in Master", "Proposed at the window-side bedside table, powered from that H2's USB-C port. It needs a clear view of the AC's front; the IR check updates if you drag it."],
    ["Confirm", "Window-side Master bedside switch", "On the RCP (3G, 2-way: L27, L30, L31) but not in your H1 schedule. Normal switch, or dropped? Yard 2G and the hob 1G are normal switches."],
    ["Confirm", "Curtain motor end and G3 spot", "Which end of the Living track the two C3s sit on, and where exactly the G3 goes on the ceiling."],
    ["Research", "C3 and LED driver routing role", "Drawn as end devices as you asked. The C3 is mains powered and reports as a router in zigbee2mqtt; the drivers are unconfirmed."]
  ];
''')

# ---------- sources
rep('    <p><b>CAT6 points:</b> M&amp;E sheet (sheet 2), 2 units: Living TV wall and the Gaming desk.</p>',
    '''    <p><b>CAT6 points and sockets:</b> M&amp;E sheet (sheet 2): CAT6 at the Living TV wall and the Gaming desk; the sofa floor socket, both Master bedside sockets and the dining-table sockets used for the H2s and the HomePod mini. From you: the fibre comes in at the TV area, a CAT6 run was added to Bedroom 2, and the Gaming room has two CAT6 points.</p>
    <p><b>Network kit (checked on the makers' spec pages, 8 Oct 2026):</b> ASUS RT-BE92U (BE9700 tri-band, 1 × 10G + 1 × 2.5G WAN/LAN, 3 × 2.5G LAN, AiMesh router or node) and ZenWiFi BT8 (BE14000 tri-band, 2.5G WAN, 2.5G LAN, 2 × 1G LAN, AiMesh router or node), from asus.com tech specs. Aqara Wall Outlet H2 UK: Thread, Bluetooth and Zigbee, switchable, Thread by default; per-socket power readings in Zigbee mode only (aqara.com/en/product/wall-outlet-h2-uk).</p>''')
rep('    <p><b>Unconfirmed:</b> the LED driver\'s routing role; whether the S100 routes; whether the M200 and HomePod mini merge into one Thread network.</p>',
    '    <p><b>Unconfirmed:</b> that the H2 outlets act as Thread routers in Matter mode (expected for mains-powered Thread devices; Aqara doesn\'t state it); the LED driver\'s routing role; whether the S100 routes; whether the M200 and HomePod mini merge into one Thread network.</p>')
rep('Doors are treated as open. It\'s a placement guide, not a survey.</p>`;', 'The Wi-Fi coverage map uses the same 2.4 GHz model. Doors are treated as open. It\'s a placement guide, not a survey.</p>`;')

# ---------- tray: hide when everything is placed
rep('function renderTray() {\n  const t = $("#tray");', 'function renderTray() {\n  const t = $("#tray");\n  t.hidden = !UNPLACED.length;')

p.write_text(s)
print("ok")
