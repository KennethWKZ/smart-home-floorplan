"""Write per-view SVG (editable, layered) and 2x PNG renders into the plan's exports/.

usage: uv run tools/export.py plans/<name>
"""
import sys, pathlib, json
from playwright.sync_api import sync_playwright
root = pathlib.Path(sys.argv[1]).resolve(); out = root / "exports"; out.mkdir(exist_ok=True); (root / ".impeccable/review").mkdir(parents=True, exist_ok=True)
pre = json.loads((root / "plan.json").read_text(encoding="utf-8"))["code"].lower()
names = {"master": "1-master-plan", "zigbee": "2-zigbee-mesh", "thread": "3-thread-matter", "wifi": "4-wifi-lan", "ir": "5-ir-aircon", "led": "6-led-power", "circuits": "7-switch-circuits"}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 1000}, color_scheme="light")
    pg.goto((root / "index.html").as_uri()); pg.wait_for_timeout(900)
    for v, n in names.items():
        pg.evaluate(f"window.__plan.setView('{v}')"); pg.wait_for_timeout(400)
        svg = pg.evaluate("window.__plan.exportSVGString()")
        (out / f"{pre}-{n}.svg").write_text(svg, encoding="utf-8")
        r = b.new_page(viewport={"width": 1896, "height": 1156}, device_scale_factor=2)
        r.set_content(f'<html><body style="margin:0">{svg.split("?>",1)[1]}</body></html>'); r.wait_for_timeout(1500)
        r.locator("svg").first.screenshot(path=str(out / f"{pre}-{n}.png")); r.close()
        print(n, len(svg) // 1024, "KB svg")
    # verify the zigbee trace survives the click now
    pg.evaluate("window.__plan.setView('zigbee')"); pg.wait_for_timeout(300)
    pg.locator('[data-id="drv-head"]').click(); pg.wait_for_timeout(2500)
    print("tracing:", pg.evaluate("document.querySelector('#plan').classList.contains('tracing')"),
          "| selection:", pg.evaluate("document.querySelector('#selPanel h2').textContent"))
    pg.locator("#stage").screenshot(path=str(root / ".impeccable/review/desktop-zigbee-trace.png"))
    # drag M200 toward the sofa and confirm Master thread link worsens
    before = pg.evaluate("window.__plan.state.view")
    pg.evaluate("window.__plan.setView('thread')"); pg.wait_for_timeout(300)
    t0 = pg.locator("#p2facts").inner_text()
    pg.locator('#viewPanel #btnBest').click(); pg.wait_for_timeout(1500)
    t1 = pg.locator("#p2facts").inner_text()
    print("thread before:", " | ".join(t0.split("\n")[1::3]), "\nafter best-spot:", " | ".join(t1.split("\n")[1::3]))
    print("m200 at", pg.evaluate("(() => { const d = document.querySelector('[data-id=m200]'); return d.getAttribute('transform'); })()"))
    pg.locator("#stage").screenshot(path=str(root / ".impeccable/review/desktop-thread-best.png"))
    b.close()
