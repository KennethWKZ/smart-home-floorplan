import sys
from playwright.sync_api import sync_playwright
root = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1440, "height": 1000})
    pg.goto(f"file://{root}/index.html"); pg.wait_for_timeout(900)
    for sel in ("#reviewBody", "#openList"): print(pg.locator(sel).inner_text()[:4200], "\n-----")
    b.close()
