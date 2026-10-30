# Zoomable Timeline - Software Spec v0.18

Date: 2026-10-18, revised 2026-10-26
Status: Approved and building. v0.2 adds tap-to-zoom bands and jump presets (section 5, 7, 8). v0.3 changes tier gating to the snapped decade (section 5). v0.5 migrates to the connections model: bands become region-form connections, views become presets, data and visualization split into layers (dataset-format.md is the dataset authoring format). v0.6 adds a dynamic bottom inset (present stays above the tray) and a Present preset. v0.7 moves the scale chip to the top-right on phones. v0.8 adds a floating Present button, 10px inset clearance, desktop chip right, and pull-to-refresh suppression. v0.9 moves the Present button to the right column above the zoom buttons. v0.10 sizes the phone tray for thumbs: 56px handle, 44px-plus touch targets. v0.11 sets touch-action: manipulation on tray tap targets for reliable mobile taps. v0.12 anchors the stage to the visual viewport (100dvh) so the closed tray handle is never hidden under the mobile URL bar. v0.13 reverts the 100dvh stage (it blanked the page on-device) and lifts the tray by safe-area plus 56px so the closed handle clears the mobile URL bar zone. v0.14 measures the mobile URL bar zone (layout minus visual viewport) and lifts the tray by exactly that plus safe-area, so the closed handle is fully visible. v0.15 sizes the stage to the measured visual height in JavaScript so the tray anchors to the visible bottom in any viewer, and the tray lift covers only the gesture bar. v0.16 replaces the dynamic inset with a standard overlay tray: the tray slides over the timeline and never resizes it, and the canvas reserves a constant 66px (plus gesture bar) for the closed handle. v0.17 makes the default view the dataset's defaultPreset (earth-history: Civilization); deep links still override, Reset still goes to full span. v0.18 adds dataset multiselect: several datasets render together on one shared axis, with toggle chips in the tray and comma-separated deep links. v0.19 adds columns mode: three or more selected datasets render as one column each, each with its own spine, dots, labels, span lanes, and region tint; single and two-dataset layouts are unchanged. v0.20 adds auto-promotion: when tier gating leaves a dataset with fewer than 4 visible events in view, the highest-importance in-view events fill the gap regardless of tier; importance values are rescored for finer granularity (near-original values, max shift 10). v0.21 splits earth-history into two datasets at the Pliocene/Pleistocene boundary (2.6M years ago, Oldowan tools): earth-history ends there with geologic regions only (30 regions, Primates preset, full-span default), and human-history covers 2.6M years ago to present (79 events, 20 regions, 10 presets, default All) structured by Wikipedia's general periods (Prehistory, Ancient history, Post-classical, Modern, with sub-periods); moved events keep tiers, importance, and blurbs, and human importance was rescored for its own era window (32 to 58 distinct values, 51 tie pairs remain in the dense civilization cluster). v0.22 adds merged mode: a Merge toggle in the tray (shown when two or more datasets are selected) draws all selected datasets in one single column, using single-mode geometry (central spine, chronological label sides, shared label pool, full-width regions painted globally broadest span first); dots and labels take their dataset's accent color, and tray chips carry the same accent as a border, so the reader can tell datasets apart in one column. Merge is opt-in and the default stays columns, because automatic geometry would also merge datasets whose ranges nest but are meant to be compared (Jewish [-6000,0] sits inside Palestinian [-15000,0]); datasets carry no composition data, so every dataset stays reusable and the merge decision lives in the viewer code, not in the data. v0.22 is superseded before publishing and never shipped: the Merge toggle is removed in v0.23. v0.23 defines background layers: universe, earth, and human history are designated as background layers in the viewer code (BACKGROUND_IDS), not in the dataset files; if the selection includes background datasets and at most one other dataset, everything merges into one single column (single-mode geometry, dataset accents, regions painted globally broadest first); if it includes background datasets and two or more others, the view is columns of the other datasets only and the background is hidden; selections with no background datasets work exactly as before (single, two-dataset, and columns modes unchanged); the app opens on the background trio when no deep link is given. v0.24 fixes the scale chip contradiction: the headline now states the actual visible span (e.g. ~13.8 billion years visible) and the snapped decade moves to the sub-line as a zoom scale (zoom 10^10), since the old headline understated full-span views. v0.25 puts a background column in column mode, replacing v0.23's hidden-background rule: when two or more non-background datasets are shown in columns, the view adds the smallest background dataset whose range contains all of them (e.g. Palestinian plus Jewish histories get Human History as the background column); if no background contains them, no background column is added. Column mode opens on the compared timelines' combined span (and Reset returns there), while panning and zooming still roam the full visible range including the background. v0.26 corrects the foreground/background model and replaces v0.25's derived-background column (never shipped): one or two foreground timelines merge into one single timeline, with the foreground integrated into the background and events from both drawn on one axis; three or more foreground timelines render as columns of the foregrounds only, with no background rendered. Two or more foreground timelines open on the foregrounds' combined span. v0.27 adds the first Connections dataset: The Trigger Effect (Connections S1E1), 12 events built from the episode transcript, from the drying that drove people to the Nile (c. 10,000 B.C.) through the plow, writing, the Step Pyramid, and Karnak to the 1965 Northeast blackout and Kuwait's oil transformation, with the chain encoded as inline arc connections (arcs do not render yet). v0.28 adds the second Connections dataset: The Long Chain (Connections S1E7), 22 events from the episode transcript, from the fluyt of 1595 through Lloyd's, coal tar, gaslight, mauve, Haber-Bosch, and the 1914 explosives crisis to nylon in 1938, spanning about 380 years. v0.29 adds `showAllEvents` (dataset flag, default false): flagged datasets skip tier gating, so every in-view event renders a dot at every zoom level; label collision declutter still applies. Both Connections datasets carry the flag. v0.30 adds the Star Wars dataset (14 events) to the main app: the saga is mapped onto the timeline before Earth's formation, with the Battle of Yavin placed 1,000 years before Earth forms and one BBY/ABY year equal to one timeline year, so the whole saga, 36,453 BBY to 35 ABY, sits strictly before Earth-history's start.

