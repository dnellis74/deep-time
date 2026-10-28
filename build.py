#!/usr/bin/env python3
"""Build index.html from src/index.html + datasets/ (single portable file).

Usage: python3 build.py  (from the repo root)
Reads src/index.html (the template, carrying a <!--__DATASETS__--> marker),
inlines datasets/manifest.json and every dataset it lists, and writes
index.html: the self-contained file the site serves and anyone can open
directly, with no server. Re-running it reproduces index.html
byte-identically from the checked-in sources. Validate first with:
    python3 validate_datasets.py datasets/*.json
"""
import json
import pathlib

root = pathlib.Path(__file__).parent
html = (root / "src" / "index.html").read_text()
manifest = json.loads((root / "datasets" / "manifest.json").read_text())
sets = {}
for item in manifest:
    sets[item["id"]] = json.loads((root / "datasets" / item["file"]).read_text())
payload = {"manifest": manifest, "sets": sets}
tag = '<script>window.__DATASETS__=' + json.dumps(payload, separators=(",", ":")) + ";</script>"
marker = "<!--__DATASETS__-->"
assert marker in html, "marker missing in src/index.html"
out = html.replace(marker, tag, 1)
(root / "index.html").write_text(out)
print("wrote", root / "index.html", len(out.encode()), "bytes")
