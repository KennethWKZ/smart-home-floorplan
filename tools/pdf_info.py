"""Check a drawings PDF and render each page to PNG, so you can see which sheet is which.

usage: uv run tools/pdf_info.py plans/<name>/source/plan.pdf [out_dir]

Per page it prints the paper size, how many vector drawing items and text spans it holds,
and a verdict. A CAD export has thousands of drawing items; a scan or photo has almost none,
and the plan tools can't trace walls from it.
"""
import pathlib, sys
import pymupdf as fitz

if len(sys.argv) not in (2, 3):
    sys.exit("usage: uv run tools/pdf_info.py <drawings.pdf> [out_dir]")
pdf = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2]) if len(sys.argv) == 3 else pdf.parent.parent / "renders"
out.mkdir(parents=True, exist_ok=True)
doc = fitz.open(pdf)
print(f"{pdf.name}: {doc.page_count} page(s)")
for i, page in enumerate(doc):
    w, h = page.rect.width, page.rect.height
    drawings, spans = len(page.get_drawings()), sum(len(l["spans"]) for b in page.get_text("dict")["blocks"] for l in b.get("lines", []))
    images = len(page.get_images())
    verdict = "vector (traceable)" if drawings > 300 else "mostly image: ask for the CAD PDF export" if images else "little content"
    png = out / f"page-{i + 1}.png"
    page.get_pixmap(dpi=110).save(png)
    print(f"  page {i + 1}: {w:.0f} x {h:.0f} pt ({w / 72 * 25.4:.0f} x {h / 72 * 25.4:.0f} mm), "
          f"{drawings} drawing items, {spans} text spans, {images} images -> {verdict}; preview {png}")