## 1. Product goal

A data-driven, vertically scrolling timeline that zooms from the full span of a dataset down to its finest events. Phone-first; responsive on desktop browsers.

v1 dataset: history of Earth, 4.54 Ga to present. Coarsest level: geologic eons. Finest level: human tool eras (Paleolithic, Neolithic, Bronze, Iron, Industrial).

Out of scope for v1:

- The general label-hierarchy engine (flagged as a future problem; v1 gets a simple tier system designed to be replaced)
- User dataset upload UI
- Any backend or server component
- Native apps

## 2. Agreed design decisions

- Vertical layout. Top is earliest, bottom is latest (present).
- Continuous exponential zoom (Eames-style): pinch, wheel, and buttons multiply/divide the visible span. Scale readout snaps to powers of 10.
- The engine is dataset-agnostic. Datasets are static JSON files; the tray picks between them.
- Declutter v1: decade tier gating plus importance-ranked greedy collision. Full hierarchy rules come later. v0.20 auto-promotion: when tier gating leaves a dataset with fewer than 4 visible events in view, the highest-importance in-view events fill the gap regardless of tier; promotion is eligibility only, declutter still decides which visible events get labels, and busy views are untouched.
- No dependencies, no build step: one `index.html` plus `datasets/*.json`. Rendering on `<canvas>`.
- Default view: when the app opens without deep-link coordinates, it shows the dataset's `defaultPreset` if one is declared (earth-history: Civilization, last 12,000 years); otherwise the full span. Deep links still override; Reset still goes to the full span.
- Multiselect: the tray dataset picker is toggle chips, not single-select. Selected datasets render together on one shared time axis. One or two foreground (non-background) datasets merge into one single column, with events from each drawn on one axis in its accent color. Three or more foreground datasets render as columns of the foregrounds only, each with its own spine, dots, labels, span lanes, and region tint, and tray chips are tagged with the column number; nothing from one dataset can sit on another's, and no background dataset is rendered (v0.26). Preset chips are the union across selected datasets, tagged with the dataset id. Deep links take a comma-separated dataset list (`?d=a,b`); old single `?d=` links keep working. Opening several datasets with no coordinates shows the foregrounds' combined span when two or more foreground datasets are selected, otherwise the combined full span; Reset returns there too. Connections stay within-dataset; cross-dataset arcs are not defined yet.

## 3. Time model

- The engine works on a plain float64 number line in dataset-declared units. It does not care what the numbers mean.
- Each dataset declares: `unit` ("years", "seconds", ...), `start`, `end`, and `timeFormat` ("ago" or "absolute").
- Earth dataset: years before present expressed as negative numbers. `start: -4540000000`, `end: 0`, `timeFormat: "ago"`.
- Display formatter: magnitude >= 1e9 renders as Ga, >= 1e6 as Ma, >= 1e3 as ka, else plain years, 2-3 significant figures. With `timeFormat: "ago"`, appends "ago" (e.g. -4540000000 renders as "4.54 Ga ago").
- Precision note: float64 is sufficient because each dataset picks an epoch near its own range. A future universe-scale dataset would use seconds-since-origin. There is no global absolute timeline in v1.

## 4. Zoom and viewport model

