"""Lightweight helpers for constructing MapLibre layer definitions."""

from __future__ import annotations

from typing import Any, Dict, Optional


class Layer:
    """Generic representation of a MapLibre style layer."""

    def __init__(
        self,
        id: str,
        type: str,
        source: Optional[str] = None,
        *,
        paint: Optional[Dict[str, Any]] = None,
        layout: Optional[Dict[str, Any]] = None,
        filter: Optional[Any] = None,
        minzoom: Optional[float] = None,
        maxzoom: Optional[float] = None,
        source_layer: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        slot: Optional[str] = None,
        **extra: Any,
    ) -> None:
        """Store layer configuration for later serialization."""

        self.id = id
        self.type = type
        self._options: Dict[str, Any] = {}

        if source is not None:
            self._options["source"] = source
        if paint is not None:
            self._options["paint"] = paint
        if layout is not None:
            self._options["layout"] = layout
        if filter is not None:
            self._options["filter"] = filter
        if minzoom is not None:
            self._options["minzoom"] = minzoom
        if maxzoom is not None:
            self._options["maxzoom"] = maxzoom
        if source_layer is not None:
            self._options["source-layer"] = source_layer
        if metadata is not None:
            self._options["metadata"] = metadata
        if slot is not None:
            self._options["slot"] = slot

        # Include any additional keyword arguments, skipping ``None`` values.
        for key, value in extra.items():
            if value is not None:
                self._options[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Return the layer definition as a plain dictionary."""

        return {"id": self.id, "type": self.type, **self._options}


class RasterLayer(Layer):
    def __init__(self, id: str, source: str, **kwargs: Any) -> None:
        super().__init__(id, "raster", source, **kwargs)


class HillshadeLayer(Layer):
    def __init__(self, id: str, source: str, **kwargs: Any) -> None:
        super().__init__(id, "hillshade", source, **kwargs)


class ColorReliefLayer(Layer):
    def __init__(self, id: str, source: str, **kwargs: Any) -> None:
        super().__init__(id, "color-relief", source, **kwargs)


class FillLayer(Layer):
    def __init__(self, id: str, source: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(id, "fill", source, **kwargs)


class LineLayer(Layer):
    def __init__(self, id: str, source: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(id, "line", source, **kwargs)


class CircleLayer(Layer):
    def __init__(self, id: str, source: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(id, "circle", source, **kwargs)


class SymbolLayer(Layer):
    def __init__(self, id: str, source: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(id, "symbol", source, **kwargs)


class FillExtrusionLayer(Layer):
    def __init__(self, id: str, source: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(id, "fill-extrusion", source, **kwargs)


__all__ = [
    "Layer",
    "RasterLayer",
    "HillshadeLayer",
    "ColorReliefLayer",
    "FillLayer",
    "LineLayer",
    "CircleLayer",
    "SymbolLayer",
    "FillExtrusionLayer",
]
