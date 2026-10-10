"""Start a new plan folder from an existing one (the starting template) and a customer's PDF.

usage: uv run tools/new_plan.py <name> --pdf <path to drawings.pdf> [--code ABC123] [--from example]

Creates plans/<name>/ with the PDF as source/plan.pdf, a copy of the template plan's src/,
and a plan.json. Walls, devices and rooms still come from the template plan until the
agent re-extracts them; see CLAUDE.md, 'Make a plan for a new home'.
"""
import argparse, json, pathlib, re, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser(description="Start a new plan folder")
ap.add_argument("name", help="short folder name, e.g. tan-condo-b12")
ap.add_argument("--pdf", required=True, help="the customer's drawings PDF (exported from CAD, not a scan)")
ap.add_argument("--code", help="short label shown on the page (default: the folder name in capitals)")
ap.add_argument("--from", dest="base", default="example", help="plan to copy src/ from (default example)")
a = ap.parse_args()

if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,40}", a.name):
    sys.exit("Use a short folder name of lowercase letters, numbers and dashes, e.g. tan-condo-b12.")
dest, base, pdf = ROOT / "plans" / a.name, ROOT / "plans" / a.base, pathlib.Path(a.pdf).expanduser()
if dest.exists():
    sys.exit(f"plans/{a.name} already exists; pick another name.")
if not (base / "src").is_dir():
    sys.exit(f"plans/{a.base}/src not found; pass --from with an existing plan.")
if not pdf.is_file() or pdf.suffix.lower() != ".pdf":
    sys.exit(f"{pdf} is not a PDF file.")

for sub in ("source", "build", "share", "exports", "inbox"):
    (dest / sub).mkdir(parents=True)
shutil.copy2(pdf, dest / "source/plan.pdf")
shutil.copytree(base / "src", dest / "src", dirs_exist_ok=True)
code = a.code or a.name.upper()
(dest / "plan.json").write_text(json.dumps({"code": code, "label": code, "pdf": "source/plan.pdf", "from": a.base, "notes": ""}, indent=2) + "\n", encoding="utf-8")
print(f"created plans/{a.name} (src/ copied from plans/{a.base}, PDF at source/plan.pdf)")
