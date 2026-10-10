"""Load index.html, collect console errors, screenshot each view at desktop + mobile."""
import sys, json
from playwright.sync_api import sync_playwright
root = sys.argv[1]; out = sys.argv[2]
views = ["master", "zigbee", "thread", "wifi", "ir"]
with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    for label, vp, scale in (("desktop", {"width": 1440, "height": 1000}, 1), ("mobile", {"width": 390, "height": 844}, 2)):
        ctx = b.new_context(viewport=vp, device_scale_factor=scale, color_scheme="light")
        pg = ctx.new_page()
        pg.on("console", lambda m: errs.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
        pg.goto("file://" + root + "/index.html"); pg.wait_for_timeout(900)
        for v in views:
            pg.evaluate(f"window.__plan.setView('{v}')"); pg.wait_for_timeout(700)
            if label == "desktop":
                pg.locator("#stage").screenshot(path=f"{out}/{label}-{v}.png")
            elif v in ("master", "thread"):
                pg.locator("#stage").screenshot(path=f"{out}/{label}-{v}.png")
        pg.evaluate("window.__plan.setView('master')"); pg.wait_for_timeout(500)
        pg.screenshot(path=f"{out}/{label}.png", full_page=True)
        info = pg.evaluate("""() => ({ docW: document.documentElement.scrollWidth, winW: innerWidth,
           routes: Object.keys(window.__plan.ZB().routes).length, hops: window.__plan.ZB().hops })""")
        print(label, json.dumps(info))
        ctx.close()
    # dark theme + trace
    ctx = b.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="dark"); pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(f"pageerror(dark): {e}"))
    pg.goto("file://" + root + "/index.html"); pg.wait_for_timeout(800)
    pg.evaluate("window.__plan.setView('zigbee')"); pg.wait_for_timeout(300)
    pg.locator('[data-id="drv-head"]').click(); pg.wait_for_timeout(2600)
    pg.locator("#stage").screenshot(path=f"{out}/dark-zigbee-trace.png")
    pg.evaluate("window.__plan.setView('thread')"); pg.wait_for_timeout(700)
    pg.locator("#stage").screenshot(path=f"{out}/dark-thread.png")
    svgstr = pg.evaluate("window.__plan.exportSVGString()")
    print("export svg bytes", len(svgstr))
    ctx.close(); b.close()
    print("ERRORS:", errs if errs else "none")
