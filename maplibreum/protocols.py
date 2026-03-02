"""Helpers for registering custom MapLibre data loading protocols."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

DEFAULT_PM_TILES_SCRIPT = "https://unpkg.com/pmtiles@3.2.0/dist/pmtiles.js"


@dataclass(frozen=True)
class PMTilesProtocol:
    """Describe a ``pmtiles://`` protocol bridge for MapLibre GL."""

    name: str = "pmtiles"
    script_url: str = DEFAULT_PM_TILES_SCRIPT
    credentials: Optional[str] = None

    def to_render_payload(self) -> Dict[str, str]:
        """Return a serialisable payload for the HTML template."""

        payload: Dict[str, str] = {"name": self.name}
        if self.credentials is not None:
            payload["credentials"] = self.credentials
        return payload


@dataclass(frozen=True)
class PMTilesSource:
    """Describe a PMTiles archive that should be available to MapLibre."""

    archive_url: str
    protocol: str = "pmtiles"
    credentials: Optional[str] = None

    @property
    def style_url(self) -> str:
        """Return the MapLibre source URL for the archive."""

        return f"{self.protocol}://{self.archive_url}"

    def to_render_payload(self) -> Dict[str, str]:
        """Return a serialisable payload for the HTML template."""

        payload: Dict[str, str] = {
            "protocol": self.protocol,
            "archive": self.archive_url,
        }
        if self.credentials is not None:
            payload["credentials"] = self.credentials
        return payload


@dataclass
class Protocol:
    """Generic custom protocol definition."""

    name: str
    definition: str


@dataclass
class FeatureTransformProtocol:
    """Protocol for transforming vector tile features on the fly."""

    name: str
    process_feature_js: str

    @property
    def definition(self) -> str:
        """Return the JavaScript implementation of the protocol."""
        return f"""
        const url = params.url.replace('{self.name}://', '');
        const [{{ default: Protobuf }}, {{ VectorTile }}, {{ default: tileToProtobuf }}] = await Promise.all([
            import('https://unpkg.com/pbf@4.0.1/dist/pbf.min.js'),
            import('https://esm.run/@mapbox/vector-tile@2.0.3/index.js'),
            import('https://esm.run/vt-pbf@3.1.3/index.js'),
        ]);
        const response = await fetch(url);
        const data = await response.arrayBuffer();
        const tile = new VectorTile(new Protobuf(data));
        const layers = Object.fromEntries(
            Object.entries(tile.layers).map(([layerId, layer]) => [
                layerId,
                {{
                    ...layer,
                    feature: (index) => {{
                        const feature = layer.feature(index);
                        {self.process_feature_js}
                        return feature;
                    }},
                }},
            ])
        );
        const encoded = tileToProtobuf({{ layers }});
        return {{ data: encoded.buffer }};
        """
