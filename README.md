# Deep Time

An infinitely zoomable, phone-first vertical timeline. One self-contained
HTML file, no server, no dependencies: pinch, scroll, or use the buttons
to zoom from billions of years down to a single year on one shared axis.

Live site: https://dnellis74.github.io/deep-time/

## Use it

- Open https://dnellis74.github.io/deep-time/ in any browser, or
- Download `index.html` from this repo and open it directly. It works
  offline: every dataset is inlined into the file.

Tap an event for details. Tap a region label to zoom to fit that era.
The tray (bottom handle on phones, side panel on desktop) holds the
dataset picker, jump presets, and the Present button. The scale chip at
the top-right shows the actual visible span, with the zoom scale (a
power of ten) beneath it. The full behavior spec, including version
history, is in `spec.md`.

## Features

- Continuous exponential zoom about the gesture midpoint, with the scale
  readout snapping to powers of ten.
- Tier gating: a label appears when the visible span's decade
  (`round(log10(span))`) is at or below the label's tier, so coarse
  views show era-level labels and fine views show detail.
- Auto-promotion: when tier gating leaves a dataset with fewer than 4
  visible events in view, the highest-importance in-view events fill the
  gap, so sparse eras still show a few major events.
- Show-all datasets: a dataset flagged `showAllEvents` skips tier
  gating, so every in-view event renders a dot at every zoom level.
  Both Connections datasets carry the flag; label collision declutter
  still applies.
- Background layers: universe, earth, and human history are the
  background, designated in the viewer code rather than in the dataset
  files, so datasets stay reusable. One or two foreground datasets
  merge into one single column, with the foreground integrated into
  the background; three or more foreground datasets render as columns
  of the foregrounds only, with no background rendered. Two or more
  foreground datasets open on the foregrounds' combined span. The app
  opens on the background trio.
- Multiselect: pick several datasets at once. One or two foreground
  datasets merge into one single timeline; three or more render as
  one column each, all sharing the same time axis. Toggle chips in the tray;
  deep links take a comma-separated list (`?d=jewish-history,palestinian-history&c=-339.5&s=389`).
- Presets: jump to named windows (eras, themes). Deep links carry the
  dataset list plus center and span (`?d=...&c=...&s=...`); Reset
  returns to the full span.

## Datasets

`index.html` is a built file: the datasets below are inlined into it.
The source data lives in `datasets/` (one JSON file per dataset, plus
`manifest.json`, the registry that lists them). The format spec and a
paste-ready prompt for generating new datasets are in
[`datasets/README.md`](datasets/README.md).

| Dataset | Events | Regions | Presets |
| --- | ---: | ---: | ---: |
| History of Earth | 75 | 30 | 3 |
| Human History | 79 | 20 | 10 |
| Powers of 10: Universe | 18 | 3 | 3 |
| Jewish History: Am Yisrael and Eretz Yisrael | 82 | 8 | 6 |
| The Southern Levant: Shared Timeline | 72 | 8 | 6 |
| Palestinian History: The People of Filastin | 81 | 8 | 6 |
| The Trigger Effect (Connections S1E1) | 12 | 0 | 4 |
| The Long Chain (Connections S1E7) | 22 | 0 | 4 |

## Validate a dataset

`validate_datasets.py` checks a dataset file against the format rules
(required fields, id format and uniqueness, times in range, tier and
importance ranges, connection endpoints, preset windows holding at
least 2 visible labels, and more). It reports errors (must fix) and
warnings (should fix, including same-window importance ties, which
make auto-promotion's picks arbitrary).

```sh
python3 validate_datasets.py datasets/your-dataset.json
```

## Build

`index.html` is built, not written by hand. The sources are
`src/index.html` (the template) and `datasets/` (the data). To
regenerate it after changing a dataset:

```sh
python3 validate_datasets.py datasets/*.json
python3 build.py
```

`build.py` inlines every dataset from `datasets/manifest.json` into
`src/index.html` and writes the self-contained `index.html`. A fresh
clone builds byte-identically to the checked-in file.

## Contributing a dataset

Follow [`datasets/README.md`](datasets/README.md): it has the full
JSON spec, a minimal example, and a prompt you can paste into an
LLM to generate a dataset. Validate the result (0 errors), then
submit the JSON file plus its `manifest.json` entry. The built
`index.html` is regenerated from `datasets/` when a dataset lands.
