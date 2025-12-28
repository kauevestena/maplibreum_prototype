"""PMTiles integration for maplibreum."""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from .sources import Source


class PMTilesProtocol:
    """Helper to register the PMTiles protocol."""

    def __init__(self, script_url: str = "https://unpkg.com/pmtiles@3.2.0/dist/pmtiles.js"):
        self.script_url = script_url

    def register(self, map_instance: "Map") -> None:
        """Register the PMTiles protocol on the map instance."""
        map_instance.add_external_script(self.script_url)

        js_code = """
(function() {
    if (typeof pmtiles === 'undefined') {
        console.error('PMTiles library is not loaded');
        return;
    }
    const protocol = new pmtiles.Protocol();
    maplibregl.addProtocol('pmtiles', protocol.tile);
})();
"""
        map_instance.add_on_load_js(js_code)


class PMTilesSource(Source):
    """Wrapper for PMTiles sources."""

    def __init__(
        self,
        url: str,
        *,
        attribution: Optional[str] = None,
        min_zoom: Optional[int] = None,
        max_zoom: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a PMTiles source.

        Parameters
        ----------
        url : str
            The URL to the PMTiles archive.
        attribution : str, optional
            Attribution text.
        min_zoom : int, optional
            Minimum zoom level.
        max_zoom : int, optional
            Maximum zoom level.
        kwargs : Any
            Additional source options.
        """
        if not url.startswith("pmtiles://") and not url.startswith("https://"):
             # If it's a direct link to a file but doesn't have the protocol prefix
             if url.endswith(".pmtiles"):
                 url = "pmtiles://" + url

        resolved: Dict[str, Any] = {
            "url": url,
        }

        if attribution:
            resolved["attribution"] = attribution
        if min_zoom is not None:
            resolved["minzoom"] = min_zoom
        if max_zoom is not None:
            resolved["maxzoom"] = max_zoom

        resolved.update(kwargs)

        super().__init__("vector", **resolved)
