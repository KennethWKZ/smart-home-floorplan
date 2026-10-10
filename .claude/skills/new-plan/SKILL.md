---
name: new-plan
description: Make a smart-home plan page for a new customer home from its architect drawings PDF, or rework an existing plan's rooms, devices or walls. Use when the user brings a new floor plan, drawing or PDF, or says "new customer", "new house", "new plan".
---

# Make a plan for a new home

Goal: `plans/<name>/index.html` shows the new home's real walls, its rooms labelled, every device the user wants placed in the right room, `tools/smoke.py` reports `errors: none`, and the user has seen it in their browser and said it looks right.

`plans/example/` is the reference: when unsure how something is done, read how the example did it, and the scripts in `tools/history/` that built it. Its PDF is not included; its traced `build/*.json` shows what good output looks like.

## 1. Collect the inputs

Ask the user (plain words, one message):

- the drawings PDF: tell them to drag the file into this terminal window and press Enter, which pastes its path;
- a short name for the folder (suggest one from the customer or unit, e.g. `tan-condo-b12`) and the label to show on the page;
- which devices the home gets. Offer the example's kit as the starting point (Aqara M200 hub, H1 switches, H2 outlets, curtain motors, LED drivers, presence sensors, IR remotes for aircons, ASUS Wi-Fi mesh) and ask what to add, drop or swap.

## 2. Check the PDF

`uv run tools/pdf_info.py <pdf> /tmp/<name>-pages` (any temp folder), then look at each `page-N.png`. Tracing needs a **vector** CAD export. If the pages are images, stop and tell the user: "This drawing is a picture, so I can't trace the walls exactly. Please ask the architect or ID for the PDF exported from their drawing software (AutoCAD/ArchiCAD/SketchUp)." Identify which page is which sheet: furniture layout, M&E (electrical points), RCP (reflected ceiling: lights and switching).

## 3. Create the folder

`uv run tools/new_plan.py <name> --pdf <pdf> --code <LABEL>`. It copies the PDF to `source/plan.pdf` and the example's `src/` as the starting page. Move the page previews into `plans/<name>/renders/`.

## 4. Trace the walls

The shared scripts hold constants tuned to the example's PDF. Copy `tools/geometry.py` (and `tools/rcp_extract.py` when the home has an RCP sheet) into `plans/<name>/scripts/` and tune the copy, keeping the shared ones unchanged:

- the page index of the M&E/RCP sheet;
- `CLIP`/`BOX`: the rectangle around the apartment, in PDF points (read it off the page preview: PNG pixels x 72 / 110);
- the colour filters for walls, outlines and furniture: list the stroke and fill colours the new PDF uses with `uv run tools/extract.py <pdf>` (coloured text and switch dots on sheets 2-3) and `uv run tools/history/classify.py <pdf> <out_dir>` (drawings grouped by colour); adapt either to the new sheet order;
- `mmPerPt`: from one dimension printed on the drawing (mm length / its length in points), or from the scale (1:50 on A3 gives 17.639 mm per pt; 1:100 gives 35.278).

Write `plans/<name>/build/geometry.json` (and `build/rcp.json`), render with `uv run tools/preview.py <geometry.json> <out.svg>` and `uv run tools/shot.py <out.svg> <out.png>`, and compare against the page preview until the walls, doors and windows match. No RCP sheet: write `{"fixtures": {}, "chains": [], "labels": []}` to `build/rcp.json` and check the switch-circuits view still loads.

## 5. Rewrite the page for this home

In `plans/<name>/src/template.html`, replace every example-specific value. Account for each of these:

- text: `<title>`, the `.meta` paragraph under the heading, `#planTitle`, the "Floor plan:" source note, and the view titles built from `Example · ...`;
- the storage prefix `"example:"` in `store` and `KEY` in `src/led-section.html` (give each plan its own, so two plans opened in one browser keep separate saved positions);
- scale and frame: `MM_PER_PT`, `VB_FULL`, `APARTMENT` (outline polygon), `CLOSED_DOORS`, `KEEP_OUT`;
- rooms: `ROOMS`, `EXTRA_LABELS`, the wet-room list `WET`;
- devices: everything added to `D` (the `add(...)`, `H1(...)` and similar calls), `UNPLACED`, `RCP_OTHER`, the `FORCED` position list, and the hub/sensor ids used by the best-spot and IR checks (`IR_PAIRS`, the `m200` references);
- LED and switching: `LED_FEATURES`, `LED_MAP`, `LED_RUNS`, `KEEP`, `PLAIN_SWITCHES`, `WATER_HEATERS`, `SW_PLACE`, `PLAIN_NAMES`, `AREA`, `ORDER_SPOT`, and `src/led-section.html`;
- the review text (open items, sources) that talks about the example owner's decisions.

Keep `window.__plan` and `window.planLed` as the names of the page's script API: `tools/export.py` and the checks call it.

## 6. Build and look

`uv run tools/build.py plans/<name>` and `uv run tools/smoke.py plans/<name>`, then screenshots at desktop width and phone width (`uv run tools/shot.py plans/<name>/index.html <png> 1440` and `... 390`). Read the screenshots: labels must not overlap devices or each other, every device sits inside its room, and nothing spills off the page on the phone. Fix and repeat until clean.

## 7. Show the user

Open `plans/<name>/index.html` in their browser. Ask them to check rooms and device spots, and explain how to move a device: drag it, then click the SVG download button and give you the file (see `CLAUDE.md`, "Changes the user makes on the page"). Apply their changes, rebuild, run `uv run tools/export.py plans/<name>` for the PNG/SVG exports, and commit: `git add -A`, `git commit -m "<name>: first plan"`.

Then offer to publish it (the `publish-plan` skill).
