import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(f"{e}\n{e.stack[:600] if e.stack else ''}"))
    pg.goto(f"file://{sys.argv[1]}/index.html"); pg.wait_for_timeout(800)
    print("\n".join(errs) or "no errors"); b.close()
