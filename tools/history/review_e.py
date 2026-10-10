import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1440, "height": 1000})
    pg.goto(f"file://{sys.argv[1]}/index.html"); pg.wait_for_timeout(1000)
    t = pg.locator("#reviewBody").inner_text()
    for a, z in (("B. Thread", "\n1"), ("C. IR", "D. RF"), ("E. Where", "F. Wi-Fi")): i = t.find(a); print(t[i:t.find(z, i)][:1300], "\n---")
    b.close()
