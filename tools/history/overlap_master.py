import sys
from playwright.sync_api import sync_playwright
JS = """(view) => {
  window.__plan.setView(view);
  const tiles = [...document.querySelectorAll('#devices .dev')].filter(g => !g.classList.contains('vis-off')).map(g => ({ n: g.dataset.id, r: g.querySelector('.tile').getBoundingClientRect() }));
  const extra = [...document.querySelectorAll('#ledpower .led-card, #ledpower .psu')].map(e => ({ n: e.classList.contains('psu') ? 'psu' : 'card', r: e.getBoundingClientRect() }));
  const all = view === 'led' ? tiles.concat(extra) : tiles, hits = [];
  for (let i = 0; i < all.length; i++) for (let j = i + 1; j < all.length; j++) { const a = all[i].r, c = all[j].r;
    if (a.left < c.right - 1 && c.left < a.right - 1 && a.top < c.bottom - 1 && c.top < a.bottom - 1) hits.push(all[i].n + ' x ' + all[j].n); }
  return view + ': ' + (hits.length ? hits.join(' | ') : 'no overlaps');
}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1440, "height": 1000}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"file://{sys.argv[1]}/index.html"); pg.wait_for_timeout(800)
    for v in ("master", "zigbee", "led"): print(pg.evaluate(JS, v))
    print("drv-head:", pg.evaluate("[byId('drv-head').x, byId('drv-head').y, (ZB.routes['drv-head'] || []).join('>')]"), "| errors:", errs or "none"); b.close()
