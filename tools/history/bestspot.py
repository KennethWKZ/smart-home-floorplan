import sys, json
from playwright.sync_api import sync_playwright
root = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"file://{root}/index.html"); pg.wait_for_timeout(800)
    print(json.dumps(pg.evaluate("bestSpot()")), "errors:", errs or "none"); b.close()
