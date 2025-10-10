"""This module contains experimental features."""

from __future__ import annotations

import textwrap

from .core import Map


class MapSynchronizer:
    """Synchronize movement of multiple maps."""

    def __init__(self, maps: list[Map]) -> None:
        if len(maps) < 2:
            raise ValueError("MapSynchronizer requires at least two maps.")
        self._maps = maps
        self._primary_map = maps[0]
        self._secondary_maps = maps[1:]

    def add_to(self, map_obj: Map) -> None:
        """Add the synchronizer to the primary map."""
        if map_obj is not self._primary_map:
            raise ValueError("MapSynchronizer can only be added to the primary map.")

        map_obj.add_external_script(
            "https://unpkg.com/@mapbox/mapbox-gl-sync-move@0.3.1"
        )
        map_obj.add_on_load_js(self._render_js(map_obj))
        map_obj.custom_css = self._render_css()

    def _render_js(self, map_obj: Map) -> str:
        """Render the JavaScript for synchronization."""
        template = map_obj.env.get_template("sync_maps.js")
        return template.render(
            primary_map_id=self._primary_map.map_id,
            secondary_map_configs=[
                {
                    "container": f"{self._primary_map.map_id}-secondary-{i}",
                    "style": m.map_style,
                    "center": m.center,
                    "zoom": m.zoom,
                }
                for i, m in enumerate(self._secondary_maps)
            ],
        )

    def _render_css(self) -> str:
        """Render the CSS for the map layout."""
        return textwrap.dedent(
            f"""
            html, body {{
                height: 100%;
            }}
            .maplibreum-sync-wrapper {{
                display: flex;
                width: 100%;
                height: 100%;
            }}
            .maplibreum-sync-wrapper > .maplibreum-sync-map {{
                flex: 1 1 0;
                height: 100%;
            }}
            #{self._primary_map.map_id} {{
                height: 100%;
            }}
            """
        ).strip()