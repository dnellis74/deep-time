# Datasets for Deep Time

This folder holds the source datasets for
[Deep Time](../README.md), one JSON file per dataset, plus
`manifest.json`, the registry the app loads them from. Each manifest
entry is `{"file", "id", "title"}`. The built `index.html` in the repo
root inlines these files, so it opens anywhere with no server.

Current datasets: `earth-history.json`, `human-history.json`,
`demo.json` (Powers of 10: Universe), `jewish-history.json`,
`levant-neutral.json` (The Southern Levant: Shared Timeline),
`palestinian-history.json`.

The rest of this file is two things: the JSON format spec, and a
paste-ready prompt for generating a new dataset with an LLM.

## JSON format spec

One JSON object per dataset. Time is years relative to 2026: a CE year
Y becomes `t = Y - 2026`, so 1938 is -88 and the present is 0. Dates
render as "88 yr ago" when `timeFormat` is `"ago"`.

### Top-level fields

| Field | Meaning |
| --- | --- |
| `id` | Unique within the app, lowercase-hyphenated (e.g. `jewish-history`). |
| `title` | Display title. |
| `unit` | Almost always `"years"`. |
| `timeFormat` | `"ago"` for dates rendered as years ago. |
| `start`, `end` | The dataset's time range in `t` units. `end` is 0 for datasets reaching the present. |
| `minSpan`, `maxSpan` | The smallest and largest zoom spans allowed, in years. |
| `events` | Array of events (below). |
| `connections` | Array of connections (below). May be empty. |
| `presets` | Array of jump presets (below). |
| `defaultPreset` | Optional: the id of the preset used as the default view when the app opens without deep-link coordinates. Deep links still override it; datasets without it default to the full span. |

### Events

