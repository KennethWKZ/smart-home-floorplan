import sys, json, pathlib
from playwright.sync_api import sync_playwright
root = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1440, "height": 1000}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto((pathlib.Path(root).resolve() / "index.html").as_uri()); pg.wait_for_timeout(1200)
    print("errors:", errs or "none")
    print(json.dumps(pg.evaluate("""() => ({
      th: Object.fromEntries(Object.entries(TH.routes).map(([k, v]) => [k, v.join('>') + ' ' + TH.linkTo[k].pl.toFixed(0) + 'dB'])),
      wf: Object.fromEntries(Object.entries(WF.assoc).map(([k, a]) => [k, a.ap.id + ' ' + a.L.pl.toFixed(0) + 'dB'])),
      zbN: Object.keys(ZB.routes).length, best: bestSpot(), tray: document.querySelector('#tray').hidden })"""), indent=0))
    import time; t = time.time(); pg.evaluate("window.__plan.setView('wifi')"); print("wifi view ms", round((time.time()-t)*1000))
    t = time.time(); pg.evaluate("drawThread(false)"); print("thread draw ms", round((time.time()-t)*1000))
    for sel in ("#reviewBody",): txt = pg.locator(sel).inner_text(); print(txt[txt.find("B. Thread"):txt.find("C. IR")][:1500]); print(txt[txt.find("F. Wi-Fi"):][:1800])
    print("errors after:", errs or "none"); b.close()
