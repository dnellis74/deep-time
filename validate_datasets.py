#!/usr/bin/env python3
"""Validate Deep Time dataset JSON files against dataset-format.md rules.

Usage: python3 validate_datasets.py <file.json> [...]
Checks (errors fail, warnings are reported but pass):
  - required top-level fields and sane ranges
  - event ids unique within the dataset, lowercase hyphenated
  - event times within [start, end], tEnd > t when present
  - tier integers, importance within 0-100
  - importance granularity (warning): two events within one era window
    (dataset span / 15, same window as rescore_importance.py) sharing an
    importance value make auto-promotion's picks arbitrary
  - region/band connections: id, label, tStart < tEnd, in range, tier, color
  - arc endpoints exist, no self-connections, no exact duplicates
  - inline connections reference existing events in the same dataset
  - presets: window within [start, end], minSpan <= s <= maxSpan,
    at least 2 labels visible at that span (tier >= round(log10(s)))
  - defaultPreset, when present, references an existing preset
Exit code 0 when no errors, 1 otherwise.
"""
import json
import math
import re
import sys

ID_RE = re.compile(r"^[a-z0-9-]+$")
KINDS = {"influences", "extends", "challenges"}


def js_round(x):
    return math.floor(x + 0.5)


def visible_labels(ds, c, s):
    dec = js_round(math.log10(s))
    lo, hi = c - s / 2, c + s / 2
    n = 0
    for e in ds.get("events", []):
        t1 = e["tEnd"] if e.get("tEnd") is not None else e["t"]
        if e.get("tier", 0) >= dec and t1 >= lo and e["t"] <= hi:
            n += 1
    for r in ds.get("connections", []):
        if r.get("form") == "region" and r.get("tier", 0) >= dec \
                and r["tEnd"] > lo and r["tStart"] < hi:
            n += 1
    return n


