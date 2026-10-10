import sys, json
from playwright.sync_api import sync_playwright
root = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1440, "height": 1000}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"file://{root}/index.html"); pg.wait_for_timeout(1200)
    r = pg.evaluate("() => Object.entries(TH.routes).map(([k, v]) => k + ': ' + v.join(' > ') + ' ' + TH.linkTo[k].pl.toFixed(0) + ' dB')")
    print("\n".join(r))
    t = pg.locator("#reviewBody").inner_text(); i = t.find("F. Wi-Fi"); print(t[i:i+700])
    pg.evaluate("state.threadMerged = true; drawThread(false); renderReview()")
    print("merged:", pg.evaluate("() => Object.entries(TH.routes).map(([k, v]) => k + ':' + v.join('>')).join(' | ')"))
    print("errors:", errs or "none"); b.close()
