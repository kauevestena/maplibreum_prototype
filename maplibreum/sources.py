"""Typed helpers for the MapLibre ``map.addSource`` API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Union


def _normalise_options(
    options: Mapping[str, Any], key_map: Mapping[str, str] | None = None
) -> Dict[str, Any]:
    """Return a copy of ``options`` with ``None`` entries removed.

    Parameters
    ----------
    options:
        Mapping of option names to values.
    key_map:
        Optional mapping translating Pythonic ``snake_case`` keys into their
        MapLibre camelCase equivalents.
    """

    translated: Dict[str, Any] = {}
    for key, value in options.items():
        if value is None:
            continue
        lookup = key
        if key_map is not None:
            lookup = key_map.get(key, key)
        translated[lookup] = value
    return translated


class Source:
    """Base class for MapLibre source definitions."""

    def __init__(self, type: str, **kwargs: Any) -> None:
        self.type = type
        self.options: Dict[str, Any] = dict(kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialisable representation of the source."""

        return {"type": self.type, **self.options}

    @property
    def __dict__(self) -> Dict[str, Any]:  # pragma: no cover - compatibility bridge
        """Expose ``to_dict`` for backwards compatibility."""

        return self.to_dict()

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"{self.__class__.__name__}({self.to_dict()!r})"


