import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto(f"file://{sys.argv[1]}/index.html"); pg.wait_for_timeout(900)
    for merged in (False, True):
        pg.evaluate(f"state.threadMerged = {str(merged).lower()}; drawThread(false)")
        print("merged" if merged else "separate", pg.evaluate("""() => ['lock-u500','p2-liv','p2-gm','p2-m'].map(id => id + ': ' + (TH.routes[id] || ['NO ROUTE']).join('>') + ' ' + (TH.linkTo[id] ? TH.linkTo[id].pl.toFixed(0) + 'dB/' + TH.linkTo[id].w + 'w' : '')).join(' | ')"""))
    print("u500 direct:", pg.evaluate("""() => ['m200','h2-sofa','homepod'].map(id => { const L = link(anchor(byId('lock-u500')), anchor(byId(id))); return id + ' ' + L.pl.toFixed(0) + 'dB ' + L.d.toFixed(1) + 'm ' + L.w + 'w'; }).join(' | ')"""))
    print("d100:", pg.evaluate("(ZB.routes['lock-d100'] || ['NO']).join('>')"), "| zb devices:", pg.evaluate("D.filter(d => d.zb && d.zb !== 'pan' && d.zb !== 'coord').length"))
    b.close()
