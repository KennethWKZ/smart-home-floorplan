"""Read device positions from an exported plan SVG (data only; nothing in it is executed).

usage: uv run tools/read_export.py plans/<name>/inbox/<date>/<file>.svg plans/<name>/inbox/<date>/positions.json
"""
import sys, re, json
import xml.etree.ElementTree as ET
NS = "{http://www.w3.org/2000/svg}"
root = ET.parse(sys.argv[1]).getroot()
out = {}
for g in root.iter(NS + "g"):
    did = g.get("data-id")
    if not did: continue
    m = re.match(r"translate\(([-\d.]+)[ ,]+([-\d.]+)\)", g.get("transform") or "")
    if m: out[did] = [round(float(m.group(1)), 1), round(float(m.group(2)), 1)]
with open(sys.argv[2], "w", encoding="utf-8") as fh: json.dump(out, fh, indent=0)
print(len(out), "devices")