| Field | Meaning |
| --- | --- |
| `id` | Unique within the dataset, lowercase-hyphenated. The same id in two datasets does not collide. |
| `label` | Short display label. |
| `t` | Time in `t` units, within `[start, end]`. |
| `tEnd` | Optional: for something spanning years (a career, a movement's active run). Must satisfy `t < tEnd <= end`. Renders as a span bar. |
| `tier` | Integer. See tier calibration below. |
| `importance` | 0-100. Higher wins label collisions, and drives auto-promotion (below). See granularity below. |
| `blurb` | One sentence, shown when the reader taps the event. |
| `connections` | Optional inline arcs (below). |

### Tier calibration

A label is eligible for display only when the visible span's decade
`round(log10(span))` is at or below the label's tier. Concretely: at a
10,000-year view (decade 4) only tier 4 and higher labels appear; at a
1,000-year view (decade 3) tier 3 and higher appear; at a 10-year view
(decade 1) tier 1 and higher appear; at a few-year view (decade 0)
everything appears.

Calibrate so every zoom level has anchor labels, but no level is
crowded. As a starting guide: tier 4 for a handful of era-defining
anchors visible at the full span; tier 3 for field-wide eras; tier 2
for landmark works and major figures; tier 1 for important
publications and events; tier 0 for fine detail. Marquee events may
sit one tier above their section so every zoom level has anchors.
Check each preset window: it must hold at least 2 visible labels at
its span, or the validator rejects it.

### Importance and granularity

`importance` is 0-100. It breaks label collisions (higher wins) and
drives auto-promotion: when tier gating leaves a dataset with fewer
than 4 visible events in view, the highest-importance in-view events
fill the gap regardless of tier, so sparse eras still show a few major
events. For that ranking to mean anything, values must be granular:
no two events within one era window (dataset span / 15) should share
a value where the scale allows. The validator warns on same-window
ties. Do not bucket everything into 40/50/60: spread values so the
ranking reflects judgment, keeping the most important events highest.

### Connections

Everything relational lives in `connections`. Each connection has a
`form` (how it renders, presentation) and a `kind` (what it means).
`form` is one of:

- `region`: a one-to-many era tint spanning a time range. Fields: `id`,
  `label`, `tStart`, `tEnd`, `tier`, `color` (hex). Membership is
  derived from time, not listed: events in the span belong to it.
  Tapping a region label zooms to fit it. Region labels render when
  the region's pixel height is at least 28px and its tier is eligible.
- `band`: a one-to-many stream whose width encodes a defined
  quantity: member count, summed importance, or an explicit numeric
  field on the connection. Width never encodes an undefined
  impression; if the quantity is not defined, the width stays
  constant. Same fields as a region.
- `arc`: a 1-1 link between two events. Fields: `from`, `to`,
  optional `kind`, optional `note` (one sentence on why the
  connection holds).

`kind` is the meaning, suggested set: `influences`, `extends`,
`challenges`. Direction is derived from time: the earlier event is
the source, the later is the target. Same-year pairs are directionless.
Inline connections (inside an event's `connections` array) are always
arcs: a plain string is an arc to that event id with kind defaulting
to `influences`; an object `{"id", "kind", "note"}` sets kind and note.
Connections are direct only: if A connects to B and B to C, do not add
A to C unless the direct connection is documented. Both endpoints must
exist, no self connections, no duplicates. Connections stay
within-dataset; cross-dataset arcs are not defined.

### Presets

Each preset is `{"id", "label", "c", "s"}`: `c` is the center time,
`s` is the span in years. The window `[c - s/2, c + s/2]` must lie
within `[start, end]`, satisfy `minSpan <= s <= maxSpan`, and hold at
least 2 visible labels at that span (count tier-eligible labels in
the window). The field is `presets`; the name `views` is reserved
for a separate visualization layer and must not be used here.

### Minimal example

```json
{
  "id": "history-of-writing",
  "title": "History of Writing",
  "unit": "years",
  "timeFormat": "ago",
  "start": -5200,
  "end": 0,
  "minSpan": 1,
  "maxSpan": 6000,
  "connections": [
    {"id": "bronze-age", "label": "Bronze Age", "form": "region",
     "tStart": -3200, "tEnd": -1100, "tier": 3, "color": "#3a2b28"}
  ],
  "events": [
    {"id": "cuneiform", "label": "Cuneiform in Sumer", "t": -5200,
     "tier": 3, "importance": 88,
     "blurb": "Wedge-shaped marks pressed into clay become the first writing system."},
    {"id": "printing-press", "label": "Gutenberg's press", "t": -586,
     "tier": 2, "importance": 90,
     "blurb": "Movable type makes books cheap enough to change who reads.",
     "connections": ["cuneiform"]}
  ],
  "presets": [
    {"id": "all", "label": "All", "c": -2600, "s": 5200},
    {"id": "modern", "label": "Modern", "c": -250, "s": 500}
  ],
  "defaultPreset": "all"
}
```

## Validate

From the repo root:

```sh
python3 validate_datasets.py datasets/your-dataset.json
```

Zero errors is required. Address warnings too: missing blurbs, and
same-window importance ties (see granularity above).

## Prompt: generate a dataset

Paste the following into an LLM, replacing `[TOPIC]` and adjusting
the scope lines to fit. It assumes the model has already discussed
the topic with you; if it has not, replace "our conversation" with
the sources it should use.

```text
Create a dataset for Deep Time, an infinitely zoomable timeline app,
about [TOPIC]. Output the dataset as JSON following the spec below
exactly. Use the simple one-file format: events and connections with
inline display hints (tier, importance, color, form). Do not invent a
separate views layer.

Scope: aim for 30-80 events, 4-8 region connections, and 4-6 presets,
adjusted to the topic. Cover the whole arc of [TOPIC], not just its
famous half. Every era should have at least one event, and every
preset window must hold at least 2 visible labels (see tier rule).

Time: years relative to 2026. A CE year Y becomes t = Y - 2026, so
1938 is -88 and the present is 0. Dates before 2026 are negative.
Set start to the earliest event's era (rounded outward) and end to 0
if the topic reaches the present. Spanning things (a career, a
movement's active run) get tEnd with t < tEnd <= end; point events
have no tEnd.

Fields per event: id (unique in the dataset, lowercase-hyphenated),
label (short), t, optional tEnd, tier (integer), importance (0-100),
blurb (one sentence), optional connections (inline arcs, below).
Top-level fields: id, title, unit ("years"), timeFormat ("ago"),
start, end, minSpan (1), maxSpan (at least the dataset span),
events, connections, presets, optional defaultPreset (a preset id).

Tier rule (this decides what shows at each zoom): a label is
eligible only when the visible span's decade round(log10(span)) is
at or below the label's tier. So tier 4 labels appear at 10,000-year
views, tier 3 at 1,000-year views, tier 2 at 100-year views, tier 1
at 10-year views, tier 0 only at few-year views. Calibrate so every
zoom level has a few anchors: a handful of tier 4 era-defining
events for the full span, tier 3 for field-wide eras, tier 2 for
landmark works and major figures, tier 1 for important events,
tier 0 for fine detail. Marquee events may sit one tier above their
section.

Importance rule: 0-100, higher wins label collisions, and sparse
views auto-fill to 4 events per dataset with the highest-importance
in-view events. Values must be granular: do not bucket everything
into 40/50/60. Spread values so the ranking reflects judgment, and
do not give two events within the same era (dataset span / 15)
the same value where the scale allows.

Connections: one connections array. form is presentation, kind is
meaning (influences, extends, challenges). Regions are one-to-many
era tints: id, label, form "region", tStart, tEnd, tier, color
(hex). Membership is derived from time, not listed. Arcs are 1-1
links: inline as a string (kind defaults to influences) or an
object with kind and note, or dataset-level with from/to/form
"arc"/kind/note. Direction comes from time (earlier influences
later); same-year pairs are directionless. Connections are direct
only, endpoints must exist, no self connections, no duplicates.

Presets: each is id, label, c (center time), s (span in years).
Every preset window must lie within [start, end], satisfy
minSpan <= s <= maxSpan, and hold at least 2 visible labels at
that span. Include an "all" preset covering the full span, and
set defaultPreset to it unless a narrower default fits better.

Output: the JSON in a single code block first, then a short Notes
section listing anything added from general knowledge rather than
our conversation, any uncertain dates, and any spec checks that
failed. Self-check before answering: ids unique and hyphenated,
all times in [start, end], tEnd > t, tiers integers, presets hold
at least 2 visible labels, no two events in one era sharing an
importance value.
```

## Adding the dataset to the app

Add the JSON file to this folder, add its `{"file", "id",
"title"}` entry to `manifest.json`, validate it (0 errors), and
the built `index.html` is regenerated from `datasets/` when the
dataset lands.
