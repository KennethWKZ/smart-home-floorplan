import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 390, "height": 844}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"file://{sys.argv[1]}"); pg.wait_for_timeout(700)
    print("mode:", pg.evaluate("document.compatMode"), "| scrollW:", pg.evaluate("document.documentElement.scrollWidth"), "| rows:", pg.locator("#led-rows tr").count(), "| errors:", errs or "none")
    b.close()
