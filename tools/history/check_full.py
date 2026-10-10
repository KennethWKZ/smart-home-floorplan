import sys, pathlib
from playwright.sync_api import sync_playwright
root = pathlib.Path(sys.argv[1]); out = root / ".impeccable/review"
with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, has_touch=True, is_mobile=True); pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"file://{root}/index.html"); pg.wait_for_timeout(900)
    pg.locator("#btnFull").click(); pg.wait_for_timeout(400)
    print("full:", pg.evaluate("document.querySelector('#stage').classList.contains('full')"), "vb:", pg.evaluate("document.querySelector('#plan').getAttribute('viewBox')"),
          "stage box:", pg.evaluate("JSON.stringify(document.querySelector('#stage').getBoundingClientRect().toJSON())"))
    pg.screenshot(path=str(out / "m-full.png"))
    # one-finger pan via pointer events on empty plan area
    before = pg.evaluate("state.vb.slice()")
    box = pg.locator("#plan").bounding_box(); x, y = box["x"] + box["width"] * .5, box["y"] + box["height"] * .15
    pg.mouse.move(x, y); pg.mouse.down(); pg.mouse.move(x - 120, y, steps=6); pg.mouse.up()
    after = pg.evaluate("state.vb.slice()")
    print("pan dx (plan units):", round(after[0] - before[0], 1))
    print("bars hidden after pan:", pg.evaluate("document.querySelector('#stage').classList.contains('chrome-off')"))
    pg.wait_for_timeout(200); pg.mouse.click(x - 60, y); pg.wait_for_timeout(400)   # a tap on empty plan brings the bars back
    print("bars back after tap:", not pg.evaluate("document.querySelector('#stage').classList.contains('chrome-off')"))
    pg.locator(".views .tab[data-view=wifi]").click(); pg.wait_for_timeout(500)
    pg.screenshot(path=str(out / "m-full-wifi.png"))
    pg.locator("#btnFullClose").click(); pg.wait_for_timeout(300)
    print("after close full:", pg.evaluate("document.querySelector('#stage').classList.contains('full')"), "nav back in place:", pg.evaluate("document.querySelector('.views').parentElement.tagName"),
          "vb:", pg.evaluate("document.querySelector('#plan').getAttribute('viewBox')"), "scrollW:", pg.evaluate("document.documentElement.scrollWidth"))
    ctx.close()
    ctx = b.new_context(viewport={"width": 1440, "height": 1000}); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"file://{root}/index.html"); pg.wait_for_timeout(900)
    print("desktop vb:", pg.evaluate("document.querySelector('#plan').getAttribute('viewBox')"))
    pg.evaluate("window.__plan.setView('wifi')"); pg.wait_for_timeout(500)
    pg.locator("#stage").screenshot(path=str(out / "desktop-wifi.png"))
    ctx.close(); b.close(); print("errors:", errs or "none")
