#!/usr/bin/env python3
"""Build the Bourbon and Hapsburg special page.

Datasets live in datasets/bourbon-hapsburg/ (own manifest). The output
is a single portable file, dist/bourbon-hapsburg.html, deployed at the
repo root next to index.html.

Three template adjustments, all asserted so a template change is caught
instead of silently shipping a broken page:
  - <title> becomes "Bourbon and Hapsburg".
  - The boot default selection ([...BACKGROUND_IDS], which does not exist
    in this build) becomes the three special dataset ids, so the page opens
    on all three datasets.
  - BACKGROUND_IDS becomes ['world-history']: the general European/world
    dataset is the background timeline, and the two dynasties are the
    foregrounds. With two foregrounds the page renders one merged timeline
    (not three columns) and opens on the foregrounds' combined span.
    This is viewer-side composition only; no dataset file carries a
    background flag.
"""
import json, pathlib

root = pathlib.Path(__file__).parent
subdir = root / "datasets" / "bourbon-hapsburg"
manifest = json.loads((subdir / "manifest.json").read_text())
ids = [item["id"] for item in manifest]
sets = {}
for item in manifest:
    sets[item["id"]] = json.loads((subdir / item["file"]).read_text())

html = (root / "index.html").read_text()
assert "<title>Deep Time</title>" in html
html = html.replace("<title>Deep Time</title>", "<title>Bourbon and Hapsburg</title>", 1)
ids_literal = "[" + ",".join("'" + i + "'" for i in ids) + "]"
n = html.count("[...BACKGROUND_IDS]")
assert n == 2, f"expected 2 boot-default sites, found {n}"
html = html.replace("[...BACKGROUND_IDS]", ids_literal)
bg_const = "const BACKGROUND_IDS=['earth-history','human-history','powers-of-10'];"
assert html.count(bg_const) == 1, "background const not found exactly once"
html = html.replace(bg_const, "const BACKGROUND_IDS=['world-history'];", 1)

payload = {"manifest": manifest, "sets": sets}
tag = '<script>window.__DATASETS__=' + json.dumps(payload, separators=(",", ":")) + ";</script>"
marker = "<!--__DATASETS__-->"
assert marker in html, "marker missing in index.html"
out = html.replace(marker, tag, 1)
dist = root / "dist"
dist.mkdir(exist_ok=True)
(dst := dist / "bourbon-hapsburg.html").write_text(out)
print("wrote", dst, len(out), "bytes")
