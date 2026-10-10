import sys, json
from playwright.sync_api import sync_playwright
url = f"file://{sys.argv[1]}/index.html"
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_timeout(600)
    print("fresh browser M200:", pg.evaluate("[byId('m200').x, byId('m200').y]"))
    # simulate a viewer with an older saved layout: M200 at the desk, P2 Living dragged
    pg.evaluate("""() => { localStorage.setItem('example:pos-v12', JSON.stringify(Object.assign(
        Object.fromEntries(D.filter(d => d.status !== 'drawing').map(d => [d.id, { x: d.x, y: d.y }])),
        { m200: { x: 716.8, y: 262.2 }, 'p2-liv': { x: 330, y: 300 } }))); localStorage.removeItem('example:layoutRev'); }""")
    pg.reload(); pg.wait_for_timeout(600)
    print("saved layout -> M200:", pg.evaluate("[byId('m200').x, byId('m200').y]"), "| P2 Living kept:", pg.evaluate("[byId('p2-liv').x, byId('p2-liv').y]"),
          "| rev:", pg.evaluate("localStorage.getItem('example:layoutRev')"))
    # a later drag of the M200 must stick across reloads
    pg.evaluate("moveDevice(byId('m200'), 700, 300); savePositions()"); pg.reload(); pg.wait_for_timeout(600)
    print("after user drag + reload M200:", pg.evaluate("[byId('m200').x, byId('m200').y]"))
    b.close(); print("errors:", errs or "none")