def validate(path):
    errors, warnings = [], []
    with open(path) as f:
        ds = json.load(f)
    if not isinstance(ds, dict):
        print(f"== {path}: skipped (not a dataset object)")
        return [], []
    name = ds.get("id", path)
    for field in ("id", "title", "unit", "timeFormat", "start", "end",
                  "minSpan", "maxSpan", "events"):
        if field not in ds:
            errors.append(f"missing top-level field {field!r}")
    if errors:
        return errors, warnings
    start, end = ds["start"], ds["end"]
    if not start < end:
        errors.append(f"start {start} not < end {end}")
    if ds["minSpan"] > ds["maxSpan"]:
        errors.append("minSpan > maxSpan")

    event_ids = {}
    for i, e in enumerate(ds["events"]):
        tag = f"event[{i}]"
        if "id" not in e or "label" not in e or "t" not in e:
            errors.append(f"{tag} missing id/label/t")
            continue
        eid = e["id"]
        if not ID_RE.match(eid):
            errors.append(f"{tag} id {eid!r} not lowercase-hyphenated")
        if eid in event_ids:
            errors.append(f"duplicate event id {eid!r}")
        event_ids[eid] = e
        if not (start <= e["t"] <= end):
            errors.append(f"event {eid!r} t={e['t']} outside [{start},{end}]")
        if e.get("tEnd") is not None:
            if not (e["t"] < e["tEnd"] <= end):
                errors.append(f"event {eid!r} bad tEnd={e['tEnd']}")
        if not isinstance(e.get("tier"), int):
            errors.append(f"event {eid!r} tier not an integer")
        if "importance" in e and not (0 <= e["importance"] <= 100):
            errors.append(f"event {eid!r} importance out of 0-100")
        if "blurb" not in e:
            warnings.append(f"event {eid!r} has no blurb")
        for conn in e.get("connections", []):
            if isinstance(conn, str):
                cid, kind = conn, "influences"
            else:
                cid, kind = conn.get("id"), conn.get("kind", "influences")
            if cid == eid:
                errors.append(f"event {eid!r} connects to itself")
            if cid not in event_ids and cid not in [x["id"] for x in ds["events"]]:
                errors.append(f"event {eid!r} inline connection to unknown {cid!r}")
            if kind not in KINDS:
                errors.append(f"event {eid!r} unknown kind {kind!r}")
        if e.get("connections") and len(set(
                c if isinstance(c, str) else c.get("id") for c in e["connections"]
        )) != len(e["connections"]):
            errors.append(f"event {eid!r} has duplicate inline connections")

    # importance granularity (warning only): auto-promotion ranks by
    # importance, so ties within one era window make its picks arbitrary.
    # Window matches rescore_importance.py: dataset span / 15.
    W = (end - start) / 15.0
    tie_pairs = []
    evs = ds["events"]
    for i, a in enumerate(evs):
        for b in evs[i + 1:]:
            if "t" in a and "t" in b and "importance" in a and "importance" in b \
                    and a["importance"] == b["importance"] \
                    and abs(a["t"] - b["t"]) <= W:
                tie_pairs.append((a.get("id", "?"), b.get("id", "?")))
    for a, b in tie_pairs[:5]:
        warnings.append(f"same-window importance tie: {a!r} and {b!r}")
    if len(tie_pairs) > 5:
        warnings.append(f"... and {len(tie_pairs) - 5} more same-window importance ties")

    conn_ids = set()
    seen_arcs = set()
    for i, c in enumerate(ds.get("connections", [])):
        tag = f"connection[{i}]"
        form = c.get("form")
        if form in ("region", "band"):
            for field in ("id", "label", "tStart", "tEnd", "tier", "color"):
                if field not in c:
                    errors.append(f"{tag} region/band missing {field!r}")
            if "id" in c:
                if c["id"] in event_ids or c["id"] in conn_ids:
                    errors.append(f"connection id {c['id']!r} collides")
                conn_ids.add(c["id"])
                if not ID_RE.match(c["id"]):
                    errors.append(f"connection id {c['id']!r} not lowercase-hyphenated")
            if "tStart" in c and "tEnd" in c:
                if not (c["tStart"] < c["tEnd"]):
                    errors.append(f"{tag} tStart >= tEnd")
                if not (start <= c["tStart"] and c["tEnd"] <= end):
                    errors.append(f"{tag} span outside [{start},{end}]")
            if not isinstance(c.get("tier"), int):
                errors.append(f"{tag} tier not an integer")
        elif form == "arc":
            a, b = c.get("from"), c.get("to")
            if a not in event_ids or b not in event_ids:
                errors.append(f"{tag} arc endpoint missing ({a!r} -> {b!r})")
            if a == b:
                errors.append(f"{tag} arc connects an event to itself")
            key = (a, b, c.get("kind", "influences"))
            if key in seen_arcs:
                errors.append(f"{tag} duplicate arc {key}")
            seen_arcs.add(key)
            if c.get("kind") and c["kind"] not in KINDS:
                errors.append(f"{tag} unknown kind {c['kind']!r}")
        elif form is not None:
            errors.append(f"{tag} unknown form {form!r}")

    preset_ids = set()
    for p in ds.get("presets", []):
        for field in ("id", "label", "c", "s"):
            if field not in p:
                errors.append(f"preset missing {field!r}: {p}")
        if p["id"] in preset_ids:
            errors.append(f"duplicate preset id {p['id']!r}")
        preset_ids.add(p["id"])
        lo, hi = p["c"] - p["s"] / 2, p["c"] + p["s"] / 2
        if not (start <= lo and hi <= end):
            errors.append(f"preset {p['id']!r} window [{lo},{hi}] outside [{start},{end}]")
        if not (ds["minSpan"] <= p["s"] <= ds["maxSpan"]):
            errors.append(f"preset {p['id']!r} span {p['s']} outside [minSpan,maxSpan]")
        n = visible_labels(ds, p["c"], p["s"])
        if n < 2:
            errors.append(f"preset {p['id']!r} window has only {n} visible label(s), need >= 2")
    if ds.get("defaultPreset") and ds["defaultPreset"] not in preset_ids:
        errors.append(f"defaultPreset {ds['defaultPreset']!r} is not a preset id")

    print(f"== {name}: {len(ds['events'])} events, "
          f"{len(ds.get('connections', []))} connections, "
          f"{len(ds.get('presets', []))} presets, "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    for e in errors:
        print(f"  ERROR: {e}")
    for w in warnings[:20]:
        print(f"  warn: {w}")
    if len(warnings) > 20:
        print(f"  ... and {len(warnings) - 20} more warnings")
    return errors, warnings


def main():
    all_errors = 0
    for path in sys.argv[1:]:
        errors, _ = validate(path)
        all_errors += len(errors)
    print("VALIDATION " + ("PASSED" if all_errors == 0 else f"FAILED ({all_errors} errors)"))
    return 0 if all_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
