#!/usr/bin/env python3
"""Build the Bourbon and Habsburg special page.

Datasets live in datasets/bourbon-habsburg/ (own manifest). The output
is a single portable file, dist/bourbon-habsburg.html, deployed at the
repo root next to index.html.

Two template adjustments, both asserted so a template change is caught
instead of silently shipping a broken page:
  - <title> becomes "Bourbon and Habsburg".
  - The boot default selection ([...BACKGROUND_IDS], which does not exist
    in this build) becomes the three special dataset ids, so the page opens
    on all three datasets. The BACKGROUND_IDS machinery itself is untouched:
    with no background dataset selected, all three count as foregrounds,
    so the page opens on their combined span and renders columns when
    three or more are selected.
"""
import json, pathlib

root = pathlib.Path(__file__).parent
subdir = root / "datasets" / "bourbon-habsburg"
manifest = json.loads((subdir / "manifest.json").read_text())
ids = [item["id"] for item in manifest]
sets = {}
for item in manifest:
    sets[item["id"]] = json.loads((subdir / item["file"]).read_text())

html = (root / "index.html").read_text()
assert "<title>Deep Time</title>" in html
html = html.replace("<title>Deep Time</title>", "<title>Bourbon and Habsburg</title>", 1)
ids_literal = "[" + ",".join("'" + i + "'" for i in ids) + "]"
n = html.count("[...BACKGROUND_IDS]")
assert n == 2, f"expected 2 boot-default sites, found {n}"
html = html.replace("[...BACKGROUND_IDS]", ids_literal)

payload = {"manifest": manifest, "sets": sets}
tag = '<script>window.__DATASETS__=' + json.dumps(payload, separators=(",", ":")) + ";</script>"
marker = "<!--__DATASETS__-->"
assert marker in html, "marker missing in index.html"
out = html.replace(marker, tag, 1)
dist = root / "dist"
dist.mkdir(exist_ok=True)
(dst := dist / "bourbon-habsburg.html").write_text(out)
print("wrote", dst, len(out), "bytes")
