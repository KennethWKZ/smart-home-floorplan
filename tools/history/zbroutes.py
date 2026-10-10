import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto(f"file://{sys.argv[1]}/index.html"); pg.wait_for_timeout(800)
    print(pg.evaluate("() => D.filter(d => d.zb === 'end').map(d => d.id + ': ' + (ZB.routes[d.id] || ['NO ROUTE']).join(' > ')).join('\\n')"))
    print("max hops", pg.evaluate("Math.max(...Object.values(ZB.hops))"), "routed", pg.evaluate("Object.keys(ZB.routes).length"))
    b.close()
