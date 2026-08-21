# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-08-20

### Added
- Added a complete-style dropdown control, external ES-module and stylesheet loading, structured vector-feature popups, reusable feature-state hover handling, and page-level dashboard elements.
- Retained initial source definitions on the generated map runtime so large mutable GeoJSON sources can be reused without serializing a second copy.
- Added five production field-test examples reproducing the distinct MapLibre applications deployed by `opensidewalkmap_beta`: the main node map, accessible routing, hazard analysis, completeness analysis, and data-acquisition dashboard.

### Changed
- Standardized generated maps on MapLibre GL JS 6.0.0 and its ES module build.
- Added an independent jsDelivr fallback for the MapLibre runtime and stylesheet.
- Normalized raw GeoJSON and `__geo_interface__` objects into valid GeoJSON sources.
- Expanded CI across Python 3.9–3.13 with separate browser, documentation, and package-release gates.
- Added eight-shard browser validation for all implemented gallery examples.
- Added live-CDN smoke tests for unpkg and the forced jsDelivr fallback.
- Added a clean-wheel installation and standalone-render smoke test.

### Fixed
- JSON-encoded floating-panel HTML so backticks and `${...}` text cannot break out of a JavaScript template literal, and removed its unnecessary delayed insertion race.
- Declared the existing runtime use of `requests` as an installation dependency.
- Made every implemented gallery example generate a browser-testable HTML page.
- Served browser tests over local HTTP and adapted MapLibre 6's ES module
  version API to the generated page's browser-global compatibility contract.
- Repaired strict Sphinx documentation builds and clarified package discovery for bundled templates.

## [0.1.0] - 2025-09-15
### Added
- Initial MapLibre integration with a `Map` object that renders interactive maps in notebooks and exported HTML.
- Layer primitives including GeoJSON overlays, choropleths, clustered data sources, and time-aware visualisations.
- Media overlays for static imagery and video along with floating image support.
- Marker utilities with HTML, DivIcon, and Beautify icon support plus draggable markers and clustering helpers.
- Map controls such as mini map, measure, search, draw tools, layer toggles, and camera helpers.
- Terrain, sky, and fog helpers alongside expression builders for data-driven styling.
- Event wiring for click, move, and draw callbacks in Jupyter environments.

[Unreleased]: https://github.com/kauevestena/maplibreum_prototype/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/kauevestena/maplibreum_prototype/releases/tag/v0.2.0
[0.1.0]: https://github.com/kauevestena/maplibreum_prototype/tree/e0ed3869ac734cfd8077f1f1a6b9b8245ff066e8
