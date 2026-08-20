"""Shared configuration for the OpenSidewalkMap field-test examples."""

from __future__ import annotations

import json
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from maplibreum import Map
from maplibreum.protocols import PMTilesProtocol


BASE_URL = "https://kauevestena.github.io/opensidewalkmap_beta/"
PMTILES_SCRIPT_URL = "https://unpkg.com/pmtiles@4.5.0/dist/pmtiles.js"
OSM_ATTRIBUTION = (
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
)
CARTO_ATTRIBUTION = (
    f'{OSM_ATTRIBUTION}; © <a href="https://carto.com/attributions">CARTO</a>'
)


def raster_style(theme: str = "light") -> dict[str, Any]:
    """Return a compact CARTO raster style matching the OSWM module basemaps."""

    tile_set = "light_all" if theme == "light" else "dark_all"
    background = "#edf0f2" if theme == "light" else "#111821"
    return {
        "version": 8,
        "name": f"CARTO {theme.title()}",
        "sources": {
            "carto": {
                "type": "raster",
                "tiles": [
                    f"https://a.basemaps.cartocdn.com/{tile_set}/{{z}}/{{x}}/{{y}}@2x.png"
                ],
                "tileSize": 256,
                "attribution": CARTO_ATTRIBUTION,
            }
        },
        "layers": [
            {"id": "background", "type": "background", "paint": {"background-color": background}},
            {"id": "carto", "type": "raster", "source": "carto"},
        ],
    }


def empty_feature_collection() -> dict[str, Any]:
    return {"type": "FeatureCollection", "features": []}


def load_json(source: Any) -> Any:
    """Load JSON from an injected object, local path, or HTTP(S) URL."""

    if isinstance(source, Mapping) or isinstance(source, list):
        return deepcopy(source)

    text_source = str(source)
    if text_source.startswith(("http://", "https://")):
        request = Request(text_source, headers={"User-Agent": "maplibreum-field-test/1"})
        with urlopen(request, timeout=60) as response:
            return json.load(response)

    with Path(text_source).expanduser().open(encoding="utf-8") as stream:
        return json.load(stream)


def add_standard_controls(
    map_object: Map,
    *,
    geolocate: bool = True,
    scale_position: str = "bottom-right",
) -> None:
    map_object.add_control(
        "navigation",
        "top-right",
        {"visualizePitch": True, "showZoom": True, "showCompass": True},
    )
    map_object.add_control("fullscreen", "top-right")
    map_object.add_control("scale", scale_position, {"unit": "metric"})
    if geolocate:
        map_object.add_control(
            "geolocate",
            "top-right",
            {
                "positionOptions": {"enableHighAccuracy": True},
                "trackUserLocation": True,
                "showUserHeading": True,
            },
        )


def add_pmtiles_v4(map_object: Map) -> None:
    map_object.add_pmtiles_protocol(PMTilesProtocol(script_url=PMTILES_SCRIPT_URL))


def save_map(map_object: Map, output: str | Path) -> Path:
    destination = Path(output).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    map_object.save(str(destination))
    return destination