- Viewport is defined by center time `C` and visible span `S` (in dataset units). Pixel mapping uses the visible drawing height `Hv = H` minus the bottom inset (visible tray height plus 10px on phones, 0 on desktop): `y(t) = Hv * (t - (C - S/2)) / S`. The inset is recomputed when the tray opens or closes and on resize; the zoom column (Present button plus +/- buttons) lifts to sit above the inset, so present renders above the tray at every zoom.
- `S` is clamped to `[minSpan, maxSpan]` from the dataset. Earth: `minSpan: 10` (years), `maxSpan: 10000000000`.
- Pinch zooms about the gesture midpoint, keeping the time under the midpoint fixed. Wheel zooms about the cursor. Buttons and double-tap step exactly one decade (S x10 or /10); double-tap centers on the tap point.
- `C` is clamped so the viewport stays inside `[start, end]`. If `S >= end - start`, `C` is pinned to the range midpoint.
- Scale readout (fixed chip, top-right: 12px from the right on phones, 58px on desktop, 312px with the desktop tray open): v0.24 headline is the human form of the actual span (e.g. "~13.8 billion years visible"), sub-line is the zoom scale `zoom 10^n` where `n = round(log10(S))`. The decade is a zoom scale, not a year count, so it no longer headlines as years visible.

## 5. Data schema

Dataset JSON:

```json
{
  "id": "earth-history",
  "title": "History of Earth",
  "unit": "years",
  "timeFormat": "ago",
  "start": -4540000000,
  "end": 0,
  "minSpan": 10,
  "maxSpan": 10000000000,
  "connections": [
    { "id": "hadean", "label": "Hadean", "form": "region", "tStart": -4540000000, "tEnd": -4000000000, "tier": 10, "color": "#3a2b28" }
  ],
  "events": [
    { "id": "first-life", "label": "First life", "t": -3800000000, "tier": 10, "importance": 95, "blurb": "Earliest evidence of life." }
  ]
}
```

Field rules:

- `tier` (integer): the event or region label is eligible for display only when the snapped decade `round(log10(S)) <= tier`, i.e. the same decade shown in the scale readout. This is the powers-of-10 label hierarchy. (v0.3: gating used to be raw `S <= 10^tier`, which disagreed with the readout whenever S sat just above a decade, e.g. a 2.08e8 span reading "10^8" while hiding tier-8 labels.)
- `importance` (0-100): collision priority. Higher wins when labels overlap.
- `tEnd` (optional, events only): when present the event is a span. Spans shorter than 36px tall draw as a small bar on the spine; taller spans draw as lane bars: overlapping spans are assigned to separate lanes (greedy interval coloring, max 6 lanes) placed alternately left/right of the spine on wide screens and stacked right of the spine on phones, each lane labeled on its outer side, so overlaps read like a chart. Tapping a lane bar shows the event's blurb.
- `blurb` (optional): one-line detail shown on tap.
- `presets` (optional): preset jump targets, `[{ "id", "label", "c", "s" }]` where `c` is the center time and `s` the visible span. Rendered as chips in the tray. Must satisfy `minSpan <= s <= maxSpan` and the window `[c - s/2, c + s/2]` within `[start, end]`. The name `views` is reserved for third-layer visualization definitions (see dataset-format.md Layers).
- `defaultPreset` (optional): the id of a preset used as the default view when the app opens without deep-link coordinates. Deep links override it; datasets without it default to the full span.
- `connections` (optional): relationships. `form` is `arc` (1-1 edge between events), `band` (1-to-many stream with width encoding a defined quantity), or `region` (1-to-many full-width tint, the v1 band behavior). Arcs may also be listed inline on events in the simplified form. Full format, layers, and width rules: dataset-format.md.
- Validation rules (documented; a validator script is optional v1): ids unique across events and connections; `tStart < tEnd`; all times within `[start, end]`; `tier` an integer; `importance` within 0-100; connection endpoints must exist; connections are direct only.

## 6. Rendering

- Single `<canvas>`, devicePixelRatio-aware. Redraw on requestAnimationFrame during gestures; static otherwise.
- Region-form connections render as full-width background washes. Nested regions paint over their parent with their own tint. A region label renders at the top of its region when the region's pixel height is >= 28px and its tier is eligible.
- Events: dots for points, bars for spans, on a vertical spine.
- Layout breakpoint at 720px width. Below: spine at x=32 with all labels to the right. At/above: centered spine with labels alternating sides.
- Label style: 14px semibold label plus 12px date subline. System font stack. Neutral dark theme.
- Declutter v1, applied every frame:
  1. Tier gating: keep only labels with `S <= 10^tier`.
  2. Greedy collision: sort survivors by `importance` descending; each placed label claims its text height plus padding (8px at Normal density); lower-importance labels that overlap a claimed box are hidden. Their dots still render.
- Tap on a dot or label shows its blurb in a small popover.

## 7. Tray

