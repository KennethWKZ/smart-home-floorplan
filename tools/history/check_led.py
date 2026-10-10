import sys, pathlib
from playwright.sync_api import sync_playwright
root = pathlib.Path(sys.argv[1]); out = root / ".impeccable/review"
sheet = (root / "share/led-power.html").read_text()
wrapped = root / "build/led-preview.html"
wrapped.write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>' + sheet + "</body></html>")
with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    for label, vp, scheme in (("desk-light", {"width": 1280, "height": 900}, "light"), ("phone-dark", {"width": 390, "height": 844}, "dark")):
        ctx = b.new_context(viewport=vp, color_scheme=scheme, device_scale_factor=2 if "phone" in label else 1); pg = ctx.new_page()
        pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(f"file://{wrapped}"); pg.wait_for_timeout(700)
        pg.screenshot(path=str(out / f"led-sheet-{label}.png"), full_page=True)
        print(label, "scrollW", pg.evaluate("document.documentElement.scrollWidth"), "vs", vp["width"])
        if label == "desk-light":
            print("summary:", pg.locator("#led-summary").inner_text().replace("\n", " "))
            rows = pg.evaluate("""() => [...document.querySelectorAll('#led-rows tr')].map(tr => [...tr.querySelectorAll('td')].map(td => td.innerText.replace(/\\s+/g, ' ').trim()).join(' | '))""")
            print("\n".join(rows))
            pg.fill("#led-wpm-gaming", "20"); pg.fill("#led-wpm-tv", "20"); pg.wait_for_timeout(100)
            print("after 20 W/m:", pg.locator("#led-summary").inner_text().replace("\n", " "))
            print(pg.evaluate("""() => document.querySelector('#led-rows tr[data-k=gaming]').innerText.replace(/\\s+/g, ' ')"""))
            print("copy text:\n" + pg.evaluate("document.querySelector('#led-copy') && (() => { return null })()") .__str__())
        ctx.close()
    # main page section
    ctx = b.new_context(viewport={"width": 1440, "height": 1000}); pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append("main: " + str(e)))
    pg.goto(f"file://{root}/index.html"); pg.wait_for_timeout(900)
    pg.locator("#led").screenshot(path=str(out / "led-main.png"))
    print("main has #led:", pg.locator("#led").count(), "foyer P2 route:", pg.evaluate("(TH.routes['p2-foyer'] || ['NO']).join('>') + ' ' + (TH.linkTo['p2-foyer'] ? TH.linkTo['p2-foyer'].pl.toFixed(0) + ' dB' : '')"))
    ctx.close(); b.close()
    print("errors:", errs or "none")
