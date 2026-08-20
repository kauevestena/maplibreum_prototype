# Architecture Audit: Native Python Config vs. Raw JS Injection

**Date:** 2026-08-20
**Scope:** Pre-PyPI-launch review of how much of maplibreum generates MapLibre
GL JS behavior through typed Python config (the Folium-style promise of the
library) versus how much still relies on hand-written JavaScript strings
spliced into the page.

## Summary

Roughly 70% of the library — the part most users will touch day to day — is
genuine, typed Python-to-JSON config generation with no JS string-building
involved. The rest is JavaScript-string templating, and it splits cleanly
into three categories: work that's arguably unavoidable given the underlying
JS libraries involved, work that's a legitimate future cleanup target, and
one piece of dead code. None of this blocks a PyPI launch — it's disclosed
here as a technical-debt map, not a list of bugs.

## 1. Genuine native-Python config generation (no action needed)

- `sources.py`, `layers.py`, `markers.py` — build plain dicts (`to_dict()`)
  serialized via Jinja's `tojson` filter.
- `expressions.py` — builds MapLibre style expressions as nested Python
  lists with structural validation; zero JS strings.
- Basic controls (`NavigationControl`, `ScaleControl`, `FullscreenControl`,
  `GeolocateControl`, `TerrainControl`, `GlobeControl` in `controls.py`) —
  plain option dicts rendered generically by the template.
- `deckgl.py`'s `DeckGLLayer.serialize()` (used by `core.py:625-641` via
  `Map.add_layer`) produces a clean JSON config consumed by a genuine
  runtime interpreter, `MaplibreumDeckGLOverlayManager`, in
  `maplibreum/templates/map_template.html:248-423`. This is the strongest
  example in the codebase of a fully data-driven third-party-library
  integration — worth using as the template for any future cleanup below.

## 2a. Thin JS-templating that's effectively unavoidable

- `maplibreum/threejs.py:77-297`, `maplibreum/babylon.py:53-135` — build a
  complete custom WebGL layer (`onAdd`/`render` callbacks, scene graph,
  matrices, lighting) as one f-string, interpolating only numeric/URI
  parameters. Three.js and Babylon.js have no Python bindings, so *some*
  amount of generated JS is inherent to offering these integrations at all.
  Not a cleanup target; flagged here only so it's not mistaken for a gap.

## 2b. Thin JS-templating worth tightening in a future release

- `maplibreum/custom.py:5-249` (`CustomGlobeLayer`) — ships two module-level
  constants, `ON_ADD_JS`/`RENDER_JS` (~200 lines of hardcoded WebGL shader
  code), with zero Python-level configurability. A good candidate for a
  typed config surface later.
- `maplibreum/realtime.py:98-261` (`LiveDataFetcher`, and its subclass
  `RandomCoordinateFetcher`) — generates a full `setInterval`/`fetch`
  polling loop as an f-string. `transform_fn` is a **user-facing parameter
  that is literally "pass me a JS function as a string"**
  (`realtime.py:119-121`) — this is an intentional, documented escape hatch
  rather than a hidden injection point, but it's worth calling out
  explicitly since it's the one place a library user is asked to author raw
  JS directly as part of the supported API.
- `maplibreum/animation.py:159-239,270-311`,
  `maplibreum/experimental.py:79-106,256-344` — same pattern: a Python
  method with numeric/name substitution that returns a full imperative JS
  routine, handed to `add_on_load_js`.
- `maplibreum/controls.py` — `onclick_js` (also surfaced via
  `core.py:2246`), and `ButtonControl`/`ToggleControl`'s `on_action`/
  `off_action` — direct user-facing raw-JS parameters.

`core.py:1488` `add_on_load_js(code: str)` is a legitimate, clearly
documented escape hatch ("Schedule raw JavaScript to execute"). The thing
worth tracking is that it isn't *just* an opt-in user feature — it's also
the primary internal implementation mechanism for most of the classes
listed above (`BabylonLayer`, `ThreeJSLayer`, `CustomGlobeLayer`,
`RouteAnimation`, `AnimatedIcon`, `MapSynchronizer`, `GlobeInteraction`,
`PMTilesProtocol`, `MeasurementTool`, `MapboxDrawControl`, etc. — see
`core.py:607,617,1025,1282` and `custom.py:245`, `pmtiles.py:34`).

## 3. Dead code

- `maplibreum/deckgl.py:80-145` — `DeckGLLayer.add_to()` hand-builds a full
  custom-layer JS string and is **never called**. `Map.add_layer` only ever
  calls `.serialize()` (`core.py:625-641`), and no test in `tests/`
  references `add_to` on a `DeckGLLayer` (confirmed via
  `grep -rn "add_to" tests/` — the only hits are `Marker.add_to`,
  `GeoJson.add_to`, etc., unrelated classes). Safe to remove in a small,
  separate cleanup PR; not required for launch.

## 4. Template splice-point inventory

`maplibreum/templates/map_template.html` — every `{{ x | safe }}` point
where a raw string enters the rendered `<script>`:

| Line | Expression | Source of the string |
|------|------------|----------------------|
| 498 | `protocol.definition \| safe` | library-internal (`PMTilesProtocol` etc.) |
| 759 | `ctrl.options.onclick_js \| safe` | user-supplied (documented escape hatch) |
| 806, 810 | `ctrl.options.on_action` / `off_action \| safe` | user-supplied (documented escape hatch) |
| 1201 | `callback \| safe` (on-load callback) | user-supplied via `add_on_load_js` |
| 1289 | `animation \| safe` | library-internal (`animation.py`) |
| 1355 | `binding.js \| safe` | library-internal |
| 1375 | `extra_js \| safe` (catch-all) | user-supplied |

Marker/popup HTML content is **not** in this list — it goes through
`{{ marker.html | tojson }}` + `DOMPurify.sanitize()` (see
`tests/test_security_xss.py`, added in this verification pass), which is
the safe pattern the table above should eventually be measured against for
any future hardening work on the user-supplied rows.

## Recommendation

No changes required before the PyPI launch. For a future release: consider
(a) removing the dead `DeckGLLayer.add_to()`, and (b) giving `custom.py`'s
`CustomGlobeLayer` a typed config surface instead of two hardcoded JS
constants, following the `deckgl.py`/`MaplibreumDeckGLOverlayManager`
pattern as the model.
