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
