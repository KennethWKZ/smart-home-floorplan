import sys, pathlib
from playwright.sync_api import sync_playwright
root = pathlib.Path(sys.argv[1]); out = root / ".impeccable/review"
sheet = (root / "share/led-power.html").read_text()
wrapped = root / "build/led-preview.html"
wrapped.write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>' + sheet + "</body></html>")
with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"file://{root}/index.html"); pg.wait_for_timeout(900)
    print("main scrollW", pg.evaluate("document.documentElement.scrollWidth"))
    pg.screenshot(path=str(out / "m-top.png"), clip={"x": 0, "y": 0, "width": 390, "height": 760})
    pg.evaluate("window.__plan.setView('thread')"); pg.wait_for_timeout(400)
    pg.locator("#viewPanel").screenshot(path=str(out / "m-thread-panel.png"))
    pg.locator("#btnPause").click(); pg.wait_for_timeout(100)
    print("pause label now:", pg.locator("#btnPause").get_attribute("aria-label"))
    pg.locator("#led").screenshot(path=str(out / "m-led.png"))
    # button widths: anything wider than its text needs?
    print(pg.evaluate("""() => [...document.querySelectorAll('.btn, .led-btn')].filter(b => b.offsetParent).map(b => (b.id || b.className) + ':' + Math.round(b.getBoundingClientRect().width)).join(' ')"""))
    ctx.close()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, color_scheme="dark", device_scale_factor=2); pg = ctx.new_page()
    pg.goto(f"file://{wrapped}"); pg.wait_for_timeout(700)
    print("sheet scrollW", pg.evaluate("document.documentElement.scrollWidth"))
    pg.screenshot(path=str(out / "m-sheet-dark.png"), full_page=True)
    ctx.close(); b.close(); print("errors:", errs or "none")
