# Pre-PyPI Launch Verification — 2026-08-20

## Go/No-Go: **GO**

The library is genuinely functional. Two real bugs were found and fixed
during this pass (both now covered by regression tests); everything else
checked out clean. Packaging is PyPI-ready.

## What was verified, and how

### Phase A — Environment setup
Fresh venv, `pip install -e .[test]` plus `build`/`twine`/`jupyter`/
`nbconvert`. Native dependencies (`rtree`, `ijson`) import cleanly. Note:
the repo's `playwright>=1.0` pin (unbounded) resolved to Playwright 1.62.0
locally, which expects a browser revision (1234) newer than what's
pre-provisioned in this sandbox (1194) — pinning `playwright==1.56.0` in
the local verification venv fixed discovery. This is a sandbox-specific
detail, not a change made to the package's own dependency pin, and not
something a real user hits (`playwright install` always fetches a matching
browser).

### Phase B — Unit tests + orphaned security scripts
`pytest -m "not browser"`: **301 passed, 1 deselected** (a `manual`-marked
PMTiles test), both before and after the fixes below.

Two root-level ad hoc scripts (`test_export_png.py`, `reproduce_xss.py`)
and one under `development/` (`test_popup_regression.py`) were regression
checks for command-injection and XSS issues, but sat outside `pytest`'s
`testpaths=["tests"]` and were never collected by CI. Ran all three
directly first to get real signal — **no vulnerability found**: the
`export_png` argv sanitization holds, and marker/popup HTML is safely
JSON-escaped + DOMPurify-sanitized, not spliced into a JS template literal.
Migrated all three into real `assert`-based pytest tests and deleted the
originals so they're actually guarded by CI going forward:
- `tests/test_export_png.py`
- `tests/test_security_xss.py`
- `tests/test_popup_regression.py`

### Phase C — Rendered-output validation (real browser)
The full `playwright_tests/test_gallery_examples.py` (120 examples) and
`test_measure_control_e2e.py` both fail in this specific sandbox — but for
an environment reason, not a code reason: every generated page
unconditionally loads DOMPurify from `cdnjs.cloudflare.com`, and most load
the default style from `demotiles.maplibre.org`; this sandbox's outbound
network policy returns `403`/`502` on `CONNECT` to both hosts (confirmed
via direct `curl` and the proxy's own status endpoint). CI already runs
this exact suite with real internet access on every push.

To get real evidence anyway, built a standalone, fully-offline Playwright
smoke test (`.browser-assets/` + a local mock style, no network calls at
all) covering 5 representative generated pages: basic map, popup, marker,
navigation controls, and clustering. **All 5 rendered successfully in real
headless Chromium — map canvas present, styled layers/sources loaded, zero
console errors, zero failed requests.** This is direct proof the
client-side runtime (the template's JS, MapLibre GL JS integration, and
DOMPurify sanitization path) genuinely works, independent of the CDN/style
availability that CI covers separately.

### Phase D — Packaging verification
```
python -m build            # sdist + wheel built cleanly
twine check --strict dist/*  # PASSED for both
```
Installed the wheel into a throwaway clean venv (no `test`/`geo` extras —
matching a real `pip install maplibreum`), and ran an import + render
smoke test from outside the repo checkout: `MAPLIBRE_VERSION` importable,
`Map().save()` produced a valid 15.9 KB HTML file containing the expected
`window.maplibreumMaps` marker. Confirms both `maplibreum/templates/*`
files ship correctly in the wheel (no `MANIFEST.in`/package-data gaps).

### Phase E — Notebooks + README
5 of 6 example notebooks (`01`–`04`, `06`) executed end-to-end with zero
errors. **Notebook 05 (`05_realtime_and_events.ipynb`) had a real bug**:
its "Animated Camera Movement" cell called
`m2.add_source("random_points", random_tracker)`, passing a
`RandomCoordinateFetcher` object directly where `add_source` expects a
dict — this isn't handled by `add_source` and blew up with
`TypeError: Object of type RandomCoordinateFetcher is not JSON
serializable` the moment the map was displayed. The correct pattern already
exists and is tested elsewhere
(`tests/test_examples/test_add_live_realtime_data.py`):
```python
m2.add_source("random_points", {"type": "geojson", "data": random_tracker.get_initial_data()})
m2.add_on_load_js(random_tracker.to_js())
```
Fixed the notebook cell to match; re-ran it and it now executes cleanly.
(One later cell in the same notebook fetches live USGS earthquake data via
`urllib.request` — that's blocked by this sandbox's network policy the
same way Phase C's CDN calls are; it's correct code, just untestable here.)

README code snippets: 2 of 3 ran cleanly. **The third had a real bug**:
`from maplibreum import LayerControl` raised `ImportError` — the
`LayerControl` class is fully implemented in `core.py` and listed in
`core.__all__`, but was never re-exported from `maplibreum/__init__.py`.
Fixed by adding it to the top-level import and `__all__`, plus a new
regression test (`tests/test_public_api_exports.py`) that asserts every
name in `maplibreum.__all__` is actually importable, so this class of bug
can't recur silently.

### Phase F — JS-injection architecture audit
Full categorized report at
`development/javascript_injection_huntdown/ARCHITECTURE_AUDIT_2026_08_20.md`.
Summary: ~70% of the library (sources, layers, expressions, popups, basic
controls, the deck.gl integration) is genuine typed-Python-to-JSON config
generation. The 3D/animation/realtime feature set relies on JS-string
templating — some of it effectively unavoidable (three.js/Babylon.js have
no Python equivalent), some of it a reasonable future cleanup target
(`custom.py`'s hardcoded shader constants, `realtime.py`'s raw-JS
`transform_fn` parameter). One dead code path was found:
`DeckGLLayer.add_to()` in `deckgl.py` is never called (`add_layer` only
uses `.serialize()`) — flagged for removal in a future cleanup, not
launch-blocking.

### Phase G — Gallery example coverage
Confirmed `development/maplibre_examples/status.json` still shows exactly
120/133 (90%) MapLibre gallery examples implemented, matching what the
README already discloses. The 13 gaps are known and listed in the status
file; no action needed for launch.

## Bugs found and fixed

1. **`LayerControl` not exported from the top-level package**
   (`maplibreum/__init__.py`) — README-documented usage was broken.
2. **Notebook 05 used the realtime-fetcher API incorrectly** — fixed to
   match the already-correct, already-tested pattern.
3. *(Not a bug, but hardened)* Three orphaned, never-CI-run security
   regression scripts confirmed no vulnerability and were migrated into
   the guarded `tests/` suite.

## Noted but out of scope for this pass

- `development/maplibre_examples/reproduced_pages/*.html` (122 files) are
  stale relative to current template/library output — running the test
  suite regenerates them with real differences. These are refreshed by the
  dedicated `update-maplibre-examples.yml` scheduled workflow, not by the
  regular test suite; left untouched here to keep this verification's diff
  focused.
- Architecture audit's "worth tightening later" items (Section 2b) are
  technical debt, not defects — no code changes made for them.
