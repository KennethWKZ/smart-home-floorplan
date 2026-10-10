"""Build a plan's index.html (plan page) and share/ LED sheets from its src/ and build/ folders.

usage: uv run tools/build.py plans/<name>
"""
import json, pathlib, re, sys

if len(sys.argv) != 2:
    sys.exit("usage: uv run tools/build.py plans/<name>")
root = pathlib.Path(sys.argv[1]).resolve()
need = ["plan.json", "src/template.html", "src/led-section.html", "build/geometry.json", "build/rcp.json"]
missing = [n for n in need if not (root / n).is_file()]
if missing:
    sys.exit(f"{root.name}: missing {', '.join(missing)}. See CLAUDE.md, 'Make a plan for a new home'.")

read = lambda n: (root / n).read_text(encoding="utf-8")
meta = json.loads(read("plan.json"))
code, label = meta["code"], meta["label"]
geo, rcp = json.loads(read("build/geometry.json")), json.loads(read("build/rcp.json"))
tpl, led = read("src/template.html"), read("src/led-section.html")

out = tpl.replace("__GEOMETRY_JSON__", json.dumps(geo, separators=(",", ":"))).replace("__RCP_JSON__", json.dumps(rcp, separators=(",", ":"))).replace("<!--LED_SECTION-->", led)
(root / "index.html").write_text(out, encoding="utf-8")
print("index.html", len(out) // 1024, "KB")

# contractor sheet: same tokens, LED block only (no floor plan, locks or cameras). The artifact host adds the doctype/head/body skeleton.
tokens = re.search(r"/\* tokens:start \*/(.*?)/\* tokens:end \*/", tpl, re.S).group(1)
sheet_led = led.replace('<h2 class="led-title" id="ledTitle">LED strip power</h2>', '<h1 class="led-title" id="ledTitle">LED strip power</h1>')
sheet = f"""<title>{code} LED Strip Power</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600&display=swap" rel="stylesheet">
<style>
/* Layout: one centred working sheet on the grey drawing-table ground, same palette as the network plan */
{tokens}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--table); color: var(--ink); font: 400 15px/1.55 Jost, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; font-variant-numeric: tabular-nums; }}
::selection {{ background: color-mix(in srgb, var(--zb) 28%, transparent); color: var(--ink); }}
.sheet-page {{ max-width: 1120px; margin: 0 auto; padding-inline: 24px; padding-block: 28px 48px; display: grid; gap: 14px; }}
.sheet-ref {{ margin: 0; font-size: .86rem; color: var(--ink-3); }}
.sheet-ref b {{ color: var(--ink-2); font-weight: 500; }}
@media (max-width: 760px) {{ .sheet-page {{ padding-inline: 16px; padding-block: 20px 36px; }} }}
</style>
<main class="sheet-page">
<p class="sheet-ref"><b>{label}</b> · lighting supply check for the contractor</p>
{sheet_led}
</main>
"""
(root / "share").mkdir(exist_ok=True)
(root / "share/led-power.html").write_text(sheet, encoding="utf-8")
print("share/led-power.html", len(sheet) // 1024, "KB")
# the same sheet as a complete document, for sending as a file (WhatsApp, email)
doc = sheet.replace("<title>", '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<title>', 1)
doc = doc.replace("</style>\n<main", "</style>\n</head>\n<body>\n<main", 1) + "</body>\n</html>\n"
(root / f"share/{code}-LED-strip-power.html").write_text(doc, encoding="utf-8")
print(f"share/{code}-LED-strip-power.html", len(doc) // 1024, "KB")
