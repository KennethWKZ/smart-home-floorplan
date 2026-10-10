import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1440, "height": 1000})
    pg.goto(f"file://{sys.argv[1]}/index.html"); pg.wait_for_timeout(800)
    pg.locator('.tab[data-view="led"]').click(); pg.wait_for_timeout(400)
    print(pg.evaluate("""() => {
      const boxes = [...document.querySelectorAll('#ledpower .led-card, #ledpower .psu'), ...[...document.querySelectorAll('#devices .dev')].filter(g => !g.classList.contains('vis-off')).map(g => g.querySelector('.tile'))]
        .map(e => ({ n: (e.closest('.led-card') ? 'card:' + e.querySelector('text.t').textContent : e.closest('.psu') ? 'psu' : 'dev:' + e.closest('.dev').dataset.id), r: e.getBoundingClientRect() }));
      const hits = [];
      for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i].r, c = boxes[j].r;
        if (a.left < c.right - 1 && c.left < a.right - 1 && a.top < c.bottom - 1 && c.top < a.bottom - 1) hits.push(boxes[i].n + ' x ' + boxes[j].n);
      }
      return hits.length ? hits.join(' | ') : 'no overlaps';
    }"""))
    b.close()
