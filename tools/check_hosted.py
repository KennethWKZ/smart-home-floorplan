"""Load a published ht-ml.app page: first without the password (the gate), then with it."""
import sys, tempfile, pathlib
from playwright.sync_api import sync_playwright

url, pwd = sys.argv[1], sys.argv[2]
host = url.split("//")[1].strip("/")
with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2)
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(url); pg.wait_for_timeout(800)
    print("gate: inputs", pg.locator("input").count(), "| buttons", pg.locator("button, input[type=submit]").count(), "| text:", pg.inner_text("body")[:160].replace("\n", " "))
    pg.screenshot(path=str(pathlib.Path(tempfile.gettempdir()) / "gate.png"))
    errs.clear()   # the gate's own 401 is expected
    ctx.add_cookies([{"name": "ht_ml_pwd", "value": pwd, "domain": host, "path": "/"}])
    pg.goto(url); pg.wait_for_timeout(1500)
    print("title:", pg.title(), "| devices:", pg.evaluate("document.querySelectorAll('#devices .dev').length"),
          "| zigbee routes:", pg.evaluate("Object.keys(window.__plan.ZB().routes).length"), "| scrollW:", pg.evaluate("document.documentElement.scrollWidth"))
    pg.locator('.tab[data-view="led"]').click(); pg.wait_for_timeout(400)
    print("LED cards:", pg.evaluate("document.querySelectorAll('#ledpower .led-card').length"), "| Jost loaded:", pg.evaluate("document.fonts.check('16px Jost')"))
    pg.screenshot(path=str(pathlib.Path(tempfile.gettempdir()) / "hosted.png"))
    print("errors:", errs or "none"); b.close()
