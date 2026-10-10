import sys, pathlib
from playwright.sync_api import sync_playwright
root = pathlib.Path(sys.argv[1]); out = root / ".impeccable/review"
with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    for label, vp, scheme in (("desktop", {"width": 1440, "height": 1000}, "light"), ("dark", {"width": 1440, "height": 1000}, "dark")):
        ctx = b.new_context(viewport=vp, color_scheme=scheme); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"file://{root}/index.html"); pg.wait_for_timeout(900)
        pg.locator('.tab[data-view="led"]').click(); pg.wait_for_timeout(600)
        pg.locator("#stage").screenshot(path=str(out / f"led-view-{label}.png"))
        if label == "desktop":
            print("cards:", pg.evaluate("[...document.querySelectorAll('#ledpower .led-card text')].map(t => t.textContent).join(' | ')"))
            print("panel:", pg.locator("#viewPanel .facts").inner_text().replace("\n", " · ")[:400])
            pg.fill("#led-wpm-head", "40"); pg.wait_for_timeout(200)
            print("after headboard 40 W/m:", pg.evaluate("[...document.querySelectorAll('#ledpower .led-card text')].map(t => t.textContent).filter(t => t.includes('172') || t.includes('Over') || t.includes('300')).join(' | ')"))
            print("drivers visible:", pg.evaluate("[...document.querySelectorAll('#devices .dev')].filter(g => !g.classList.contains('vis-off')).map(g => g.dataset.id).join(',')"))
        ctx.close()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, has_touch=True, is_mobile=True); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"file://{root}/index.html"); pg.wait_for_timeout(900)
    print("phone tab labels:", pg.evaluate("[...document.querySelectorAll('.tab')].map(t => getComputedStyle(t.querySelector('.lbl-short')).display === 'none' ? t.querySelector('.lbl-long').textContent : t.querySelector('.lbl-short').textContent).join(' / ')"), "scrollW", pg.evaluate("document.documentElement.scrollWidth"))
    pg.locator("#btnFull").click(); pg.wait_for_timeout(300); pg.locator('.tab[data-view="led"]').click(); pg.wait_for_timeout(500)
    pg.screenshot(path=str(out / "led-view-phone-full.png"))
    ctx.close(); b.close(); print("errors:", errs or "none")