- Bottom sheet on phone (< 720px), right-side panel on desktop. Handle/toggle reachable one-handed on phone.
- Contents:
  - Dataset picker (populated from `datasets/manifest.json`; v1 ships Earth plus one small demo dataset to prove switching works). Picker chips toggle: tapping adds or removes a dataset, at least one stays selected, and in multi mode selected chips are tagged Left / Right by side.
  - Jump to: preset chips, the union of the selected datasets' `presets` arrays (e.g. Primates, Genus Homo, Civilization, Industrial era, Present), tagged with the dataset id when several datasets are selected
  - Present button (right column above the zoom buttons, always visible; jumps to the Present preset, falls back to the dataset end)
  - Label density: Sparse / Normal / Dense (collision padding multiplier 1.5 / 1.0 / 0.6)
  - Regions on/off
  - Reset view button
  - Hint line: "Tap an era name on the timeline to zoom into it."
  - Phone ergonomics: 56px handle with a 56x6 grab pill; every tappable control is at least 44px tall.
  - Tray overlay and viewport anchoring: the stage height is set to window.innerHeight in JavaScript so the tray anchors to the visible bottom in any viewer (Dave opens local files in a viewer app, not Chrome, where CSS viewport units misbehave); the tray slides over the timeline and never resizes it, and the canvas reserves a constant inset for the closed handle only (56px handle + 10px clearance + gesture bar).
- The scale readout and zoom +/- buttons live on the canvas, not in the tray. Zoom buttons sit bottom-right, above the tray handle.

## 8. Gestures and input

- `touch-action: none` on the canvas; the app is a fixed viewport (the page itself does not scroll).
- Pull-to-refresh is suppressed: the canvas default-prevents touchmove (non-passive) and overscroll is contained, so dragging to the top cannot trigger a browser reload.
- Tray tap targets use `touch-action: manipulation` so mobile taps register as clicks without double-tap-zoom interference.
- One-finger drag pans. Pinch zooms. Double-tap zooms in one decade. Desktop: wheel zooms about cursor, drag pans, `+`/`-` keys step a decade, arrow keys pan.
- Deep link: `?dataset=<id>&c=<center>&s=<span>`. Updated via replaceState when a gesture ends, so any view is shareable and restorable.
- Tap an era band's label to zoom the viewport to fit that band (span x 1.25 margin, animated, leaving room for adjacent-era context). Event dots and labels take tap priority over band labels.

## 9. Earth dataset content plan (tiers)

| Tier (label appears when snapped decade <= tier) | Content |
|---|---|
| 10^10 | Eons: Hadean, Archean, Proterozoic, Phanerozoic |
| 10^9 | Eras (Paleozoic, Mesozoic, Cenozoic; Proterozoic eras) |
| 10^8 | Periods |
| 10^7 | Epochs; primate origins (~55 Ma) |
| 10^6 | Primate diversification; early hominins (~7-2 Ma) |
| 10^5 | Genus Homo (~2.8 Ma); H. erectus; Neanderthals; H. sapiens (~300 ka) |
| 10^4 | Paleolithic subdivisions; agriculture (~12 ka) |
| 10^3 | Neolithic; Bronze Age (~5 ka); Iron Age (~3 ka); writing |
| 10^2 | Classical through early modern |
| 10^1 | Industrial era detail (~10 yr resolution) |

Target: roughly 120-200 events, 40 bands. Compiling the data is a separate task after spec approval. Dates are approximate; the dataset records sources (ICS geologic timescale, standard human-evolution references). Curation rule learned 2026-10-18: marquee events may sit one tier above their section so every decade view has anchor labels (e.g. earliest primates at tier 8, headline Homo species at tier 7, agriculture/writing at tier 5, steam engine at tier 3). Every preset window must contain at least 2 eligible labels; verify by query, not by eye.

## 10. File layout

```
index.html                  # all CSS and JS inline
datasets/manifest.json      # dataset list for the tray picker
datasets/earth-history.json # v1 dataset
datasets/demo.json          # tiny second dataset proving the picker
```

No npm, no bundler, no runtime dependencies.

## 11. Acceptance criteria (v1)

- Opens in phone Safari/Chrome; drag and pinch are smooth on a mid-range phone.
- Zooms from the full 4.54 Ga down to a 10-year window; readout, tiers, and bands behave per sections 4-6.
- Every tray control works; switching datasets reloads cleanly.
- A deep link restores the exact view it encodes.
- Decluttering is visibly working: no overlapping labels at any decade, dots remain for hidden labels.

## 12. Open questions for review

1. Second demo dataset: RESOLVED 2026-10-18, demo is Powers of 10: Universe (built).
2. Double-tap centers on the tap point (specced). Keep it?
3. Dark theme default ok, or light?
4. Anything in the schema missing for datasets you already have in mind?
