import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1440, "height": 1000}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"file://{sys.argv[1]}/index.html"); pg.wait_for_timeout(800)
    pg.evaluate("window.__plan.setView('wifi')"); pg.wait_for_timeout(300)
    # every Wi-Fi packet path that reaches the router must hug a drawn backhaul curve (sampled), not cut straight across
    r = pg.evaluate("""() => {
      const paths = [...document.querySelectorAll('#wifi .pkt-wf animateMotion')].map(a => a.getAttribute('path'));
      const curves = [...document.querySelectorAll('#wifi .eth.backhaul')];
      let worst = 0;
      for (const d of paths) {
        const pts = d.slice(1).split('L').map(s => s.split(' ').map(Number));
        if (pts.length <= 2) continue;                       // client straight to the main router
        for (const [x, y] of pts.slice(1)) {                 // from the node onwards
          let best = Infinity;
          for (const c of curves) { const L = c.getTotalLength(); for (let i = 0; i <= 200; i++) { const q = c.getPointAtLength(L * i / 200); best = Math.min(best, Math.hypot(q.x - x, q.y - y)); } }
          worst = Math.max(worst, best);
        }
      }
      return { packets: paths.length, viaNode: paths.filter(d => d.split('L').length > 2).length, worstOffCurve: +worst.toFixed(2) };
    }""")
    print(r, "| M200:", pg.evaluate("[byId('m200').x, byId('m200').y]"), "| errors:", errs or "none"); b.close()