class RasterSource(Source):
    """Wrapper for ``raster`` sources backed by tiled imagery."""

    _KEY_MAP = {
        "tile_size": "tileSize",
        "min_zoom": "minzoom",
        "max_zoom": "maxzoom",
    }

    def __init__(
        self,
        tiles: Union[str, Sequence[str], None] = None,
        *,
        url: Optional[str] = None,
        tile_size: int = 256,
        attribution: Optional[str] = None,
        bounds: Optional[Sequence[float]] = None,
        scheme: Optional[str] = None,
        min_zoom: Optional[int] = None,
        max_zoom: Optional[int] = None,
        volatile: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        if tiles is None and url is None:
            raise ValueError("RasterSource requires either 'tiles' or 'url'")

        resolved: Dict[str, Any] = {}
        if tiles is not None:
            if isinstance(tiles, str):
                resolved["tiles"] = [tiles]
            else:
                resolved["tiles"] = list(tiles)
        if url is not None:
            resolved["url"] = url

        resolved.update(
            _normalise_options(
                {
                    "tile_size": tile_size,
                    "attribution": attribution,
                    "bounds": list(bounds) if bounds is not None else None,
                    "scheme": scheme,
                    "min_zoom": min_zoom,
                    "max_zoom": max_zoom,
                    "volatile": volatile,
                },
                self._KEY_MAP,
            )
        )
        resolved.update(_normalise_options(kwargs, self._KEY_MAP))

        super().__init__("raster", **resolved)


class RasterDemSource(Source):
    """Wrapper for ``raster-dem`` terrain sources."""

    _KEY_MAP = {
        "tile_size": "tileSize",
        "min_zoom": "minzoom",
        "max_zoom": "maxzoom",
    }

    def __init__(
        self,
        *,
        url: Optional[Union[str, Sequence[str]]] = None,
        tiles: Union[str, Sequence[str], None] = None,
        tile_size: int = 512,
        attribution: Optional[str] = None,
        encoding: Optional[str] = None,
        bounds: Optional[Sequence[float]] = None,
        min_zoom: Optional[int] = None,
        max_zoom: Optional[int] = None,
        volatile: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        if url is None and tiles is None:
            raise ValueError("RasterDemSource requires either 'url' or 'tiles'")

        resolved: Dict[str, Any] = {}
        if tiles is not None:
            if isinstance(tiles, str):
                resolved["tiles"] = [tiles]
            else:
                resolved["tiles"] = list(tiles)
        if url is not None:
            if isinstance(url, str):
                resolved["url"] = url
            else:
                resolved["tiles"] = list(url)

        resolved.update(
            _normalise_options(
                {
                    "tile_size": tile_size,
                    "attribution": attribution,
                    "encoding": encoding,
                    "bounds": list(bounds) if bounds is not None else None,
                    "min_zoom": min_zoom,
                    "max_zoom": max_zoom,
                    "volatile": volatile,
                },
                self._KEY_MAP,
            )
        )
        resolved.update(_normalise_options(kwargs, self._KEY_MAP))

        super().__init__("raster-dem", **resolved)


class VectorSource(Source):
    """Wrapper for ``vector`` tile sources."""

    _KEY_MAP = {
        "min_zoom": "minzoom",
        "max_zoom": "maxzoom",
        "tile_size": "tileSize",
        "promote_id": "promoteId",
    }

    def __init__(
        self,
        *,
        tiles: Union[str, Sequence[str], None] = None,
        url: Optional[str] = None,
        bounds: Optional[Sequence[float]] = None,
        scheme: Optional[str] = None,
        min_zoom: Optional[int] = None,
        max_zoom: Optional[int] = None,
        attribution: Optional[str] = None,
        promote_id: Optional[Union[str, Mapping[str, str]]] = None,
        volatile: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        if tiles is None and url is None:
            raise ValueError("VectorSource requires either 'tiles' or 'url'")

        resolved: Dict[str, Any] = {}
        if tiles is not None:
            if isinstance(tiles, str):
                resolved["tiles"] = [tiles]
            else:
                resolved["tiles"] = list(tiles)
        if url is not None:
            resolved["url"] = url

        resolved.update(
            _normalise_options(
                {
                    "bounds": list(bounds) if bounds is not None else None,
                    "scheme": scheme,
                    "min_zoom": min_zoom,
                    "max_zoom": max_zoom,
                    "attribution": attribution,
                    "promote_id": promote_id,
                    "volatile": volatile,
                },
                self._KEY_MAP,
            )
        )
        resolved.update(_normalise_options(kwargs, self._KEY_MAP))

        super().__init__("vector", **resolved)


class GeoJSONSource(Source):
    """Wrapper for GeoJSON sources with clustering and filtering options."""

    _KEY_MAP = {
        "max_zoom": "maxzoom",
        "cluster_radius": "clusterRadius",
        "cluster_max_zoom": "clusterMaxZoom",
        "cluster_min_points": "clusterMinPoints",
        "cluster_properties": "clusterProperties",
        "line_metrics": "lineMetrics",
        "generate_id": "generateId",
        "promote_id": "promoteId",
        "pre_fetch_zoom_delta": "preFetchZoomDelta",
    }

    def __init__(
        self,
        data: Any,
        *,
        attribution: Optional[str] = None,
        max_zoom: Optional[int] = None,
        buffer: Optional[int] = None,
        tolerance: Optional[float] = None,
        cluster: Optional[bool] = None,
        cluster_radius: Optional[int] = None,
        cluster_max_zoom: Optional[int] = None,
        cluster_min_points: Optional[int] = None,
        cluster_properties: Optional[Mapping[str, Any]] = None,
        line_metrics: Optional[bool] = None,
        generate_id: Optional[bool] = None,
        promote_id: Optional[Union[str, Mapping[str, str]]] = None,
        filter: Optional[Any] = None,
        pre_fetch_zoom_delta: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        resolved: Dict[str, Any] = {"data": data}
        resolved.update(
            _normalise_options(
                {
                    "attribution": attribution,
                    "max_zoom": max_zoom,
                    "buffer": buffer,
                    "tolerance": tolerance,
                    "cluster": cluster,
                    "cluster_radius": cluster_radius,
                    "cluster_max_zoom": cluster_max_zoom,
                    "cluster_min_points": cluster_min_points,
                    "cluster_properties": cluster_properties,
                    "line_metrics": line_metrics,
                    "generate_id": generate_id,
                    "promote_id": promote_id,
                    "filter": filter,
                    "pre_fetch_zoom_delta": pre_fetch_zoom_delta,
                },
                self._KEY_MAP,
            )
        )
        resolved.update(_normalise_options(kwargs, self._KEY_MAP))

        super().__init__("geojson", **resolved)

    @property
    def data(self) -> Any:
        """The GeoJSON data for the source."""
        return self.options["data"]

    @classmethod
    def from_file(
        cls, file_path: Union[str, Path], **kwargs: Any
    ) -> GeoJSONSource:
        """Create a GeoJSONSource from a local file.

        Parameters
        ----------
        file_path:
            Path to the GeoJSON file.
        **kwargs:
            Other options for the GeoJSONSource.

        Returns
        -------
        A new GeoJSONSource instance.
        """
        with open(file_path) as f:
            data = json.load(f)

        return cls(data=data, **kwargs)


class ImageSource(Source):
    """Wrapper for ``image`` sources with optional bounds shortcuts."""

    def __init__(
        self,
        *,
        url: str,
        coordinates: Optional[Sequence[Sequence[float]]] = None,
        bounds: Optional[Sequence[float]] = None,
        attribution: Optional[str] = None,
        volatile: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        if coordinates is None and bounds is None:
            raise ValueError("ImageSource requires either 'coordinates' or 'bounds'")

        if coordinates is None and bounds is not None:
            if len(bounds) != 4:
                raise ValueError("bounds must be [west, south, east, north]")
            west, south, east, north = bounds
            coordinates = [
                [west, north],
                [east, north],
                [east, south],
                [west, south],
            ]

        resolved: Dict[str, Any] = {
            "url": url,
            "coordinates": [list(coord) for coord in coordinates or []],
        }
        resolved.update(
            _normalise_options(
                {"attribution": attribution, "volatile": volatile}, key_map=None
            )
        )
        resolved.update(_normalise_options(kwargs))

        super().__init__("image", **resolved)


class VideoSource(Source):
    """Wrapper for ``video`` sources supporting multiple URLs."""

    def __init__(
        self,
        urls: Union[str, Sequence[str]],
        *,
        coordinates: Optional[Sequence[Sequence[float]]] = None,
        bounds: Optional[Sequence[float]] = None,
        attribution: Optional[str] = None,
        volatile: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        if coordinates is None and bounds is None:
            raise ValueError("VideoSource requires either 'coordinates' or 'bounds'")

        if isinstance(urls, str):
            url_list = [urls]
        else:
            url_list = list(urls)

        if coordinates is None and bounds is not None:
            if len(bounds) != 4:
                raise ValueError("bounds must be [west, south, east, north]")
            west, south, east, north = bounds
            coordinates = [
                [west, north],
                [east, north],
                [east, south],
                [west, south],
            ]

        resolved: Dict[str, Any] = {
            "urls": url_list,
            "coordinates": [list(coord) for coord in coordinates or []],
        }
        resolved.update(
            _normalise_options(
                {"attribution": attribution, "volatile": volatile}, key_map=None
            )
        )
        resolved.update(_normalise_options(kwargs))

        super().__init__("video", **resolved)


class CanvasSource(Source):
    """Wrapper for ``canvas`` sources."""

    def __init__(
        self,
        *,
        canvas: str,
        coordinates: Optional[Sequence[Sequence[float]]] = None,
        bounds: Optional[Sequence[float]] = None,
        animate: Optional[bool] = None,
        attribution: Optional[str] = None,
        volatile: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        if coordinates is None and bounds is None:
            raise ValueError("CanvasSource requires either 'coordinates' or 'bounds'")

        if coordinates is None and bounds is not None:
            if len(bounds) != 4:
                raise ValueError("bounds must be [west, south, east, north]")
            west, south, east, north = bounds
            coordinates = [
                [west, north],
                [east, north],
                [east, south],
                [west, south],
            ]

        resolved: Dict[str, Any] = {
            "canvas": canvas,
            "coordinates": [list(coord) for coord in coordinates or []],
        }
        resolved.update(
            _normalise_options(
                {
                    "animate": animate,
                    "attribution": attribution,
                    "volatile": volatile,
                }
            )
        )
        resolved.update(_normalise_options(kwargs))

        super().__init__("canvas", **resolved)


__all__ = [
    "Source",
    "RasterSource",
    "RasterDemSource",
    "VectorSource",
    "GeoJSONSource",
    "ImageSource",
    "VideoSource",
    "CanvasSource",
    "VideoOverlay",
]


class VideoOverlay:
    """
    Helper class for managing video overlays with playback controls.
    
    This class provides an alternative to JavaScript injection for
    video overlay management by handling source setup and playback control.
    """
    
    def __init__(self, source_id, layer_id, urls, coordinates,
                 autoplay=True, loop=True, click_to_toggle=True):
        """Initialize a VideoOverlay.
        
        Parameters
        ----------
        source_id : str
            ID for the video source.
        layer_id : str
            ID for the video raster layer.
        urls : list of str
            List of video URLs (multiple formats for browser compatibility).
        coordinates : list of [lon, lat] pairs
            Four corner coordinates for the video overlay (clockwise from top-left).
        autoplay : bool, optional
            Whether to autoplay the video (default: True).
        loop : bool, optional
            Whether to loop the video (default: True).
        click_to_toggle : bool, optional
            Whether clicking the map toggles play/pause (default: True).
        """
        self.source_id = source_id
        self.layer_id = layer_id
        self.urls = urls if isinstance(urls, list) else [urls]
        self.coordinates = coordinates
        self.autoplay = autoplay
        self.loop = loop
        self.click_to_toggle = click_to_toggle
        
    def get_source_config(self):
        """Get the video source configuration.
        
        Returns
        -------
        dict
            Video source configuration.
        """
        return {
            "type": "video",
            "urls": self.urls,
            "coordinates": self.coordinates
        }
    
    def get_layer_config(self):
        """Get the video layer configuration.
        
        Returns
        -------
        dict
            Raster layer configuration for the video.
        """
        return {
            "id": self.layer_id,
            "type": "raster",
            "source": self.source_id
        }
    
    def to_js(self):
        """Generate JavaScript code for video playback control.
        
        Returns
        -------
        str
            JavaScript code for controlling video playback.
        """
        # Setup code
        state_var = f"_videoPlaying_{self.source_id.replace('-', '_')}"
        
        setup_code = f"""
(function() {{
    // Initialize video playback state
    window.{state_var} = {str(self.autoplay).lower()};
    
    // Get video source
    const videoSource = map.getSource('{self.source_id}');
    if (!videoSource) {{
        console.warn('Video source "{self.source_id}" not found');
        return;
    }}
"""
        
        # Click handler for toggle
        if self.click_to_toggle:
            toggle_code = f"""
    
    // Add click handler to toggle playback
    map.on('click', function() {{
        if (window.{state_var}) {{
            videoSource.pause();
            window.{state_var} = false;
        }} else {{
            videoSource.play();
            window.{state_var} = true;
        }}
    }});
"""
        else:
            toggle_code = ""
        
        js_code = setup_code + toggle_code + """
}})();
"""
        return js_code
    
    def get_play_method(self):
        """Get JavaScript method call to play the video.
        
        Returns
        -------
        str
            JavaScript code to play the video.
        """
        return f"map.getSource('{self.source_id}').play();"
    
    def get_pause_method(self):
        """Get JavaScript method call to pause the video.
        
        Returns
        -------
        str
            JavaScript code to pause the video.
        """
        return f"map.getSource('{self.source_id}').pause();"
