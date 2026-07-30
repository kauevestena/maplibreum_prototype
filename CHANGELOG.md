# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Standardized generated maps on MapLibre GL JS 6.0.0 and its ES module build.
- Added an independent jsDelivr fallback for the MapLibre runtime and stylesheet.
- Normalized raw GeoJSON and `__geo_interface__` objects into valid GeoJSON sources.
- Expanded CI across Python 3.9–3.13 with separate browser, documentation, and package-release gates.

### Fixed
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

[0.1.0]: https://github.com/kauevestena/maplibreum_prototype/releases/tag/v0.1.0
